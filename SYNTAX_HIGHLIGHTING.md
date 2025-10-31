# Syntax Highlighting Enhancement

## Overview
Enhanced the raw editor (left pane) with context-aware Python syntax highlighting to match the preview pane functionality.

## Features Added

### Context-Aware Highlighting
- **Python Code Sections**: Full Python syntax highlighting with colors for:
  - Keywords (import, def, if, for, etc.)
  - Function names and built-ins
  - Strings and numbers
  - Operators and punctuation
  - Comments

- **Commands Sections**: Basic highlighting for:
  - Section headers
  - Command keywords
  - Comments

- **Mixed Content**: Automatically detects section type based on:
  - `<CODE: PYTHON>` → Python highlighting
  - `<CODE>` → Python highlighting (default)
  - `<COMMANDS>` → Basic highlighting
  - Tool-specific sections handled appropriately

### Implementation Details

#### New Methods Added:
1. `_should_use_python_highlighting(line)` - Determines highlighting mode
2. `_detect_python_context_for_line(line)` - Context detection logic

#### Enhanced Method:
- `draw_line()` - Now supports both Python and basic syntax highlighting modes

#### Context Detection Logic:
1. Scans backwards from current line to find section header
2. Identifies section type (CODE vs COMMANDS)
3. Checks for tool specifiers (PYTHON, VIM, VSCODE, SHELL)
4. Defaults to Python highlighting for generic CODE sections
5. Uses basic highlighting for COMMANDS and non-Python sections

## Usage
The enhancement is automatic - no user interaction required. The raw editor will now display:

- **Python code** with full syntax highlighting (same as preview pane)
- **Commands** with basic highlighting for readability
- **Section headers** with appropriate formatting

## Benefits
1. **Improved Readability**: Python code is easier to read and understand
2. **Consistency**: Raw editor now matches preview pane highlighting
3. **Context Awareness**: Different highlighting for different content types
4. **Better Development Experience**: Syntax errors and structure more visible

## Testing
Use the test file created by `test_syntax_highlighting.py` or any existing `.sxt` file to see the enhanced highlighting in action.
