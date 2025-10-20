# TyRec — typing recorder

TyRec (tyrec.py) simulates typing from an input file and supports a small set of escape/command sequences, an "arrow mode", and live input recording via the Pause/Break key.

## Key commands

TyRec reads characters from an input file and turns them into simulated key events. The following special characters and escape sequences are recognised:

- Newline: `\n` — sends Enter.
- Backspace: `\b` — sends Backspace.
- Space: (literal space) — sends Space.
- Arrow mode trigger: `\a` — when this character appears in the input stream, TyRec switches to "arrow mode" and treats the next character as an arrow/command key instead of a literal character.

When in arrow mode, the next character maps to the following actions:

- `u` — Up arrow
- `d` — Down arrow
- `l` — Left arrow
- `r` — Right arrow
- `s` — press Shift (hold)
- `S` — release Shift
- `e` — End
- `b` — Home
- `E` — Ctrl+End
- `B` — Ctrl+Home
- `U` — Page Up
- `D` — Page Down
- `C` — Escape
- `z` — pause for 5 seconds
- `Q` — exit arrow mode without sending a key

Any unknown command after `\a` will raise an error when running TyRec.

## Live input recording (Pause/Break)

If `pynput` is installed, TyRec starts a background listener that toggles live input recording when the Pause/Break key is pressed. When live input recording is active TyRec will record real-time key events until Pause/Break is pressed again, then resume processing the input file.

If `pynput` isn't available, the Pause/Break toggle and live-recording features are skipped and TyRec falls back to a dry-run controller that prints simulated key events.

## CLI options

Usage: `python tyrec.py [input_file] [options]`

- `input_file` — path to the input file to type. Required.
- `-t`, `--active_window_title` — Expected active window title substring to wait for before typing (default: `PowerShell`). TyRec uses `pygetwindow` if available to check the active window; if not installed it skips the check.
- `--no-delay` — Disable random delays (useful for faster testing).

## Notes

- TyRec will print the processed input to stdout before simulating typing.
- If you want to include literal backslash escape sequences (for example `\\n`) in your input file, ensure they are escaped appropriately for the file encoding and how you're writing the file — TyRec decodes common escape sequences using Python's `unicode_escape` decoding when reading the input file.
