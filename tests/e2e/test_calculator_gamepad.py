"""Calculator read from the gamepad, in the PicoDeck simulator.

The pad tests drive it from the simulator's test gamepad (sim.pad), the path
a Bluetooth controller takes: it reaches picocalc.gamepad only, never
picocalc.input. A spy put before main.lua logs each frame that differs from
the one before as CALC|tab=..|expr=..|res=..|info=..|hint=..: the active tab's
name (y 22, drawn in cyan), the expression (y 40), the result (y 60), and the
graph view's two status lines (y 282 and 294). Saving and exiting writes the
history to /data/<id>/history.json.
"""
import re
import time
from pathlib import Path

from conftest import APP, APP_ID, stage

_SPY = r"""
local disp, sys = picocalc.display, picocalc.sys
local dt, fl, cyan = disp.drawText, disp.flush, disp.CYAN
local KEYS = {[40] = 'expr', [60] = 'res', [282] = 'info', [294] = 'hint'}
local f, last = {}, nil
disp.drawText = function(x, y, t, fg, ...)
  if y == 22 then
    if fg == cyan then f.tab = t end
  elseif KEYS[y] then f[KEYS[y]] = t end
  return dt(x, y, t, fg, ...)
end
disp.flush = function(...)
  local line = string.format('CALC|tab=%s|expr=%s|res=%s|info=%s|hint=%s', f.tab or '',
    f.expr or '', f.res or '', f.info or '', f.hint or '')
  if line ~= last then last = line; sys.log(line) end
  f = {}
  return fl(...)
end
"""


def _mark(sim):
    """The seq the next log entry gets."""
    return sim.get_log_buffer(tail=1).get("next_seq", 0)


def _see(sim, since, timeout=5.0, **want):
    """Wait for a spy frame, logged at `since` or later, whose fields include
    `want` (exact values); return its text."""
    looks = "".join(rf"(?=.*\|{k}={re.escape(v)}(\||$))" for k, v in want.items())
    return sim.wait_for_log(r"^CALC" + looks, timeout=timeout, since_seq=since)


def _launch(sim, rebind=None):
    """Stage with the spy, connect the test pad (nothing held), launch, and
    wait for the first frame: Basic, empty expression."""
    stage(sim, rebind=rebind, prepend=_SPY)
    sim.pad("none")
    seq = _mark(sim)
    sim.launch_app(APP)
    _see(sim, seq, timeout=10, tab="Basic", expr="0")
    return seq


def _press(sim, button):
    """One test-pad press, then a moment for its release."""
    sim.pad(button, 100)
    time.sleep(0.25)


def _tap(sim, key):
    """One keyboard key (or a typed character), read by the OS."""
    r = sim.keypress(key)
    sim.wait_input_consumed(r["input_seq"], timeout=5.0)
    time.sleep(0.25)


def _history(sim):
    path = Path(sim.sd_card_path) / "data" / APP_ID / "history.json"
    return path.read_text() if path.exists() else ""


def _exited(sim):
    assert sim.wait_for_exit(timeout=10)["result"] == "returned"


def _tabs(sim, since):
    return {m.group(1) for e in sim.get_log_lines(since)
            if (m := re.match(r"^CALC\|tab=([^|]*)\|", e["text"]))}


def test_calculator_tabs_grid_and_exit_on_the_pad(simulator):
    sim = simulator
    seq = _launch(sim)
    _press(sim, "r")                    # Basic -> Sci
    _see(sim, seq, tab="Sci")
    _press(sim, "down")
    _press(sim, "down")                 # Sci row 3, col 1: "7"
    _press(sim, "a")
    _see(sim, seq, tab="Sci", expr="7")
    _press(sim, "l")                    # back to Basic (row 3, col 1 there is "4")
    _see(sim, seq, tab="Basic", expr="7")
    _press(sim, "down")
    _press(sim, "down")                 # row 5, col 1: "+/-"
    _press(sim, "left")                 # wraps to row 5, col 6: "="
    _press(sim, "a")
    _see(sim, seq, expr="7", res="= 7")
    _press(sim, "b")                    # saves the history and exits
    _exited(sim)
    assert '"expr":"7"' in _history(sim), _history(sim)


def test_calculator_f2_f3_keys_do_not_step_tabs(simulator):
    """F3 (history) and F2 (2nd layer) are also L and R's default keys: they
    must do their own command only, and never step a tab."""
    sim = simulator
    seq = _launch(sim)
    _tap(sim, "f3")                     # history overlay opens
    _press(sim, "b")                    # B closes it
    _tap(sim, "f2")                     # 2nd layer on
    _tap(sim, "f2")                     # and off
    _press(sim, "down")                 # Basic row 2, col 1: "7"
    _press(sim, "a")
    _see(sim, seq, tab="Basic", expr="7")
    assert _tabs(sim, seq) == {"Basic"}, _tabs(sim, seq)
    _press(sim, "b")
    _exited(sim)


