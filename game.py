import os
import sys
import time as t
import random as rd
import queue
from enum import Enum

import keyboard

import cell
import snake as sn
import menu


# ---------- ANSI ----------
if os.name == 'nt':
    try:
        import ctypes
        k32 = ctypes.windll.kernel32
        k32.SetConsoleMode(k32.GetStdHandle(-11), 7)   # enable VT on Windows 10+
    except Exception:
        pass

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

CURSOR_HOME  = '\033[H'
HIDE_CURSOR  = '\033[?25l'
SHOW_CURSOR  = '\033[?25h'
CLEAR_SCREEN = '\033[2J\033[H'


# ---------- Input (event-driven, no missed presses) ----------
_key_queue = queue.Queue()
_hooked = False

def _on_key(event):
    _key_queue.put(event.name)

def _start_keyboard():
    global _hooked
    if _hooked:
        return
    try:
        keyboard.on_press(_on_key)
        _hooked = True
    except Exception:
        pass

def _drain():
    out = []
    while True:
        try:
            out.append(_key_queue.get_nowait())
        except queue.Empty:
            return out


class Direction(Enum):
    up = 0
    left = 1
    down = 2
    right = 3


HEAD_CHARS = {
    Direction.up:    '▲',
    Direction.down:  '▼',
    Direction.left:  '◀',
    Direction.right: '▶',
}

OPPOSITE = {
    Direction.up:    Direction.down,
    Direction.down:  Direction.up,
    Direction.left:  Direction.right,
    Direction.right: Direction.left,
}


