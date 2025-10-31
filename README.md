# TyRec — typing recorder

TyRec (tyrec.py) simulates typing from an input file and supports a small set of escape/command sequences, an "arrow mode", and live input recording via the Pause/Break key.

## Table of Contents

- [Installation](#installation)
- [New: Structured Format & Interactive Editor](#new-structured-format--interactive-editor)
- [Documentation](#documentation)
- [Interactive Editor Features](#interactive-editor-features)
- [Legacy Format (tyrec.py)](#legacy-format-tyrecpy)
- [Running TyRec from anywhere](#running-tyrec-from-anywhere-add-to-path)

## Installation

### Basic Installation

To install typing-bot for basic usage:

```bash
pip install typing-bot
```

### Development Installation

If you need to run the project's tests or contribute to development, install with dev dependencies:

```bash
pip install -e '.[dev]'
```

The dev installation includes:
- **pytest** - For running tests
- **pre-commit** - For code quality checks
- **black, isort, flake8** - For code formatting and linting
- **mypy** - For type checking
- **coverage** - For test coverage reports
- **bandit** - For security scanning

See [DEVELOPMENT.md](DEVELOPMENT.md) for complete development setup instructions.

## New: Structured Format & Interactive Editor

**🎉 NEW FEATURES:**
- **Structured Format**: Write readable `.sxt` files instead of cryptic escape sequences
- **Interactive Editor**: Visual editor with live preview and syntax highlighting
- **Tool-Specific Commands**: Context-aware shortcuts for VIM, VS Code, Shell, and Python

### Quick Start with Structured Format

```bash
# Use the interactive editor
python struct_editor.py examples/example.sxt

# Or convert and run structured files
python structured_capture.py examples/example.sxt --preview
python structured_capture.py examples/example.sxt --active_window_title "VS Code"
```

**Structured format example:**
```
<CODE: PYTHON>
    {{IMPORT_NUMPY}}
    data = np.array([1, 2, 3])
    print(f"Mean: {np.mean(data)}")
</CODE>

<COMMANDS: VIM>
    SAVE
    NORMAL_MODE
</COMMANDS>
```

**📖 Quick Navigation:**
- [Documentation](#documentation) - Complete guides and references
- [Interactive Editor](#interactive-editor-features) - Visual editor features
- [Examples](examples/) - Ready-to-use examples and demos
- [Legacy Format](#legacy-format-tyrecpy) - Original tyrec.py documentation

See [STRUCTURED_FORMAT.md](STRUCTURED_FORMAT.md) for complete documentation.

## Documentation

### 📚 Complete Documentation

- **[STRUCTURED_FORMAT.md](STRUCTURED_FORMAT.md)** - Complete guide to the structured format syntax, commands, and templates
- **[EDITOR_IMPLEMENTATION.md](EDITOR_IMPLEMENTATION.md)** - Interactive editor features, interface design, and usage guide
- **[SHORT_COMMANDS.md](SHORT_COMMANDS.md)** - Concise short command syntax (`<u5>`, `<l3>`, etc.) for improved readability
- **[SYNTAX_HIGHLIGHTING.md](SYNTAX_HIGHLIGHTING.md)** - Context-aware Python syntax highlighting features

### 📁 Directory Documentation

## Directory Structure

- **[examples/README.md](examples/README.md)** - Example .sxt files and demonstration usage
- **[scripts/README.md](scripts/README.md)** - Utility scripts and development tools
- **[tests/README.md](tests/README.md)** - Development test files and testing documentation

### 🚀 Getting Started

1. **Start Here**: Try the [interactive editor](#interactive-editor-features) with `python struct_editor.py examples/example.sxt`
2. **Learn the Format**: Read [STRUCTURED_FORMAT.md](STRUCTURED_FORMAT.md) for complete syntax guide
3. **Explore Examples**: Browse [examples/](examples/) directory for real-world usage patterns
4. **Advanced Features**: Check [SHORT_COMMANDS.md](SHORT_COMMANDS.md) for productivity shortcuts

---

## Interactive Editor Features

The new `struct_editor.py` provides:
- **Split-pane interface**: Source on left, live preview on right
- **Syntax highlighting**: Color-coded sections and commands
- **Real-time preview**: See converted output as you type
- **File operations**: Save, open, new file with keyboard shortcuts
- **Error prevention**: Visual feedback prevents syntax errors

---

## Legacy Format (tyrec.py)

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

## Running TyRec from anywhere (add to PATH)

If you want to run `tyrec.py` from any working directory, add the repository folder (the folder containing `tyrec.py`) to your PATH so that PowerShell (or another shell) can find it.

Examples for PowerShell (run in an elevated shell if you want to update the system PATH):

- Run once in the current session by prepending the folder to the PATH environment variable:

```powershell
$env:PATH = "C:\path\to\typing_bot;" + $env:PATH
python tyrec.py CODE_FILE.txt
```

- Make the PATH change permanent for the current user (persist across sessions):

```powershell
[Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";C:\path\to\typing_bot", "User")
# you may need to restart PowerShell for the change to take effect
```

- Alternatively, call the script by full path without modifying PATH:

```powershell
python C:\path\to\typing_bot\tyrec.py C:\path\to\code_to_type.txt
```

Replace `C:\path\to\typing_bot` with the actual absolute path to your repository.