def test_calculator_history_on_the_pad(simulator):
    sim = simulator
    seq = _launch(sim)
    _tap(sim, "7")
    _tap(sim, "=")                      # typed: evaluates
    _see(sim, seq, expr="7", res="= 7")
    _tap(sim, "del")                    # the keyboard's Del clears the expression
    seq = _mark(sim)
    _tap(sim, "f3")                     # history overlay
    _press(sim, "a")                    # A recalls the entry and closes it
    _see(sim, seq, expr="7")
    seq = _mark(sim)
    _press(sim, "a")                    # the grid again: row 1, col 1 is "("
    _see(sim, seq, expr="7(")
    _tap(sim, "f3")
    _press(sim, "b")                    # B closes the overlay...
    seq = _mark(sim)
    _press(sim, "a")                    # ...so A presses "(" again
    _see(sim, seq, expr="7((")
    _press(sim, "b")
    _exited(sim)


def test_calculator_f4_presses_the_key_and_f5_quits(simulator):
    """With the default bindings F4 is A and F5 is B: they no longer step
    the tabs."""
    sim = simulator
    seq = _launch(sim)
    _tap(sim, "down")                   # the keyboard's arrows: row 2, "7"
    _tap(sim, "f4")
    _see(sim, seq, tab="Basic", expr="7")
    _tap(sim, "enter")                  # Enter presses it too
    _see(sim, seq, tab="Basic", expr="77")
    assert _tabs(sim, seq) == {"Basic"}, _tabs(sim, seq)
    sim.keypress("f5")
    _exited(sim)


def test_calculator_graph_view_on_the_pad(simulator):
    """With A bound to Z, the graph view's hints name Z."""
    sim = simulator
    seq = _launch(sim, rebind={"a": ["Z"]})
    _press(sim, "r")
    _press(sim, "r")                    # Basic -> Sci -> Graph
    _see(sim, seq, tab="Graph")
    _press(sim, "left")                 # row 1 wraps to col 6: "View"
    seq = _mark(sim)
    _press(sim, "a")
    _see(sim, seq, tab="Graph", info="x:[-10,10] y:[-10,10]",
         hint="Arrows:pan +/-:zoom R:reset I:input T:table Z:trace")
    seq = _mark(sim)
    _press(sim, "right")                # pans
    _see(sim, seq, info="x:[-8,12] y:[-10,10]")
    seq = _mark(sim)
    _press(sim, "a")                    # trace
    _see(sim, seq, hint="Left/Right:move Up/Down:func Z/Esc:back")
    seq = _mark(sim)
    _press(sim, "b")                    # back to the input grid
    _see(sim, seq, tab="Graph", info="", hint="")
    _press(sim, "b")                    # saves and exits
    _exited(sim)


def test_calculator_typed_letter_does_not_also_press_its_pad_button(simulator):
    """A letter typed on the keyboard is only text, even when a pad button is
    bound to that key: with Right on D, typing hex "d" in Base must not also
    move the cursor."""
    sim = simulator
    seq = _launch(sim, rebind={"right": ["D"]})
    _press(sim, "l")                    # Basic -> Base (wraps)
    _see(sim, seq, tab="Base")
    _tap(sim, "d")                      # hex D
    _see(sim, seq, tab="Base", expr="D")
    _press(sim, "down")
    _press(sim, "down")                 # row 3: col 1 is "7", col 2 is "8"
    seq = _mark(sim)
    _press(sim, "a")
    _see(sim, seq, tab="Base", expr="D7")
    _press(sim, "b")
    _exited(sim)


def test_calculator_esc_closes_then_quits(simulator):
    """Esc is B's key too: it closes the history overlay, leaves the
    full-screen graph, and on the grid saves the history and quits."""
    sim = simulator
    seq = _launch(sim)
    _tap(sim, "7")
    _tap(sim, "=")
    _see(sim, seq, expr="7", res="= 7")
    _tap(sim, "f3")
    _tap(sim, "esc")                    # closes the overlay, does not quit
    seq = _mark(sim)
    _press(sim, "a")                    # the grid answers: "(" at row 1, col 1
    _see(sim, seq, expr="7(")
    _press(sim, "r")
    _press(sim, "r")                    # Graph
    _press(sim, "left")                 # row 1 wraps to col 6: "View"
    seq = _mark(sim)
    _press(sim, "a")
    _see(sim, seq, tab="Graph", info="x:[-10,10] y:[-10,10]")
    seq = _mark(sim)
    _tap(sim, "esc")                    # back to the input grid
    _see(sim, seq, tab="Graph", info="", hint="")
    _tap(sim, "esc")                    # saves and quits
    _exited(sim)
    assert '"expr":"7"' in _history(sim), _history(sim)


def test_calculator_shift_f2_f3_step_the_tabs(simulator):
    """Shift+F3 and Shift+F2 reach the app as F8 and F7; the gamepad reads
    them as R and L."""
    sim = simulator
    seq = _launch(sim)
    _tap(sim, "f8")
    _see(sim, seq, tab="Sci")
    seq = _mark(sim)
    _tap(sim, "f7")
    _see(sim, seq, tab="Basic")
    _press(sim, "b")
    _exited(sim)
