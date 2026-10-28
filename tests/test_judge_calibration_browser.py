"""Privileged fixture parity checks, not independent judge accuracy."""

import json
import os
from pathlib import Path

import pytest

pytestmark = [
    pytest.mark.browser,
    pytest.mark.skipif(
        os.environ.get("GAMEBENCH_JUDGE_WRAPPER_TESTS") != "1",
        reason="Run scripts/test-judge-calibration.sh in isolated Chromium",
    ),
]
CASES = (
    [c for c in json.loads(Path("/plan.json").read_text())["cases"] if c["repetition"] == 1]
    if os.environ.get("GAMEBENCH_JUDGE_WRAPPER_TESTS") == "1"
    else []
)


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["id"])
def test_anonymized_fixture_preserves_known_behavior(case):
    from playwright.sync_api import sync_playwright
    from test_gameplay_calibration_browser import Player, probe_platformer, probe_racing

    directory = Path("/output") / case["id"]
    directory.mkdir()
    fixture = Path("/tasks") / case["id"] / "environment/fixture"
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": 1280, "height": 800}, record_video_dir=str(directory)
        )

        def route(request):
            url = request.request.url
            if url == "http://game.invalid/":
                request.fulfill(
                    body=(fixture / "index.html").read_bytes(), content_type="text/html"
                )
            elif url == "http://game.invalid/game.js":
                request.fulfill(
                    body=(fixture / "game.js").read_bytes(), content_type="text/javascript"
                )
            else:
                request.abort()

        context.route("**/*", route)
        page = context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto("http://game.invalid/")
        assert page.locator("a").count() == 0
        page.get_by_role("button", name="Start", exact=True).click()
        player = Player(page, directory, case["game"])
        probe = probe_platformer if case["game"] == "platformer" else probe_racing
        observed = bool(probe(player, case["criterion"]))
        player.shot("final")
        context.close()
        browser.close()
    result = {
        "kind": "privileged_wrapper_regression_not_judge_accuracy",
        "case": case,
        "observed_pass": observed,
        "page_errors": errors,
        "events": player.events,
    }
    (directory / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    assert not errors
    assert observed == (case["expected_status"] == "passed")
