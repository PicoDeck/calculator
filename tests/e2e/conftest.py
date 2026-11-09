"""The app in the PicoDeck simulator.

Uses PicoDeck's E2E harness from $PICODECK_ROOT (default
~/Projects/PicoDeck/picodeck): its card builder and simulator driver. The
simulator binary is $PICODECK_SIM_BINARY, else that checkout's
build_sim/picodeck_simulator (`make simulator` there). The app is staged from
this repo's files.txt, the files the release zip ships."""
import json
import os
import shutil
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
PICODECK = Path(os.environ.get("PICODECK_ROOT", Path.home() / "Projects" / "PicoDeck" / "picodeck"))
sys.path.insert(0, str(PICODECK / "tests" / "e2e"))

from helpers import build_sd_card, stop_and_check  # noqa: E402
from picodeck_simulator import PicodeckSimulator  # noqa: E402

MANIFEST = json.loads((REPO / "app.json").read_text())
APP_ID = MANIFEST["id"]
APP = MANIFEST.get("dirname", APP_ID.rsplit(".", 1)[-1])
SHIPPED = [l.strip() for l in (REPO / "files.txt").read_text().splitlines() if l.strip()]


def stage(sim, rebind=None, no_gamepad=False, prepend=""):
    """Copy the shipped files to the running simulator's /apps/<APP>.

    rebind writes /data/<id>/gamepad.json; no_gamepad puts
    `picocalc.gamepad = nil` before main.lua, as on firmware before API
    version 9; prepend is Lua put before main.lua (spies, a fixed RNG)."""
    sd = Path(sim.sd_card_path)
    dest = sd / "apps" / APP
    for rel in SHIPPED:
        (dest / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(REPO / rel, dest / rel)
    main = dest / "main.lua"
    head = ("picocalc.gamepad = nil\n" if no_gamepad else "") + prepend
    if head:
        main.write_text(head + main.read_text())
    if rebind:
        path = sd / "data" / APP_ID / "gamepad.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(rebind))
    return dest


@pytest.fixture
def simulator(tmp_path):
    """A test-mode simulator on a fresh card (PicoDeck's hello and system/lib
    only); the test stages the app with stage()."""
    sd = build_sd_card(tmp_path / "sd_card", fixtures=[])
    binary = os.environ.get("PICODECK_SIM_BINARY") or str(PICODECK / "build_sim" / "picodeck_simulator")
    sim = PicodeckSimulator(binary_path=binary, sd_card_path=str(sd), test_mode=True,
                            crash_log_path=str(tmp_path / "crash.log"))
    sim.start()
    yield sim
    stop_and_check(sim)
