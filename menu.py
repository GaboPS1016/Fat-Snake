import os

MIN_DIM       = 3
MIN_VELOCITY  = 0.5
MAX_VELOCITY  = 20.0


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def show_title():
    title = "FAT SNAKE GAME"
    print("=" * 46)
    print(title.center(46))
    print("=" * 46)


def main_menu():
    """Returns: 'play' | 'settings' | 'quit'"""
    clear_screen()
    show_title()
    print()
    print("  1. Play")
    print("  2. Settings")
    print("  3. Quit")
    print()
    while True:
        choice = input("> Choose an option [1-3]: ").strip()
        if choice == "1": return "play"
        if choice == "2": return "settings"
        if choice == "3": return "quit"
        print("  ! Invalid option, try again.")


def settings_menu(m, n, v):
    """Returns: (m, n, v). Empty input keeps the current value."""
    clear_screen()
    show_title()
    print()
    print("  Current settings:")
    print(f"    Rows     : {m}")
    print(f"    Columns  : {n}")
    print(f"    Velocity : {v}")
    print()
    print("  Press Enter to keep the current value.")
    print()
    while True:
        try:
            raw = input(f"  Rows     [{m}]: ").strip()
            new_m = int(raw) if raw else m

            raw = input(f"  Columns  [{n}]: ").strip()
            new_n = int(raw) if raw else n

            raw = input(f"  Velocity [{v}]: ").strip()
            new_v = float(raw) if raw else v

            if new_m < MIN_DIM or new_n < MIN_DIM:
                print(f"  ! Minimum size is {MIN_DIM}x{MIN_DIM}. Try again.\n")
                continue
            if not (MIN_VELOCITY <= new_v <= MAX_VELOCITY):
                print(f"  ! Velocity must be between {MIN_VELOCITY} and {MAX_VELOCITY}. Try again.\n")
                continue
            return new_m, new_n, new_v
        except ValueError:
            print("  ! Please enter valid numbers. Try again.\n")


def game_over_menu(score, won, elapsed):
    """Returns: 'again' | 'menu' | 'quit'"""
    clear_screen()
    show_title()
    print()
    print("            *** YOU WIN ***" if won else "            !!! GAME OVER !!!")
    print()
    print(f"  Score       : {score}")
    print(f"  Time played : {elapsed:.1f}s")
    print()
    print("  1. Play Again")
    print("  2. Main Menu")
    print("  3. Quit")
    print()
    while True:
        choice = input("> Choose an option [1-3]: ").strip()
        if choice == "1": return "again"
        if choice == "2": return "menu"
        if choice == "3": return "quit"
        print("  ! Invalid option, try again.")