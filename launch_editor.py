#!/usr/bin/env python3
"""
Launcher for the struct editor with error handling and environment checks.
"""

import os
import sys


def check_terminal_support():
    """Check if the terminal supports curses."""
    try:
        import curses

        # Test if we can initialize curses
        if not sys.stdout.isatty():
            return False, "Not running in a TTY (terminal)"

        if os.environ.get("TERM", "") == "":
            return False, "TERM environment variable not set"

        return True, "Terminal support OK"
    except ImportError:
        return False, "curses module not available"
    except Exception as e:
        return False, f"Terminal check failed: {e}"


def main():
    """Main launcher."""
    print("Struct Editor Launcher")
    print("=" * 40)

    # Check terminal support
    supported, message = check_terminal_support()
    print(f"Terminal check: {message}")

    if not supported:
        print("\nThe interactive editor requires a proper terminal environment.")
        print("You can still use the core functionality:")
        print()
        print("1. View the demo:")
        print("   python editor_demo.py")
        print()
        print("2. Use the command-line structured capture:")
        print("   python structured_capture.py examples/example.sxt --preview")
        print()
        print("3. Convert files:")
        print("   python structured_capture.py input.sxt --output output.txt")
        return 1

    print("\nLaunching interactive editor...")
    print("Use Ctrl+Q to quit the editor")
    print()

    try:
        # Import and run the editor
        from struct_editor import main as editor_main

        editor_main()
    except KeyboardInterrupt:
        print("\nEditor interrupted by user.")
    except Exception as e:
        print(f"\nEditor error: {e}")
        print("\nFallback options:")
        print("- python editor_demo.py  (view demo)")
        print("- python structured_capture.py --help  (command line tool)")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
