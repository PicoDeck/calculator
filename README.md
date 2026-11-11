# Calculator

A scientific calculator for [PicoDeck](https://picodeck.net) on the
ClockworkPi PicoCalc. It has six tabs: Basic, Sci, Graph, Solve, Stat and
Base. It evaluates whole expressions, and has complex numbers, an equation
solver, statistics, number bases, function graphs and a history.

## Controls

It reads `picocalc.gamepad` for moving and pressing, so a Bluetooth
controller and the bindings in Settings → Controls work in it; typing stays
on the keyboard. The keys below are the default bindings.

| Key | Gamepad button | Action |
|---|---|---|
| Arrows | D-pad | Move over the button grid (repeats while held) |
| Enter or F4 | A | Press the highlighted button |
| Typing | | Enter an expression directly; `=` evaluates it |
| Backspace, Del | | Delete the last character, clear the expression |
| F1 | | Angle mode: DEG, RAD, GRAD |
| F2 | | The second function layer (Sci tab) |
| F3 | | History: D-pad Up/Down to choose, A to recall |
| Shift+F2, Shift+F3 | L, R | Previous and next tab |
| Esc or F5 | B | Close the history or the full-screen graph, else save the history and quit |

L and R's default keys are F2 and F3, which keep their own meaning here, so on
the PicoCalc's keyboard step the tabs with Shift+F2 and Shift+F3, or bind other
keys to L and R in Settings → Controls.

In the full-screen graph (View on the Graph tab) the D-pad pans and A traces
(in the trace Left/Right move, Up/Down switch the function, A goes back);
`+`/`-` zoom, R resets, I edits, T shows a table (Up/Down scroll, Left/Right
change the step, A goes back). B returns to the grid. Its hints name the keys
you have bound.

Changed for keyboard users: F4 and F5 no longer switch tabs. F4 presses the
highlighted button, like Enter, and F5 saves and quits, like Esc.

## Install

From the **App Store** on the device (firmware 0.7.0 or later), or copy the
files listed in `files.txt` to `/apps/calculator/` on the SD card.

## Development

- `make test` runs the unit tests (`tests/`, luaunit) under your `lua` (5.4).
- `make e2e` runs the simulator tests in PicoDeck's simulator. It needs a
  PicoDeck checkout with the simulator built (`make simulator` there), at
  `~/Projects/PicoDeck/picodeck` or `$PICODECK_ROOT`.
- `make zip` builds the release zip from `files.txt`, as CI does. A tag
  `v<version>` matching `app.json`'s version publishes it as a release, which
  the PicoDeck store lists.

`TODO.md` lists the features still missing. The app was part of the
[PicoDeck repository](https://github.com/PicoDeck/picodeck) until version
0.1.1; its history came with it.
