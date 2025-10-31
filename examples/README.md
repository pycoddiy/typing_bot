# Examples Directory

This directory contains example files demonstrating various features of the typing bot structured format.

## Core Examples

### Basic Examples
- **`example.sxt`** - Simple basic example showing the fundamental structured format
- **`example_python.sxt`** - Python-specific code example
- **`example_mixed.sxt`** - Mixed content example

### Editor-Specific Examples
- **`example_vscode.sxt`** - VS Code specific commands and shortcuts
- **`example_vim.sxt`** - VIM specific commands and navigation
- **`example_shell.sxt`** - Shell/terminal specific commands

### Interactive Editor Demos
- **`editor_example.sxt`** - Comprehensive VS Code style interactive demo with matplotlib plotting
- **`editor_example_vim.sxt`** - VIM style version of the interactive demo showing VIM navigation patterns

## Feature Demonstrations

### Syntax Highlighting
- **`python_highlight_demo.sxt`** - Demonstrates Python syntax highlighting features

### Short Commands
- **`short_commands_demo.sxt`** - Shows the short command syntax (`<u5>`, `<l3>`, etc.)
- **`short_commands_clean_demo.sxt`** - Clean version demonstrating concise short command usage

## Usage

You can run any example with:
```bash
# Interactive editor mode
python struct_editor.py examples/example_name.sxt

# Direct processing
python structured_capture.py examples/example_name.sxt

# Preview mode
python structured_capture.py examples/example_name.sxt --preview
```

## Key Features Demonstrated

1. **Templates** - `{{IMPORT_NUMPY}}`, `{{IF_NAME_MAIN}}`, `{{TRY_EXCEPT}}`
2. **Editor Commands** - Both VS Code and VIM navigation styles
3. **Short Syntax** - Concise commands like `<u5>` for `ARROW_UP 5`
4. **Syntax Highlighting** - Context-aware Python code highlighting
5. **Mixed Content** - Code sections with different languages and command types

## Comparison

Compare `editor_example.sxt` (VS Code style) with `editor_example_vim.sxt` (VIM style) to see different approaches to the same task:
- VS Code uses cursor positioning and keyboard shortcuts
- VIM uses word movements and modal navigation patterns
