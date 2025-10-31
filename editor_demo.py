#!/usr/bin/env python3
"""
Demo script for the struct_editor.py functionality.

This script demonstrates the features of the interactive editor without requiring
a full terminal interface.
"""

import os
import sys
import tempfile

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from struct_editor import StructuredParser


def demo_editor_features():
    """Demonstrate the editor features."""
    print("=== Struct Editor Demo ===\n")
    
    # Create sample content
    sample_content = """<CODE: PYTHON>
    # Python code with shortcuts
    {{IMPORT_NUMPY}}
    
    def calculate_mean(data):
        return np.mean(data)
    
    {{IF_NAME_MAIN}}
        data = [1, 2, 3, 4, 5]
        result = calculate_mean(data)
        {{PRINT_DEBUG}}
</CODE>

<COMMANDS>
    # Navigate and edit
    ARROW_UP 2
    ARROW_RIGHT 10
    BACKSPACE 6
</COMMANDS>

<CODE>
    print(f"Mean value: {result}")
</CODE>

<COMMANDS: VSCODE>
    # Save using VS Code shortcut
    SAVE
</COMMANDS>"""

    print("1. Sample .struct file content:")
    print("-" * 50)
    print(sample_content)
    print("-" * 50)
    print()
    
    # Create temporary file and parse
    with tempfile.NamedTemporaryFile(mode='w', suffix='.struct', delete=False, encoding='utf-8') as f:
        f.write(sample_content)
        temp_file = f.name
    
    try:
        parser = StructuredParser()
        converted = parser.parse_structured_file(temp_file)
        
        print("2. Live preview (final text result after executing commands):")
        print("-" * 50)
        
        # Simulate the execution to show final text result
        from struct_editor import StructEditor
        import curses
        
        # Create a mock editor to use the simulation method
        class MockEditor:
            def __init__(self):
                self.parser = StructuredParser()
            
            def simulate_execution(self, content, up_to_line):
                # Use the same simulation logic as the editor
                try:
                    lines = content.split('\n')
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.struct', delete=False, encoding='utf-8') as f:
                        f.write(content)
                        temp_filename = f.name
                    
                    try:
                        converted = self.parser.parse_structured_file(temp_filename)
                        return self._simulate_typing_result(converted)
                    finally:
                        os.unlink(temp_filename)
                except Exception as e:
                    return [f"Simulation Error: {e}"]
            
            def _simulate_typing_result(self, commands):
                text_buffer = []
                cursor_line = 0
                cursor_col = 0
                
                i = 0
                while i < len(commands):
                    char = commands[i]
                    
                    while len(text_buffer) <= cursor_line:
                        text_buffer.append("")
                    
                    if char == '\a':
                        if i + 1 < len(commands):
                            arrow_cmd = commands[i + 1]
                            cursor_line, cursor_col = self._handle_arrow_command(
                                arrow_cmd, text_buffer, cursor_line, cursor_col
                            )
                            i += 2
                            continue
                        else:
                            i += 1
                            continue
                    elif char == '\n':
                        current_line = text_buffer[cursor_line] if cursor_line < len(text_buffer) else ""
                        before_cursor = current_line[:cursor_col]
                        after_cursor = current_line[cursor_col:]
                        text_buffer[cursor_line] = before_cursor
                        text_buffer.insert(cursor_line + 1, after_cursor)
                        cursor_line += 1
                        cursor_col = 0
                    elif char == '\b':
                        if cursor_col > 0:
                            line = text_buffer[cursor_line]
                            text_buffer[cursor_line] = line[:cursor_col-1] + line[cursor_col:]
                            cursor_col -= 1
                        elif cursor_line > 0:
                            prev_line = text_buffer[cursor_line - 1]
                            current_line = text_buffer[cursor_line]
                            text_buffer[cursor_line - 1] = prev_line + current_line
                            del text_buffer[cursor_line]
                            cursor_line -= 1
                            cursor_col = len(prev_line)
                    elif 32 <= ord(char) <= 126:
                        line = text_buffer[cursor_line]
                        text_buffer[cursor_line] = line[:cursor_col] + char + line[cursor_col:]
                        cursor_col += 1
                    
                    i += 1
                
                if len(text_buffer) > cursor_line:
                    line = text_buffer[cursor_line]
                    text_buffer[cursor_line] = line[:cursor_col] + "│" + line[cursor_col:]
                else:
                    text_buffer.append("│")
                
                return text_buffer
            
            def _handle_arrow_command(self, cmd, text_buffer, cursor_line, cursor_col):
                if cmd == 'u':
                    cursor_line = max(0, cursor_line - 1)
                    if cursor_line < len(text_buffer):
                        cursor_col = min(cursor_col, len(text_buffer[cursor_line]))
                elif cmd == 'd':
                    cursor_line = min(len(text_buffer), cursor_line + 1)
                    if cursor_line < len(text_buffer):
                        cursor_col = min(cursor_col, len(text_buffer[cursor_line]))
                elif cmd == 'l':
                    if cursor_col > 0:
                        cursor_col -= 1
                    elif cursor_line > 0:
                        cursor_line -= 1
                        cursor_col = len(text_buffer[cursor_line]) if cursor_line < len(text_buffer) else 0
                elif cmd == 'r':
                    if cursor_line < len(text_buffer) and cursor_col < len(text_buffer[cursor_line]):
                        cursor_col += 1
                    elif cursor_line < len(text_buffer) - 1:
                        cursor_line += 1
                        cursor_col = 0
                elif cmd == 'b':
                    cursor_col = 0
                elif cmd == 'e':
                    if cursor_line < len(text_buffer):
                        cursor_col = len(text_buffer[cursor_line])
                elif cmd == 'B':
                    cursor_line = 0
                    cursor_col = 0
                elif cmd == 'E':
                    cursor_line = len(text_buffer) - 1 if text_buffer else 0
                    if cursor_line < len(text_buffer):
                        cursor_col = len(text_buffer[cursor_line])
                
                return cursor_line, cursor_col
        
        mock_editor = MockEditor()
        final_result = mock_editor.simulate_execution(sample_content, 100)  # Show full execution
        
        for i, line in enumerate(final_result, 1):
            print(f"{i:3d}: {line}")
        print("-" * 50)
        print("Note: │ indicates cursor position")
        print()
        
        print("3. Editor Features:")
        print("-" * 50)
        print("• Split-pane interface: Source code on left, final text preview on right")
        print("• Syntax highlighting for .struct format:")
        print("  - Green: Section headers (<CODE>, <COMMANDS>)")
        print("  - Cyan: Tool specifiers (PYTHON, VIM, VSCODE, etc.)")
        print("  - Blue: Command keywords (ARROW_UP, BACKSPACE, etc.)")
        print("  - Yellow: Comments (lines starting with #)")
        print("• Python syntax highlighting in preview pane:")
        print("  - Blue: Python keywords (def, import, if, return, etc.)")
        print("  - Green: Strings (\"text\", 'text')")
        print("  - Cyan: Functions and method calls")
        print("  - Magenta: Numbers")
        print("  - Yellow: Operators (+, -, =, etc.)")
        print("  - Yellow: Comments (# text)")
        print("• Real-time preview showing final text result")
        print("• Cursor position indicator (│) shows where typing would be")
        print("• Line-by-line execution preview up to current editor line")
        print("• Standard editing operations (insert, delete, backspace)")
        print("• File operations:")
        print("  - Ctrl+S: Save file")
        print("  - Ctrl+O: Open file (prompt for filename)")
        print("  - Ctrl+N: New file")
        print("  - Ctrl+Q: Quit (with unsaved changes warning)")
        print()
        
        print("4. Usage Examples:")
        print("-" * 50)
        print("# Start editor with new file:")
        print("python struct_editor.py")
        print()
        print("# Edit existing file:")
        print("python struct_editor.py example.struct")
        print()
        print("# The editor provides immediate visual feedback:")
        print("# - Type '{{IMPORT_NUMPY}}' in a <CODE: PYTHON> section")
        print("# - See it expand to 'import numpy as np' in the preview")
        print("# - Add commands in <COMMANDS> sections")
        print("# - Watch the text get modified in real-time in the preview")
        print("# - See exactly where the cursor would be positioned")
        print()
        
        print("5. Benefits:")
        print("-" * 50)
        print("• Visual editing makes complex automation scripts easier to create")
        print("• Immediate feedback shows exactly what text will be produced")
        print("• Split view shows both readable source and final text result")
        print("• Syntax highlighting improves readability")
        print("• Real-time simulation prevents errors and misunderstandings")
        print("• See cursor positioning and text modifications in real-time")
        print()
        
    finally:
        os.unlink(temp_file)


