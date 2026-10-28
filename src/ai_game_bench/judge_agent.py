"""Harbor agent adapter for a local Codex screenshot-only gameplay evaluator.

Harbor owns trials, timeouts, retries and sandboxes. Codex owns the model/tool
loop. This adapter only forwards two restricted tools into Harbor's browser.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import os
import shutil
import tempfile
import time
from pathlib import Path

from harbor.agents.base import BaseAgent

VERSION = "0.1.1"
CODEX_VERSION = "codex-cli 0.165.0"
DISABLED_FEATURES = (
    "shell_tool",
    "multi_agent",
    "memories",
    "apps",
    "plugins",
    "view_image",
    "browser_use",
    "browser_use_external",
    "computer_use",
    "image_generation",
    "hooks",
    "skill_search",
    "code_mode",
    "code_mode_host",
)
RESULT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "status": {"type": "string", "enum": ["passed", "failed", "not_tested", "infra_error"]},
        "reason": {"type": "string"},
        "evidence_ids": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["status", "reason", "evidence_ids"],
}
TOOLS = [
    {
        "type": "function",
        "name": "game_observe",
        "description": "Observe the game screenshot. No source, DOM or hidden state access.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "type": "function",
        "name": "game_act",
        "description": (
            "Use ordinary mouse/keyboard actions. Screenshot coordinates are 1280x800. "
            "Hold keys for 0..3000 ms then release; wait uses no keys. Set frames=1..4 "
            "for evenly spaced screenshots during the action (plus a before frame). "
            "Use short holds to see a jump's ascent. Time keeps running between calls."
        ),
        "inputSchema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "action": {"type": "string", "enum": ["click", "hold", "wait"]},
                "x": {"type": "integer", "minimum": 0, "maximum": 1279},
                "y": {"type": "integer", "minimum": 0, "maximum": 799},
                "keys": {
                    "type": "array",
                    "uniqueItems": True,
                    "items": {
                        "type": "string",
                        "enum": [
                            "ArrowLeft",
                            "ArrowRight",
                            "ArrowUp",
                            "ArrowDown",
                            "Space",
                            "a",
                            "d",
                            "w",
                            "s",
                        ],
                    },
                },
                "duration_ms": {"type": "integer", "minimum": 0, "maximum": 3000},
                "frames": {"type": "integer", "minimum": 1, "maximum": 4},
            },
            "required": ["action"],
        },
    },
]


def codex_arguments(effort):
    config = {"features." + name: False for name in DISABLED_FEATURES}
    config.update(
        {
            "features.skip_host_skill_discovery": True,
            "web_search": "disabled",
            "project_doc_max_bytes": 0,
            "model_reasoning_effort": effort,
        }
    )
    args = ["codex", "app-server"]
    for key, value in config.items():
        args += ["-c", f"{key}={json.dumps(value)}"]
    return args


def compact_event(value):
    """Retain native events without duplicating inline images; files hold images."""
    if isinstance(value, dict):
        return {k: compact_event(v) for k, v in value.items()}
    if isinstance(value, list):
        return [compact_event(v) for v in value]
    if isinstance(value, str) and value.startswith("data:image/"):
        return {"inline_image_sha256": hashlib.sha256(value.encode()).hexdigest()}
    return value


class CodexGameplayJudge(BaseAgent):
    @staticmethod
    def name():
        return "codex-gameplay-judge"

    def version(self):
        return VERSION

    def __init__(self, *args, effort="high", allow_model_calls=False, **kwargs):
        super().__init__(*args, **kwargs)
        if allow_model_calls is not True:
            raise ValueError("Explicit allow_model_calls=true is required for calibration.")
        if not self.model_name:
            raise ValueError("Pin an evaluator model.")
        self.effort = effort
        self._proc = None

    async def _browser(self, environment, action):
        encoded = base64.b64encode(json.dumps(action).encode()).decode()
        result = await environment.exec(f"python /opt/bridge.py call {encoded}", timeout_sec=25)
        if result.return_code:
            raise RuntimeError("Browser bridge failed: " + (result.stderr or "")[-1000:])
        data = json.loads(result.stdout)
        if data.get("infrastructure_error") or data.get("page_errors"):
            raise RuntimeError(
                "Browser measurement failed: "
                + str(data.get("infrastructure_error") or data["page_errors"])
            )
        return data

    async def setup(self, environment):
        version = await asyncio.create_subprocess_exec(
            "codex", "--version", stdout=asyncio.subprocess.PIPE
        )
        stdout, _ = await version.communicate()
        if stdout.decode().strip() != CODEX_VERSION:
            raise RuntimeError(
                f"Adapter calibrated for {CODEX_VERSION}; review a new CLI version first."
            )
        await environment.exec(
            "mkdir -p /logs/agent/gameplay /workspace; "
            "nohup python /opt/bridge.py >/tmp/browser.log 2>&1 </dev/null &"
        )
        # Setup readiness does not call a model or consume a game action.
        for _ in range(30):
            check = await environment.exec("test -s /logs/agent/gameplay/events.json")
            if check.return_code == 0:
                return
            await asyncio.sleep(0.2)
        raise RuntimeError("Browser did not start")

    async def run(self, instruction, environment, context):
        started = time.monotonic()
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self._context = context
        self._final = None
        self._request_id = 0
        self._events = (self.logs_dir / "codex-events.jsonl").open("w")
        receipt = {
            "schema_version": "judge-session/0.1",
            "adapter_version": VERSION,
            "adapter_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "codex_version": CODEX_VERSION,
            "requested_model": self.model_name,
            "effort": self.effort,
            "access_mode": "screenshot_only",
            "tool_schema_sha256": hashlib.sha256(
                json.dumps(TOOLS, sort_keys=True).encode()
            ).hexdigest(),
            "instruction_sha256": hashlib.sha256(instruction.encode()).hexdigest(),
            "auth": "existing ChatGPT login",
            "cost_usd": None,
            "cost_basis": "subscription; per-session charge not available",
            "creation_context_hidden": True,
            "expected_answers_visible": False,
        }
        (self.logs_dir / "instruction.md").write_text(instruction)
        stderr = (self.logs_dir / "codex-stderr.txt").open("wb")
        try:
            # Credentials remain in a private temporary directory outside the repo,
            # are never mounted in the game, and are deleted with this context.
            with tempfile.TemporaryDirectory(prefix="agb-judge-") as temporary:
                root = Path(temporary)
                auth_home, cwd = root / "auth", root / "workspace"
                auth_home.mkdir(mode=0o700)
                cwd.mkdir(mode=0o700)
                auth = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "auth.json"
                shutil.copyfile(auth, auth_home / "auth.json")
                (auth_home / "auth.json").chmod(0o600)
                args = codex_arguments(self.effort)
                env = {
                    key: os.environ[key]
                    for key in ("PATH", "HOME", "USER", "TMPDIR", "LANG")
                    if key in os.environ
                }
                env["CODEX_HOME"] = str(auth_home)
                self._proc = await asyncio.create_subprocess_exec(
                    *args,
                    cwd=cwd,
                    env=env,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=stderr,
                    limit=16 * 1024 * 1024,
                )
                await self._rpc(
                    "initialize",
                    {
                        "clientInfo": {"name": "agb_judge", "version": VERSION},
                        "capabilities": {"experimentalApi": True},
                    },
                )
                await self._send({"method": "initialized", "params": {}})
                thread = await self._rpc(
                    "thread/start",
                    {
                        "model": self.model_name,
                        "allowProviderModelFallback": False,
                        "cwd": str(cwd),
                        "ephemeral": True,
                        "sandbox": "read-only",
                        "approvalPolicy": "never",
                        "dynamicTools": TOOLS,
                        "baseInstructions": (
                            "You are a browser game evaluator. Use only game_observe and game_act. "
                            "Return the requested JSON verdict."
                        ),
                        "developerInstructions": (
                            "No coding, file access, other tools, source inspection, delegation "
                            "or web search. Evaluate only the supplied game behavior from actual "
                            "screenshots/actions."
                        ),
                        "selectedCapabilityRoots": [],
                    },
                )
                receipt["resolved_model"] = thread.get("model")
                receipt["thread_id"] = thread["thread"]["id"]
                context.metadata = dict(receipt)
                await self._rpc(
                    "turn/start",
                    {
                        "threadId": receipt["thread_id"],
                        "effort": self.effort,
                        "input": [{"type": "text", "text": instruction}],
                        "outputSchema": RESULT_SCHEMA,
                    },
                )
                while True:
                    event = await self._read()
                    method = event.get("method")
                    params = event.get("params", {})
                    if method == "item/tool/call":
                        tool = params.get("tool")
                        data = params.get("arguments", {})
                        if isinstance(data, str):
                            data = json.loads(data)
                        if tool not in {"game_observe", "game_act"}:
                            raise RuntimeError("Unexpected evaluator tool")
                        result = await self._browser(
                            environment, {"action": "observe"} if tool == "game_observe" else data
                        )
                        contents = []
                        for frame in result.pop("images", []):
                            contents += [
                                {"type": "inputText", "text": "Observation " + frame["id"]},
                                {
                                    "type": "inputImage",
                                    "imageUrl": "data:image/png;base64," + frame["image"],
                                },
                            ]
                        contents.append({"type": "inputText", "text": json.dumps(result)})
                        await self._send(
                            {
                                "id": event["id"],
                                "result": {
                                    "contentItems": contents,
                                    "success": "action_error" not in result,
                                },
                            }
                        )
                    elif "id" in event and "method" in event:
                        raise RuntimeError("Unexpected server request: " + method)
                    elif method == "turn/completed":
                        turn = params["turn"]
                        if turn.get("status") != "completed":
                            raise RuntimeError("Codex turn failed: " + str(turn.get("error")))
                        break
                if self._final is None:
                    raise RuntimeError("Evaluator returned no verdict")
                result = json.loads(self._final)
                (self.logs_dir / "judgement.json").write_text(json.dumps(result, indent=2) + "\n")
                await environment.upload_file(
                    self.logs_dir / "judgement.json", "/workspace/judgement.json"
                )
        finally:
            if self._proc and self._proc.returncode is None:
                self._proc.terminate()
                try:
                    await asyncio.wait_for(self._proc.wait(), 5)
                except TimeoutError:
                    self._proc.kill()
                    await self._proc.wait()
            try:
                await self._browser(environment, {"action": "close"})
            except Exception as exc:
                receipt["capture_close_error"] = str(exc)
            receipt["elapsed_seconds"] = round(time.monotonic() - started, 3)
            receipt["usage"] = {
                "input_including_cache": context.n_input_tokens,
                "cached_input": context.n_cache_tokens,
                "output": context.n_output_tokens,
            }
            context.metadata = receipt
            (self.logs_dir / "session.json").write_text(json.dumps(receipt, indent=2) + "\n")
            stderr.close()
            self._events.close()

    async def _send(self, data):
        self._events.write(json.dumps({"direction": "send", **compact_event(data)}) + "\n")
        self._events.flush()
        self._proc.stdin.write((json.dumps(data) + "\n").encode())
        await self._proc.stdin.drain()

    async def _read(self):
        line = await self._proc.stdout.readline()
        if not line:
            raise RuntimeError("Codex app-server closed unexpectedly")
        event = json.loads(line)
        self._events.write(json.dumps({"direction": "receive", **compact_event(event)}) + "\n")
        self._events.flush()
        method = event.get("method")
        params = event.get("params", {})
        if method in {"item/started", "item/completed"}:
            item = params.get("item", {})
            if method == "item/completed" and item.get("type") == "agentMessage":
                self._final = item.get("text")
            if item.get("type") not in {
                "userMessage",
                "reasoning",
                "agentMessage",
                "dynamicToolCall",
                "contextCompaction",
            }:
                raise RuntimeError(
                    "Evaluator attempted a disallowed tool; exclude this measurement"
                )
        if method == "thread/tokenUsage/updated":
            usage = params.get("tokenUsage", {}).get("total", {})
            self._context.n_input_tokens = usage.get("inputTokens")
            self._context.n_cache_tokens = usage.get("cachedInputTokens")
            self._context.n_output_tokens = usage.get("outputTokens")
        return event

    async def _rpc(self, method, params):
        self._request_id += 1
        ident = self._request_id
        await self._send({"id": ident, "method": method, "params": params})
        while True:
            response = await self._read()
            if response.get("id") == ident and "method" not in response:
                if "error" in response:
                    raise RuntimeError(f"Codex {method}: {response['error']}")
                return response["result"]


class CaptureSmokeJudge(CodexGameplayJudge):
    """Free transport/recording check; deliberately abstains, never calls Codex."""

    @staticmethod
    def name():
        return "capture-smoke-no-model"

    def __init__(self, *args, **kwargs):
        kwargs["allow_model_calls"] = True
        kwargs["model_name"] = "no-model"
        super().__init__(*args, **kwargs)

    async def run(self, instruction, environment, context):
        context.metadata = {"model_calls": 0, "kind": "transport_smoke_not_judge_calibration"}
        try:
            before = await self._browser(environment, {"action": "observe"})
            await self._browser(environment, {"action": "click", "x": 150, "y": 174})
            after = await self._browser(
                environment,
                {"action": "hold", "keys": ["ArrowRight"], "duration_ms": 200, "frames": 2},
            )
            result = {
                "status": "not_tested",
                "reason": "Free capture smoke only; no semantic game judgement.",
                "evidence_ids": [before["images"][0]["id"], after["images"][-1]["id"]],
            }
            self.logs_dir.mkdir(parents=True, exist_ok=True)
            path = self.logs_dir / "judgement.json"
            path.write_text(json.dumps(result) + "\n")
            await environment.upload_file(path, "/workspace/judgement.json")
        finally:
            await self._browser(environment, {"action": "close"})
