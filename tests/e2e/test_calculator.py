"""Calculator in the PicoDeck simulator. Moved from PicoDeck's
tests/e2e/test_idle_apps.py when the app got this repo.

Waiting for a key must not redraw and flush the screen flat out: a loop with
no wait keeps Core 0 and the panel's bus busy on a battery device."""
import time

from conftest import APP, stage


def _presents_while_idle(sim, seconds=2.0):
    start = sim.present_count()
    time.sleep(seconds)
    return sim.present_count() - start


def _lit_changed_by(sim, key):
    before = sim.screenshot_pil().convert("RGB").tobytes()
    seq = sim.keypress(key)["input_seq"]
    sim.wait_input_consumed(seq)
    time.sleep(0.3)
    return sim.screenshot_pil().convert("RGB").tobytes() != before


def test_calculator_sleeps_until_a_key(simulator):
    stage(simulator)
    simulator.launch_app(APP)
    time.sleep(0.6)
    # Once a second, for the status bar's clock and battery.
    assert _presents_while_idle(simulator) <= 4
    assert _lit_changed_by(simulator, "7")
    simulator.exit_app()
    simulator.wait_for_exit(timeout=10)
