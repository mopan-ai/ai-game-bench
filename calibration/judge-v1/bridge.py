"""Restricted screenshot/ordinary-input bridge, inside a Harbor sandbox only."""

import base64
import hashlib
import http.server
import json
import sys
import time
import urllib.request
from pathlib import Path

PORT = 9041
OUT = Path("/logs/agent/gameplay")
KEYS = {"ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "Space", "a", "d", "w", "s"}


def validate_action(data):
    if not isinstance(data, dict) or set(data) - {
        "action",
        "x",
        "y",
        "keys",
        "duration_ms",
        "frames",
    }:
        raise ValueError("Unknown action fields")
    if data.get("action") not in {"observe", "click", "hold", "wait"}:
        raise ValueError("Unsupported action")
    duration = data.get("duration_ms", 0)
    frames = data.get("frames", 1)
    if type(duration) is not int or not 0 <= duration <= 3000:
        raise ValueError("duration_ms must be an integer in 0..3000")
    if type(frames) is not int or not 1 <= frames <= 4:
        raise ValueError("frames must be an integer in 1..4")
    keys = data.get("keys", [])
    if (
        not isinstance(keys, list)
        or any(k not in KEYS for k in keys)
        or len(set(keys)) != len(keys)
    ):
        raise ValueError("Unsupported keys")
    if data["action"] == "click":
        for name, limit in [("x", 1280), ("y", 800)]:
            if type(data.get(name)) is not int or not 0 <= data[name] < limit:
                raise ValueError("Click must be within the scored viewport")
    return data


def serve():
    from playwright.sync_api import sync_playwright

    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(
            viewport={"width": 1280, "height": 800},
            record_video_dir=str(OUT),
            record_video_size={"width": 1280, "height": 800},
        )
        # Only these two frozen files may load. No file URLs, remote requests,
        # alternate fixtures, query parameters, or navigation supplied by agents.
        origin = "http://game.invalid/"

        def route(req):
            files = {
                origin: ("index.html", "text/html"),
                origin + "game.js": ("game.js", "application/javascript"),
            }
            if req.request.url not in files:
                req.abort()
                return
            name, mime = files[req.request.url]
            req.fulfill(body=(Path("/fixture") / name).read_bytes(), content_type=mime)

        ctx.route("**/*", route)
        page = ctx.new_page()
        errors, events = [], []
        page.on("pageerror", lambda err: errors.append(str(err)))
        page.goto(origin)
        started = time.monotonic()
        count, starts, frames_count = 0, 0, 0

        def save():
            (OUT / "events.json").write_text(
                json.dumps(
                    {
                        "schema_version": "judge-actions/0.1",
                        "browser": browser.version,
                        "access_mode": "screenshot_only",
                        "clock": "realtime",
                        "viewport": [1280, 800],
                        "page_errors": errors,
                        "events": events,
                    },
                    indent=2,
                )
                + "\n"
            )

        def shot():
            nonlocal frames_count
            frames_count += 1
            ident = f"frame-{frames_count:04d}"
            content = page.screenshot()
            (OUT / (ident + ".png")).write_bytes(content)
            events.append(
                {
                    "id": ident,
                    "kind": "observation",
                    "at_seconds": round(time.monotonic() - started, 3),
                    "file": ident + ".png",
                    "sha256": hashlib.sha256(content).hexdigest(),
                }
            )
            save()
            return {"id": ident, "image": base64.b64encode(content).decode()}

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass

            def do_POST(self):
                nonlocal count, starts
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                    if not 0 < length <= 4096:
                        raise ValueError("Invalid request size")
                    data = json.loads(self.rfile.read(length))
                    if data == {"action": "close"}:
                        save()
                        ctx.close()
                        result = {"closed": True}
                    else:
                        validate_action(data)
                        count += 1
                        if count > 60 or time.monotonic() - started > 300:
                            raise ValueError("Calibration action/time budget exhausted")
                        action = data["action"]
                        # Detect ordinary Start/Restart clicks for the session budget.
                        if action == "click":
                            for name in ("Start", "Restart"):
                                button = page.get_by_role("button", name=name, exact=True)
                                rect = button.bounding_box()
                                if (
                                    rect
                                    and rect["x"] <= data["x"] <= rect["x"] + rect["width"]
                                    and rect["y"] <= data["y"] <= rect["y"] + rect["height"]
                                    and button.is_enabled()
                                ):
                                    starts += 1
                                    if starts > 6:
                                        raise ValueError("Six-session limit reached")
                        images = [shot()]
                        events.append(
                            {
                                "id": f"action-{count:04d}",
                                "kind": "action",
                                "at_seconds": round(time.monotonic() - started, 3),
                                **data,
                            }
                        )
                        keys = data.get("keys", []) if action == "hold" else []
                        try:
                            if action == "click":
                                page.mouse.click(data["x"], data["y"])
                            for key in keys:
                                page.keyboard.down(key)
                            duration = data.get("duration_ms", 0)
                            frames = data.get("frames", 1)
                            for _ in range(frames):
                                if duration:
                                    page.wait_for_timeout(duration / frames)
                                images.append(shot())
                        finally:
                            for key in reversed(keys):
                                page.keyboard.up(key)
                        result = {
                            "images": images,
                            "page_errors": errors,
                            "elapsed_seconds": round(time.monotonic() - started, 3),
                            "actions_remaining": 60 - count,
                            "sessions_used": starts,
                        }
                    save()
                except ValueError as exc:
                    result = {"action_error": str(exc)}
                except Exception as exc:
                    result = {"infrastructure_error": type(exc).__name__ + ": " + str(exc)}
                content = json.dumps(result).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)

        save()
        http.server.HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "call":
        data = base64.b64decode(sys.argv[2], validate=True)
        request = urllib.request.Request(
            f"http://127.0.0.1:{PORT}", data=data, headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(request, timeout=20) as response:
            print(response.read().decode())
    else:
        serve()
