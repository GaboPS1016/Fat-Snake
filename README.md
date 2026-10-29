# Fat Snake Game 🐍

A modern, flicker-free **Snake** game for the terminal, written in pure Python.
No Pygame, no curses — just ANSI escape codes, event-driven input, and a
frame-accurate game loop.

```
  SCORE   7   BEST  12   SPEED  5.0   TIME  14.2s   PLAYING
  ┌────────────────────┐
  │· · · · · · · ■ ■ · │
  │· · · · · · · ■ · · │
  │· · · · ● · · ▼ · · │
  │· · · · · · · · · · │
  │· · · · · · · · · · │
  │· · · · · · · · · · │
  └────────────────────┘
  ESC quit   SPACE pause
```

---

## Features

- **Flicker-free rendering** — repaints in place with `\033[H` instead of
  clearing the screen every frame.
- **Instant, event-driven input** — uses `keyboard.on_press` hooks instead of
  polling, so fast turns are never dropped.
- **Direction buffer** — queues up to two turns ahead, so tight corners feel
  smooth.
- **Frame-accurate timing** — `perf_counter()` keeps speed constant regardless
  of board size.
- **Pause / resume** — `SPACE` toggles pause without freezing the render loop.
- **Configurable board and speed** — via the in-game settings menu.
- **Best score** — tracked across rounds for the current session.
- **Self-collision detection** — classic snake rules, with the tail cell freed
  on the same frame.
- **ANSI colors + box-drawing borders** — works on Linux, macOS, and
  Windows 10+ (VT enabled automatically).
- **Clean menu flow** — Main Menu → Play / Settings / Quit, plus a
  Game Over screen with *Play Again*, *Main Menu*, and *Quit*.

---

## Requirements

- **Python 3.8+**
- [`keyboard`](https://pypi.org/project/keyboard/) — install with:

  ```bash
  pip install keyboard
  ```

- **Terminal with ANSI support**
  - Linux / macOS: any modern terminal ✅
  - Windows 10+: Windows Terminal, PowerShell, or CMD ✅
  - Windows: needs VT mode enabled (done automatically by `game.py`)

> On Linux, `keyboard` may require `sudo` or membership in the `input` group to
> capture global key events.

---

## Installation

```bash
git clone https://github.com/<your-user>/fat-snake-game.git
cd fat-snake-game
pip install keyboard
```

---

## Running

```bash
python game.py
```

You'll see the **Main Menu**:

```
==============================================
              FAT SNAKE GAME
==============================================

  1. Play
  2. Settings
  3. Quit

> Choose an option [1-3]:
```

---

## Controls

| Key | Action |
|---|---|
| `↑` / `W` | Move up |
| `↓` / `S` | Move down |
| `←` / `A` | Move left |
| `→` / `D` | Move right |
| `SPACE` | Pause / resume |
| `ESC` | Abort current game → Main Menu |

---

## Settings

From the **Settings** menu you can change:

- **Rows** — board height (minimum 3)
- **Columns** — board width (minimum 3)
- **Velocity** — frames per second (range `0.5` – `20.0`)

Press **Enter** to keep the current value.

Higher velocity = faster game. A value of `5.0` is a relaxed pace; `15.0`+ is
frenetic.

---

## Project structure

```
.
├── game.py     # Game loop, rendering, input handling, main()
├── snake.py    # Snake entity (body, step logic)
├── cell.py     # Board cell + Type enum (empty / snake / apple)
├── menu.py     # Main menu, settings menu, game-over menu
└── README.md
```

### `cell.py`

A minimal `cell` object with `m`, `n`, and `type_cell`, plus a `Type` enum:

```python
class Type(Enum):
    empty = 0
    snake = 1
    apple = 2
```

### `snake.py`

The `snake` class tracks `body` (list of `(m, n)` tuples) and `lenght`.
`step(newm, newn, game)`:

1. Detects apple consumption.
2. Marks the new head as `snake`.
3. If no apple was eaten, pops the tail and marks it `empty`.
4. If an apple was eaten, increments length and decrements `game.apples_count`.

### `game.py`

Owns the board, the snake, and the loop. Highlights:

- **`run()`** — returns `"win"`, `"lose"`, or `"abort"`.
- **`_handle_input()`** — drains the event queue and applies direction changes.
- **`_queue_dir()` / `_apply_queued_dir()`** — two-slot direction buffer.
- **`render()`** — builds the entire frame as a single string, then writes once.

### `menu.py`

Stateless menu helpers:

- `main_menu()` → `"play"` / `"settings"` / `"quit"`
- `settings_menu(m, n, v)` → `(m, n, v)`
- `game_over_menu(score, won, elapsed)` → `"again"` / `"menu"` / `"quit"`

---

## How rendering stays flicker-free

Naive terminal games do this on every frame:

```python
os.system('clear')   # wipe
print_board()        # redraw
```

That produces visible flicker. This project instead:

1. **Hides the cursor** at game start (`\033[?25l`).
2. **Moves to the top-left** of the screen (`\033[H`) each frame.
3. **Overwrites** the previous frame with the new one.
4. **Writes the whole frame in one `sys.stdout.write`** (no per-cell prints).

Because every line has a deterministic width (fixed-width HUD fields, fixed
border length), nothing is left behind. As a safety net, each line is
terminated with `\033[K` (erase-to-end-of-line).

---

## Customization

### Change the snake body character

In `render()`, look for:

```python
ch = f"{GREEN}■{RESET}"   # body cell
```

Swap `■` for any of these (all render as squares in monospaced fonts):

| Glyph | Code point | Notes |
|---|---|---|
| `■` | U+25A0 | Small square (safe default) |
| `◼` | U+25FC | Medium square |
| `▮` | U+25AE | Vertical rectangle (taller) |
| `██` | U+2588 ×2 | Solid, fills the whole cell horizontally |

If you switch to `██` (two columns wide), also change the other branches to
two-character strings and remove the extra space from `row.append`.

### Change the color palette

All colors are defined at the top of `game.py`:

```python
RESET        = '\033[0m'
BOLD         = '\033[1m'
DIM          = '\033[2m'
RED          = '\033[91m'
GREEN        = '\033[92m'
BRIGHT_GREEN = '\033[38;5;46m'
YELLOW       = '\033[93m'
CYAN         = '\033[96m'
GRAY         = '\033[90m'
DARK_GRAY    = '\033[38;5;238m'
```

Any 256-color code (`\033[38;5;NNNm` for foreground, `\033[48;5;NNNm` for
background) works on Windows Terminal, iTerm2, and modern Linux terminals.

### Change the default board size and speed

In `main()`:

```python
m, n, v = 10, 10, 5.0
```

Adjust `MIN_VELOCITY` / `MAX_VELOCITY` in `menu.py` if you want a different
range in the settings screen.

---

## Known limitations

- **Windows 10 or newer** is required for ANSI colors. On Windows 7/8 the
  output will be raw escape codes.
- **`keyboard` permissions** — on Linux you may need to run with `sudo` or add
  your user to the `input` group:

  ```bash
  sudo usermod -aG input $USER   # log out and back in afterward
  ```

- **No save file** — best score is per-session only.

---

## Possible extensions

- Persistent best score via a `highscore.json` file.
- Golden apples worth 3 points (spawn with low probability).
- Wall-wrap mode (toggle in settings).
- Optional Pygame renderer for graphical mode.

---

## License

MIT — do whatever you want with it.

---

## Credits

Built as a learning project for terminal rendering, event-driven input, and
small-scale game architecture in pure Python.
