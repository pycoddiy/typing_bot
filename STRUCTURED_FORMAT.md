# Structured Typing Bot Format

This document describes the new structured format for typing bot files that provides better readability and maintainability compared to the raw escape sequence format. The format supports both generic commands and tool-specific shortcuts for enhanced productivity.

## Overview

The structured format uses XML-like tags to separate code content from control commands:
- `<CODE>` sections contain the actual text to be typed
- `<COMMANDS>` sections contain control commands like arrow keys, backspace, etc.
- **NEW:** Tool specifiers like `<CODE: PYTHON>`, `<COMMANDS: VIM>` provide context-aware shortcuts

## Basic Structure

```
<CODE>
    Your actual code or text content goes here
    It can span multiple lines
    Content is automatically dedented
</CODE>

<COMMANDS>
    # Control commands go here
    ENTER
    ARROW_UP 2
    BACKSPACE 3
</COMMANDS>

<CODE: PYTHON>
    # Python-specific code with shortcuts
    {{IMPORT_NUMPY}}
    {{IF_NAME_MAIN}}
</CODE>

<COMMANDS: VIM>
    # Vim-specific commands
    INSERT_MODE
    SAVE
    NORMAL_MODE
</COMMANDS>
```

## Available Commands

### Generic Navigation Commands
- `ARROW_UP [count]` - Move cursor up (default: 1)
- `ARROW_DOWN [count]` - Move cursor down (default: 1)
- `ARROW_LEFT [count]` - Move cursor left (default: 1)
- `ARROW_RIGHT [count]` - Move cursor right (default: 1)
- `HOME` - Move to beginning of line
- `END` - Move to end of line
- `CTRL_HOME` - Move to beginning of document
- `CTRL_END` - Move to end of document
- `PAGE_UP` - Page up
- `PAGE_DOWN` - Page down

### Generic Editing Commands
- `BACKSPACE [count]` - Delete character(s) before cursor (default: 1)
- `ENTER [count]` - Insert newline(s) (default: 1)

### Generic Modifier Keys
- `SHIFT_PRESS` - Press and hold Shift key
- `SHIFT_RELEASE` - Release Shift key

### Generic Special Commands
- `ESCAPE` - Press Escape key
- `SLEEP [count]` - Sleep for 5 seconds × count (default: 1)
- `EXIT_ARROW_MODE` - Exit arrow command mode

## Tool-Specific Commands

### VIM Commands (`<COMMANDS: VIM>`)
- `NORMAL_MODE` - Switch to normal mode (ESC)
- `INSERT_MODE` - Switch to insert mode (i)
- `APPEND_MODE` - Switch to append mode (a)
- `VISUAL_MODE` - Switch to visual mode (v)
- `COMMAND_MODE` - Enter command mode (:)
- `SAVE` - Save file (:w)
- `QUIT` - Quit (:q)
- `SAVE_QUIT` - Save and quit (:wq)
- `FORCE_QUIT` - Force quit without saving (:q!)
- `DELETE_LINE` - Delete current line (dd)
- `YANK_LINE` - Yank (copy) current line (yy)
- `PASTE` - Paste (p)
- `UNDO` - Undo (u)
- `WORD_FORWARD` - Move forward by word (w)
- `WORD_BACKWARD` - Move backward by word (b)
- `LINE_END` - Move to end of line ($)
- `LINE_START` - Move to start of line (0)
- `FILE_TOP` - Move to top of file (gg)
- `FILE_BOTTOM` - Move to bottom of file (G)

### Shell Commands (`<COMMANDS: SHELL>`)
- `CLEAR` - Clear terminal (clear)
- `TAB_COMPLETE` - Tab completion
- `HISTORY_UP` - Previous command in history
- `HISTORY_DOWN` - Next command in history
- `MOVE_TO_START` - Move cursor to start of line (Ctrl+A)
- `MOVE_TO_END` - Move cursor to end of line (Ctrl+E)

### VS Code Commands (`<COMMANDS: VSCODE>`)
- `SAVE` - Save file (Ctrl+S)
- `COPY` - Copy (Ctrl+C)
- `PASTE` - Paste (Ctrl+V)
- `UNDO` - Undo (Ctrl+Z)
- `REDO` - Redo (Ctrl+Y)
- `FIND` - Find (Ctrl+F)
- `COMMENT` - Toggle comment (Ctrl+/)
- `FORMAT` - Format document (Ctrl+Shift+F)
- `COMMAND_PALETTE` - Open command palette (Ctrl+Shift+P)

## Tool-Specific Code Shortcuts

### Python Shortcuts (`<CODE: PYTHON>`)
Use `{{SHORTCUT}}` syntax to expand common Python patterns:

- `{{IMPORT_NUMPY}}` → `import numpy as np`
- `{{IMPORT_PANDAS}}` → `import pandas as pd`
- `{{IMPORT_MATPLOTLIB}}` → `import matplotlib.pyplot as plt`
- `{{PRINT_DEBUG}}` → `print(f"DEBUG: {|}")` (cursor positioned at |)
- `{{IF_NAME_MAIN}}` → `if __name__ == "__main__":`
- `{{TRY_EXCEPT}}` → Complete try-except block template

## Examples

### Simple Text Entry
```
<CODE>
    print("Hello, World!")
</CODE>
```