def show_editor_layout():
    """Show what the editor interface looks like."""
    print("6. Editor Interface Layout:")
    print("=" * 80)
    print("┌─────────────────────── Source (.struct) ─────────────┬── Final Text Preview ───┐")
    print("│  1 <CODE: PYTHON>                                     │Final Text Preview        │")
    print("│  2     # Python code with shortcuts                  │                          │")
    print("│  3     import numpy as np                            │  1: # Python code with s │")
    print("│ >4                                                   │  2: import numpy as np   │")
    print("│  5     def calculate_mean(data):                     │  3:                      │")
    print("│  6         return np.mean(data)                      │  4: def calculate_mean(d │")
    print("│  7                                                   │  5:     return np.mean(d │")
    print("│  8     if __name__ == \"__main__\":                    │  6:                      │")
    print("│  9         data = [1, 2, 3, 4, 5]                   │  7: if __name__ == \"__ma │")
    print("│ 10         result = calculate_mean(data)             │  8:     data = [1, 2, 3, │")
    print("│ 11         print(f\"DEBUG: {}\")                       │  9:     result = calcula │")
    print("│ 12 </CODE>                                           │ 10:     print(f\"DEBUG: {│")
    print("│ 13                                                   │ 11:                      │")
    print("│ 14 <COMMANDS>                                        │ 12: print(f\"Mean: {resul│")
    print("│ 15     ARROW_UP 2                                    │ 13:                      │")
    print("│ 16     ARROW_RIGHT 6                                 │                          │")
    print("│ 17     BACKSPACE 6                                   │                          │")
    print("│ 18 </COMMANDS>                                       │                          │")
    print("├──────────────────────────────────────────────────────┴──────────────────────────┤")
    print("│example.struct* - L4:C1    Ctrl+S:Save │ ↑↓:Navigate │ Ctrl+Q:Quit              │")
    print("└───────────────────────────────────────────────────────────────────────────────────┘")
    print()
    print("Legend:")
    print("• > indicates current cursor line")
    print("• * indicates unsaved changes")
    print("• Left pane shows editable .struct source with syntax highlighting")
    print("• Right pane shows final text that would result from execution up to current line")
    print("• │ in preview indicates where the typing cursor would be positioned")
    print("• Status bar shows file info and keyboard shortcuts")


if __name__ == "__main__":
    demo_editor_features()
    show_editor_layout()
    
    print("\n" + "=" * 80)
    print("To try the interactive editor:")
    print("python struct_editor.py [filename.struct]")
    print("=" * 80)