class game:
    def __init__(self, m, n, v, best=0):
        self.velocity = v
        self.n = n
        self.m = m
        self.best = best
        self.board = [[None for _ in range(n)] for _ in range(m)]
        m0, n0 = 0, rd.randint(0, n - 1)
        self.free_cells = []
        self.dir = Direction.down
        for mi in range(m):
            for ni in range(n):
                self.board[mi][ni] = cell.cell(mi, ni)
                self.free_cells.append((mi, ni))
        self.free_cells.remove((m0, n0))
        self.snake = sn.snake(m0, n0, self)
        self.apples_count = 0
        self.end = False
        self.score = 0
        self.time_elapsed = 0.0
        self.paused = False
        self._abort = False
        self._pending_dir = []
        self._start = 0.0

    # ---------- public ----------

    def run(self):
        """Game loop. Returns 'win' | 'lose' | 'abort'."""
        _start_keyboard()
        _drain()                                   # drop stale events
        sys.stdout.write(CLEAR_SCREEN + HIDE_CURSOR)
        sys.stdout.flush()

        self._start = t.perf_counter()
        frame_time = 1.0 / self.velocity
        next_frame = self._start

        try:
            while len(self.free_cells) > 0:
                now = t.perf_counter()

                # Poll input at ~200 Hz between frames
                if now < next_frame:
                    self._handle_input()
                    if self._abort:
                        return 'abort'
                    t.sleep(min(next_frame - now, 0.005))
                    continue

                next_frame = now + frame_time

                self._handle_input()
                if self._abort:
                    return 'abort'

                if self.paused:
                    self.render(paused=True)
                    continue

                if self.apples_count == 0:
                    self.apple_spawn()

                self._apply_queued_dir()
                self.move()

                if self.end:
                    self.time_elapsed = t.perf_counter() - self._start
                    self.render()
                    t.sleep(0.6)
                    return 'lose'

                self.render()

            self.time_elapsed = t.perf_counter() - self._start
            self.render()
            t.sleep(0.6)
            return 'win'
        finally:
            sys.stdout.write(SHOW_CURSOR)
            sys.stdout.flush()
            self.best = max(self.best, self.score)

    # ---------- input ----------

    def _handle_input(self):
        for key in _drain():
            if key == 'esc':
                self._abort = True
                return
            if key == 'space':
                self.paused = not self.paused
            elif key in ('up', 'w'):
                self._queue_dir(Direction.up)
            elif key in ('down', 's'):
                self._queue_dir(Direction.down)
            elif key in ('left', 'a'):
                self._queue_dir(Direction.left)
            elif key in ('right', 'd'):
                self._queue_dir(Direction.right)

        # safety net if the hook missed ESC
        if not self._abort and keyboard.is_pressed('esc'):
            self._abort = True

    def _queue_dir(self, nd):
        cur = self._pending_dir[-1] if self._pending_dir else self.dir
        if nd == cur or nd == OPPOSITE[cur]:
            return
        self._pending_dir.append(nd)
        if len(self._pending_dir) > 2:              # allow at most 2 queued turns
            self._pending_dir.pop(0)

    def _apply_queued_dir(self):
        if self._pending_dir:
            self.dir = self._pending_dir.pop(0)

    # ---------- simulation ----------

    def apple_spawn(self):
        l = len(self.free_cells)
        if l == 0:
            return
        a = self.free_cells[rd.randint(0, l - 1)]
        self.board[a[0]][a[1]].type_cell = cell.Type.apple
        self.apples_count += 1

    def move(self):
        head = self.snake.body[-1]
        fi = [-1, 0, 1, 0]
        ci = [ 0,-1, 0, 1]
        nm = head[0] + fi[self.dir.value]
        nn = head[1] + ci[self.dir.value]

        # walls
        if nm >= self.m or nm < 0 or nn >= self.n or nn < 0:
            self.end = True
            return

        # self-collision (tail is allowed because it frees up this frame)
        if self.board[nm][nn].type_cell == cell.Type.snake:
            tail = self.snake.body[0]
            if (nm, nn) != tail:
                self.end = True
                return

        prev_len = len(self.snake.body)
        self.snake.step(nm, nn, self)
        if len(self.snake.body) > prev_len:
            self.score += 1
            self.best = max(self.best, self.score)

    # ---------- render ----------

    def render(self, paused=False):
        elapsed = self.time_elapsed or (t.perf_counter() - self._start)
        status_text  = "PAUSED" if paused else "PLAYING"
        status_color = YELLOW   if paused else CYAN
        status = f"{status_color}{BOLD}{status_text.ljust(7)}{RESET}"
        
        lines = []
        # HUD
        lines.append(
            f"  {CYAN}SCORE{RESET} {BOLD}{self.score:>3}{RESET}"
            f"   {CYAN}BEST{RESET} {BOLD}{self.best:>3}{RESET}"
            f"   {CYAN}SPEED{RESET} {self.velocity:>4.1f}"
            f"   {CYAN}TIME{RESET} {elapsed:>5.1f}s"
            f"   {status}"
        )
        # top border
        lines.append(f"  {GRAY}┌{'─' * (self.n * 2)}┐{RESET}")

        head_pos = self.snake.body[-1] if self.snake.body else None

        for f in range(self.m):
            row = [f"  {GRAY}│{RESET}"]
            for c in range(self.n):
                t_ = self.board[f][c].type_cell
                if t_ == cell.Type.snake:
                    if (f, c) == head_pos:
                        ch = f"{BRIGHT_GREEN}{HEAD_CHARS[self.dir]}{RESET}"
                    else:
                        ch = f"{GREEN}■{RESET}"
                elif t_ == cell.Type.apple:
                    ch = f"{RED}●{RESET}"
                else:
                    ch = f"{DARK_GRAY}·{RESET}"
                row.append(f"{ch} ")
            row.append(f"{GRAY}│{RESET}")
            lines.append("".join(row))

        lines.append(f"  {GRAY}└{'─' * (self.n * 2)}┘{RESET}")
        lines.append(f"  {DIM}ESC quit   SPACE pause{RESET}")

        # Single write → no flicker
        sys.stdout.write(CURSOR_HOME + "\n".join(lines) + "\n")
        sys.stdout.flush()


def main():
    m, n, v = 10, 10, 5.0
    best = 0
    while True:
        action = menu.main_menu()
        if action == "quit":
            menu.clear_screen(); print("Thanks for playing!"); return
        if action == "settings":
            m, n, v = menu.settings_menu(m, n, v)
            continue

        while True:
            g = game(m, n, v, best=best)
            result = g.run()
            best = g.best
            if result == "abort":
                break
            choice = menu.game_over_menu(g.score, result == "win", g.time_elapsed)
            if choice == "again":
                continue
            elif choice == "menu":
                break
            else:
                menu.clear_screen(); print("Thanks for playing!"); return


if __name__ == "__main__":
    main()