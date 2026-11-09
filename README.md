# Calculator

A scientific calculator for [PicoDeck](https://picodeck.net) on the
ClockworkPi PicoCalc. It has six tabs: Basic, Sci, Graph, Solve, Stat and
Base. It evaluates whole expressions, and has complex numbers, an equation
solver, statistics, number bases, function graphs and a history.

## Keys

| Key | Action |
|---|---|
| Arrows, Enter | Move over the button grid and press a button |
| Typing | Enter an expression directly |
| F1 | Angle mode: DEG, RAD, GRAD |
| F2 | The second function layer (Sci tab) |
| F3 | History: Up and Down to choose, Enter to recall |
| F4, F5 (or Shift+Left/Right) | Previous and next tab |
| Esc | Close the history or the full-screen graph, else quit |

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