### Python with Shortcuts
```
<CODE: PYTHON>
    {{IMPORT_NUMPY}}
    {{IMPORT_MATPLOTLIB}}

    data = np.random.randn(100)
    plt.plot(data)
    plt.show()

    {{IF_NAME_MAIN}}
        {{PRINT_DEBUG}}
</CODE>
```

### VIM Automation
```
<COMMANDS: VIM>
    INSERT_MODE
</COMMANDS>

<CODE>
    #!/bin/bash
    echo "Hello World"
</CODE>

<COMMANDS: VIM>
    NORMAL_MODE
    SAVE
    FILE_TOP
    APPEND_MODE
</COMMANDS>

<CODE>
    # Script header
</CODE>

<COMMANDS: VIM>
    NORMAL_MODE
    SAVE_QUIT
</COMMANDS>
```

### VS Code Workflow
```
<CODE>
    function hello() {
        console.log("Hello");
    }
</CODE>

<COMMANDS: VSCODE>
    SAVE
    FIND
</COMMANDS>

<CODE>
    hello
</CODE>

<COMMANDS: VSCODE>
    ESCAPE
    FORMAT
</COMMANDS>
```

### Shell Session
```
<COMMANDS: SHELL>
    CLEAR
</COMMANDS>

<CODE>
    ls -la
</CODE>

<COMMANDS: SHELL>
    ENTER
    TAB_COMPLETE
</COMMANDS>

<CODE>
    cd proj
</CODE>

<COMMANDS: SHELL>
    TAB_COMPLETE
    ENTER
</COMMANDS>
```

### Text with Corrections
```
<CODE>
    print("Hello, Wrold!")
</CODE>

<COMMANDS>
    # Fix the typo
    BACKSPACE 6
</COMMANDS>

<CODE>
    World!")
</CODE>
```

### Multi-line Commands
```
<COMMANDS>
    # Navigate to top and select all content
    CTRL_HOME
    SHIFT_PRESS
    CTRL_END
    SHIFT_RELEASE
</COMMANDS>
```

### Complex Navigation Example
```
<CODE>
    def hello():
        pass
</CODE>

<COMMANDS>
    # Go back and add parameter
    ARROW_UP 1
    ARROW_LEFT 2
</COMMANDS>

<CODE>
    name
</CODE>

<COMMANDS>
    ARROW_RIGHT 2
    ARROW_DOWN 1
    BACKSPACE 4
</COMMANDS>

<CODE>
    print(f"Hello, {name}!")
</CODE>
```

## Usage

### Interactive Editor

Edit .sxt files with live preview using the interactive editor:

```bash
# Launch editor with new file
python struct_editor.py

# Edit existing file
python struct_editor.py examples/example.sxt

# Or use the launcher (with error handling)
python launch_editor.py
```

**Editor Features:**
- **Split-pane interface**: Source code on left, final text preview on right
- **Syntax highlighting**: Color-coded sections, commands, and comments
- **Real-time preview**: See final text result as it would appear after execution
- **Line-by-line simulation**: Preview shows execution results up to current editor line
- **Cursor position indicator**: See exactly where the typing cursor would be (│)
- **Standard editing**: Insert, delete, backspace, enter
- **File operations**: Save (Ctrl+S), Open (Ctrl+O), New (Ctrl+N), Quit (Ctrl+Q)

### Command Line Interface

Run a structured file:
```bash
python structured_capture.py input.sxt --active_window_title "VS Code"
```

Preview the converted format without running:
```bash
python structured_capture.py input.sxt --preview
```

Convert to legacy format:
```bash
python structured_capture.py input.sxt --output legacy_file.txt
```

### Command Line Options

- `--active_window_title`, `-t`: Window title to wait for (default: "PowerShell")
- `--no-delay`: Disable typing delays for faster execution
- `--preview`: Show converted content without running
- `--output`, `-o`: Convert to legacy format and save to file

## Migration from Legacy Format

The old escape sequence format can be converted to structured format:

**Old format:**
```
print("Hello")\b\b\b\b\bWorld")
```

**New structured format:**
```
<CODE>
    print("Hello")
</CODE>

<COMMANDS>
    BACKSPACE 5
</COMMANDS>

<CODE>
    World")
</CODE>
```

## Benefits

1. **Readability**: Clear separation between code and commands with proper indentation
2. **Maintainability**: Commands can be documented with comments
3. **Grouping**: Related commands can be visually grouped
4. **Explicit Enters**: No confusion between newlines in content vs. Enter commands
5. **Multi-line Commands**: Commands can span multiple lines for better organization
6. **Auto-dedenting**: Content is automatically dedented, so you can indent for readability
7. **Tool-Specific Shortcuts**: Context-aware commands and code expansions for different tools
8. **Code Templates**: Predefined shortcuts for common programming patterns

## File Extensions

- Use `.sxt` extension for structured format files
- Use `.txt` extension for legacy format files

## Supported Tool Specifiers

- `PYTHON` - Python code with import shortcuts and template expansions
- `VIM` - Vim editor commands and navigation
- `SHELL` - Shell/terminal commands and shortcuts
- `VSCODE` - Visual Studio Code keyboard shortcuts
- More tools can be added by extending the parser

## Backward Compatibility

All existing structured files without tool specifiers continue to work unchanged. Tool specifiers are optional and additive.
