#!/usr/bin/env bash
set -euo pipefail
repo_dir="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo_dir"
mkdir -p artifacts/judge-wrapper-parity
output_dir="$(mktemp -d "$repo_dir/artifacts/judge-wrapper-parity/run.XXXXXX")"
uv run --locked agb calibration prepare "$output_dir/plan" --model no-model --effort high
mkdir -p "$output_dir/evidence"
image_tag="ai-game-bench-browser:playwright-1.62.0"
docker build -t "$image_tag" datasets/smoke-create-v0.2/create-click-counter-zh-001/environment
# Privileged, deterministic checks of derived public fixtures. No Codex/model,
# credentials, host browser, external network or creator platform is used.
docker run --rm --network none --read-only --shm-size=256m \
  --tmpfs /tmp:rw,exec,nosuid,size=512m \
  --mount "type=bind,source=$output_dir/plan/tasks,target=/tasks,readonly" \
  --mount "type=bind,source=$output_dir/plan/plan.json,target=/plan.json,readonly" \
  --mount "type=bind,source=$repo_dir/tests,target=/checks,readonly" \
  --mount "type=bind,source=$output_dir/evidence,target=/output" \
  --env GAMEBENCH_JUDGE_WRAPPER_TESTS=1 \
  "$image_tag" python -m pytest /checks/test_judge_calibration_browser.py \
  -q -p no:cacheprovider -o 'markers=browser: real Chromium calibration'
printf 'Free wrapper parity evidence: %s\n' "$output_dir/evidence"
