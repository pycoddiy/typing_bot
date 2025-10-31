#!/usr/bin/env python3
"""
Interactive editor for structured typing bot files (.struct).

This editor provides:
- Split-pane view with source on left, preview on right
- Line-by-line navigation with arrow keys
- Live preview of converted legacy format
- Syntax highlighting for structured format
- File operations (open, save, new)

Usage:
    python struct_editor.py [filename.struct]
"""

import curses
import os
import sys
import argparse
from pathlib import Path
from typing import List, Optional, Tuple
import tempfile

# Add current directory to Python path to import structured_capture
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from structured_capture import StructuredParser


class StructEditor:
    """Interactive editor for .struct files with live preview."""
    
    def __init__(self, stdscr, filename: Optional[str] = None):
        self.stdscr = stdscr
        self.filename = filename
        self.lines: List[str] = []
        self.cursor_y = 0
        self.cursor_x = 0
        self.scroll_y = 0
        self.scroll_x = 0
        self.preview_scroll = 0
        self.modified = False
        self.status_message = ""
        self.parser = StructuredParser()
        
        # Initialize colors
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN, -1)    # Section headers
        curses.init_pair(2, curses.COLOR_BLUE, -1)     # Keywords
        curses.init_pair(3, curses.COLOR_YELLOW, -1)   # Comments
        curses.init_pair(4, curses.COLOR_RED, -1)      # Status/errors
        curses.init_pair(5, curses.COLOR_CYAN, -1)     # Tool specifiers
        curses.init_pair(6, curses.COLOR_MAGENTA, -1)  # Preview header
        
        # Python syntax highlighting colors
        curses.init_pair(7, curses.COLOR_BLUE, -1)     # Python keywords
        curses.init_pair(8, curses.COLOR_GREEN, -1)    # Python strings
        curses.init_pair(9, curses.COLOR_CYAN, -1)     # Python functions/classes
        curses.init_pair(10, curses.COLOR_MAGENTA, -1) # Python numbers
        curses.init_pair(11, curses.COLOR_YELLOW, -1)  # Python operators
        
        # Color constants
        self.COLOR_HEADER = curses.color_pair(1)
        self.COLOR_KEYWORD = curses.color_pair(2)
        self.COLOR_COMMENT = curses.color_pair(3)
        self.COLOR_ERROR = curses.color_pair(4)
        self.COLOR_TOOL = curses.color_pair(5)
        self.COLOR_PREVIEW = curses.color_pair(6)
        
        # Python syntax colors
        self.COLOR_PY_KEYWORD = curses.color_pair(7)
        self.COLOR_PY_STRING = curses.color_pair(8)
        self.COLOR_PY_FUNCTION = curses.color_pair(9)
        self.COLOR_PY_NUMBER = curses.color_pair(10)
        self.COLOR_PY_OPERATOR = curses.color_pair(11)
        
        # Load file if provided
        if filename:
            self.load_file(filename)
        else:
            self.new_file()
        
        # Configure curses
        curses.curs_set(1)
        self.stdscr.keypad(True)
        self.stdscr.timeout(100)  # Non-blocking input with 100ms timeout
        
    def new_file(self):
        """Create a new empty file with template."""
        self.lines = [
            "<CODE>",
            "    # Your code here",
            "    print(\"Hello, World!\")",
            "</CODE>",
            "",
            "<COMMANDS>",
            "    # Commands here",
            "    ENTER 2",
            "</COMMANDS>",
        ]
        self.filename = None
        self.modified = False
        self.cursor_y = 1
        self.cursor_x = 4
        
    def load_file(self, filename: str):
        """Load a .struct file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.lines = f.read().splitlines()
            self.filename = filename
            self.modified = False
            self.status_message = f"Loaded {filename}"
        except Exception as e:
            self.status_message = f"Error loading {filename}: {e}"
            self.new_file()
    
    def save_file(self, filename: Optional[str] = None):
        """Save the current file."""
        if filename:
            self.filename = filename
        
        if not self.filename:
            self.status_message = "No filename specified"
            return False
        
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.lines) + '\n')
            self.modified = False
            self.status_message = f"Saved {self.filename}"
            return True
        except Exception as e:
            self.status_message = f"Error saving: {e}"
            return False
    
    def simulate_execution(self, content: str, up_to_line: int) -> List[str]:
        """Simulate the execution of commands up to a specific line and return the resulting text state."""
        try:
            # Parse the content up to the current line, but handle partial sections
            lines = content.split('\n')
            partial_content = self._build_partial_content(lines, up_to_line)
            
            # Create temporary file with partial content
            with tempfile.NamedTemporaryFile(mode='w', suffix='.struct', delete=False, encoding='utf-8') as f:
                f.write(partial_content)
                temp_filename = f.name
            
            try:
                # Convert using structured parser to get the command sequence
                converted = self.parser.parse_structured_file(temp_filename)
                
                # Simulate the typing execution and filter out section tags
                result_lines = self._simulate_typing_result(converted)
                
                # Remove any section tags that might have leaked through
                filtered_lines = self._filter_section_tags(result_lines)
                return filtered_lines
                
            finally:
                os.unlink(temp_filename)
                
        except Exception as e:
            return [f"Simulation Error: {e}"]
    
    def _filter_section_tags(self, lines: List[str]) -> List[str]:
        """Remove section tags from the result lines."""
        filtered = []
        for line in lines:
            # Remove any text that looks like section tags
            import re
            # Remove patterns like <CODE>, <COMMANDS>, </CODE>, </COMMANDS>, etc.
            cleaned_line = re.sub(r'</?(?:CODE|COMMANDS)(?:\s*:\s*[A-Z]+)?\s*>', '', line)
            if cleaned_line or (not line.strip().startswith('<') or not line.strip().endswith('>')):
                filtered.append(cleaned_line)
        
        # Remove empty lines at the beginning
        while filtered and not filtered[0].strip():
            filtered.pop(0)
            
        return filtered if filtered else [""]
    
    def _build_partial_content(self, lines: List[str], up_to_line: int) -> str:
        """Build content that includes complete sections plus partial processing up to current line."""
        result_lines = []
        i = 0
        
        while i <= up_to_line and i < len(lines):
            line = lines[i].strip()
            
            # Check if this is a section start
            if line.startswith('<CODE') or line.startswith('<COMMANDS'):
                # Find the matching closing tag
                section_type = 'CODE' if line.startswith('<CODE') else 'COMMANDS'
                closing_tag = f'</{section_type}'
                
                # Add the opening tag
                result_lines.append(lines[i])
                i += 1
                
                # Process content within the section
                section_content_lines = []
                section_end_found = False
                
                while i <= up_to_line and i < len(lines):
                    current_line = lines[i]
                    
                    # Check if this is the closing tag
                    if current_line.strip().startswith(closing_tag):
                        section_end_found = True
                        # Add the closing tag and break
                        result_lines.extend(section_content_lines)
                        result_lines.append(current_line)
                        i += 1
                        break
                    else:
                        # Add this line to section content
                        section_content_lines.append(current_line)
                        i += 1
                
                # If we reached the end without finding closing tag, add partial content
                if not section_end_found and section_content_lines:
                    result_lines.extend(section_content_lines)
                    # Add a temporary closing tag to make it valid
                    result_lines.append(f'</{section_type}>')
            elif line.startswith('</'):
                # Skip standalone closing tags
                i += 1
            else:
                # Only include non-tag content
                if not (line.startswith('<') and line.endswith('>')):
                    result_lines.append(lines[i])
                i += 1
        
        return '\n'.join(result_lines)
    
    def _simulate_typing_result(self, commands: str) -> List[str]:
        """Simulate what text would appear after executing the typing commands."""
        # This simulates the final text state that would result from typing
        text_buffer = [""]  # Start with one empty line
        cursor_line = 0
        cursor_col = 0
        
        i = 0
        while i < len(commands):
            char = commands[i]
            
            # Ensure we have enough lines in buffer
            while len(text_buffer) <= cursor_line:
                text_buffer.append("")
            
            if char == '\a':  # Arrow command mode
                if i + 1 < len(commands):
                    arrow_cmd = commands[i + 1]
                    cursor_line, cursor_col = self._handle_arrow_command(
                        arrow_cmd, text_buffer, cursor_line, cursor_col
                    )
                    i += 2  # Skip both \a and the command
                    continue
                else:
                    i += 1
                    continue
            elif char == '\n':
                # Split current line at cursor
                current_line = text_buffer[cursor_line] if cursor_line < len(text_buffer) else ""
                before_cursor = current_line[:cursor_col]
                after_cursor = current_line[cursor_col:]
                
                text_buffer[cursor_line] = before_cursor
                text_buffer.insert(cursor_line + 1, after_cursor)
                cursor_line += 1
                cursor_col = 0
            elif char == '\b':
                # Backspace
                if cursor_col > 0:
                    line = text_buffer[cursor_line]
                    text_buffer[cursor_line] = line[:cursor_col-1] + line[cursor_col:]
                    cursor_col -= 1
                elif cursor_line > 0:
                    # Join with previous line
                    prev_line = text_buffer[cursor_line - 1]
                    current_line = text_buffer[cursor_line] if cursor_line < len(text_buffer) else ""
                    text_buffer[cursor_line - 1] = prev_line + current_line
                    if cursor_line < len(text_buffer):
                        del text_buffer[cursor_line]
                    cursor_line -= 1
                    cursor_col = len(prev_line)
            elif char == '\t':
                # Tab - insert spaces
                line = text_buffer[cursor_line]
                text_buffer[cursor_line] = line[:cursor_col] + "    " + line[cursor_col:]
                cursor_col += 4
            elif 32 <= ord(char) <= 126:  # Printable characters
                line = text_buffer[cursor_line]
                text_buffer[cursor_line] = line[:cursor_col] + char + line[cursor_col:]
                cursor_col += 1
            
            i += 1
        
        # Add cursor indicator to current position
        if cursor_line < len(text_buffer):
            line = text_buffer[cursor_line]
            # Ensure cursor_col is within bounds
            cursor_col = max(0, min(cursor_col, len(line)))
            text_buffer[cursor_line] = line[:cursor_col] + "│" + line[cursor_col:]
        else:
            text_buffer.append("│")
        
        # Remove empty lines at the end
        while len(text_buffer) > 1 and text_buffer[-1] == "":
            text_buffer.pop()
        
        return text_buffer
    
    def _handle_arrow_command(self, cmd: str, text_buffer: List[str], cursor_line: int, cursor_col: int) -> tuple:
        """Handle arrow commands and return new cursor position."""
        if cmd == 'u':  # Up
            cursor_line = max(0, cursor_line - 1)
            if cursor_line < len(text_buffer):
                cursor_col = min(cursor_col, len(text_buffer[cursor_line]))
        elif cmd == 'd':  # Down
            cursor_line = min(len(text_buffer), cursor_line + 1)
            if cursor_line < len(text_buffer):
                cursor_col = min(cursor_col, len(text_buffer[cursor_line]))
        elif cmd == 'l':  # Left
            if cursor_col > 0:
                cursor_col -= 1
            elif cursor_line > 0:
                cursor_line -= 1
                cursor_col = len(text_buffer[cursor_line]) if cursor_line < len(text_buffer) else 0
        elif cmd == 'r':  # Right
            if cursor_line < len(text_buffer) and cursor_col < len(text_buffer[cursor_line]):
                cursor_col += 1
            elif cursor_line < len(text_buffer) - 1:
                cursor_line += 1
                cursor_col = 0
        elif cmd == 'b':  # Home
            cursor_col = 0
        elif cmd == 'e':  # End
            if cursor_line < len(text_buffer):
                cursor_col = len(text_buffer[cursor_line])
        elif cmd == 'B':  # Ctrl+Home
            cursor_line = 0
            cursor_col = 0
        elif cmd == 'E':  # Ctrl+End
            cursor_line = len(text_buffer) - 1 if text_buffer else 0
            if cursor_line < len(text_buffer):
                cursor_col = len(text_buffer[cursor_line])
        elif cmd == 'U':  # Page Up
            cursor_line = max(0, cursor_line - 10)
            if cursor_line < len(text_buffer):
                cursor_col = min(cursor_col, len(text_buffer[cursor_line]))
        elif cmd == 'D':  # Page Down
            cursor_line = min(len(text_buffer), cursor_line + 10)
            if cursor_line < len(text_buffer):
                cursor_col = min(cursor_col, len(text_buffer[cursor_line]))
        # Note: 'z' (sleep) and other commands don't affect cursor position
        
        return cursor_line, cursor_col
    
    def get_syntax_highlight_attr(self, line: str, x: int) -> int:
        """Get the color attribute for syntax highlighting."""
        line_stripped = line.strip()
        
        # Section headers
        if line_stripped.startswith('<') and ('CODE' in line_stripped or 'COMMANDS' in line_stripped):
            if ':' in line_stripped:
                # Tool specifier
                return self.COLOR_TOOL
            return self.COLOR_HEADER
        
        # Comments
        if line_stripped.startswith('#'):
            return self.COLOR_COMMENT
        
        # Commands (uppercase words)
        if line_stripped and line_stripped.split()[0].isupper():
            return self.COLOR_KEYWORD
        
        return curses.A_NORMAL
    
    def get_python_syntax_highlight(self, line: str, start_pos: int, length: int) -> List[tuple]:
        """Get Python syntax highlighting for a portion of text.
        Returns list of (text, color_attr) tuples."""
        import re
        
        # Extract the portion of line to highlight
        text = line[start_pos:start_pos + length] if start_pos + length <= len(line) else line[start_pos:]
        if not text:
            return [(text, curses.A_NORMAL)]
        
        # Python keywords
        python_keywords = {
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else',
            'except', 'exec', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
            'lambda', 'not', 'or', 'pass', 'print', 'raise', 'return', 'try', 'while', 'with',
            'yield', 'True', 'False', 'None'
        }
        
        # Built-in functions
        python_builtins = {
            'abs', 'all', 'any', 'bin', 'bool', 'bytearray', 'bytes', 'callable', 'chr', 'classmethod',
            'compile', 'complex', 'delattr', 'dict', 'dir', 'divmod', 'enumerate', 'eval', 'exec',
            'filter', 'float', 'format', 'frozenset', 'getattr', 'globals', 'hasattr', 'hash',
            'help', 'hex', 'id', 'input', 'int', 'isinstance', 'issubclass', 'iter', 'len',
            'list', 'locals', 'map', 'max', 'memoryview', 'min', 'next', 'object', 'oct',
            'open', 'ord', 'pow', 'property', 'range', 'repr', 'reversed', 'round', 'set',
            'setattr', 'slice', 'sorted', 'staticmethod', 'str', 'sum', 'super', 'tuple',
            'type', 'vars', 'zip', '__import__', 'np', 'plt', 'pd'
        }
        
        result = []
        i = 0
        
        while i < len(text):
            # Skip whitespace
            if text[i].isspace():
                start = i
                while i < len(text) and text[i].isspace():
                    i += 1
                result.append((text[start:i], curses.A_NORMAL))
                continue
            
            # Check for comments
            if text[i] == '#':
                result.append((text[i:], self.COLOR_COMMENT))
                break
            
            # Check for strings
            if text[i] in ['"', "'"]:
                quote = text[i]
                start = i
                i += 1
                # Find the closing quote
                while i < len(text) and text[i] != quote:
                    if text[i] == '\\' and i + 1 < len(text):
                        i += 2  # Skip escaped character
                    else:
                        i += 1
                if i < len(text):
                    i += 1  # Include closing quote
                result.append((text[start:i], self.COLOR_PY_STRING))
                continue
            
            # Check for numbers
            if text[i].isdigit():
                start = i
                while i < len(text) and (text[i].isdigit() or text[i] in '.eE+-'):
                    i += 1
                result.append((text[start:i], self.COLOR_PY_NUMBER))
                continue
            
            # Check for operators
            if text[i] in '+-*/%=<>!&|^~()[]{},.':
                result.append((text[i], self.COLOR_PY_OPERATOR))
                i += 1
                continue
            
            # Check for identifiers (keywords, builtins, functions, variables)
            if text[i].isalpha() or text[i] == '_':
                start = i
                while i < len(text) and (text[i].isalnum() or text[i] == '_'):
                    i += 1
                
                word = text[start:i]
                
                # Check if it's followed by a parenthesis (function call)
                next_non_space = i
                while next_non_space < len(text) and text[next_non_space].isspace():
                    next_non_space += 1
                
                if word in python_keywords:
                    result.append((word, self.COLOR_PY_KEYWORD))
                elif word in python_builtins or (next_non_space < len(text) and text[next_non_space] == '('):
                    result.append((word, self.COLOR_PY_FUNCTION))
                else:
                    result.append((word, curses.A_NORMAL))
                continue
            
            # Default: single character
            result.append((text[i], curses.A_NORMAL))
            i += 1
        
        return result
    
    def draw_line(self, y: int, line: str, is_current: bool = False):
        """Draw a line with syntax highlighting."""
        max_y, max_x = self.stdscr.getmaxyx()
        editor_width = max_x // 2 - 1
        
        if y >= max_y - 2:  # Reserve space for status line
            return
        
        # Clear the line
        try:
            self.stdscr.move(y, 0)
            self.stdscr.clrtoeol()
        except curses.error:
            return
        
        # Draw line number
        line_num = y + self.scroll_y + 1
        try:
            line_num_str = f"{line_num:3d} "
            if is_current:
                self.stdscr.addstr(y, 0, line_num_str, curses.A_REVERSE)
            else:
                self.stdscr.addstr(y, 0, line_num_str, curses.A_DIM)
        except curses.error:
            pass
        
        # Draw the line content with syntax highlighting
        visible_line = line[self.scroll_x:self.scroll_x + editor_width - 4]
        
        # Determine if we should use Python syntax highlighting
        use_python_highlighting = self._should_use_python_highlighting(line)
        
        try:
            if use_python_highlighting:
                # Use Python syntax highlighting
                highlighted_parts = self.get_python_syntax_highlight(visible_line, 0, len(visible_line))
                x_pos = 4
                for text_part, color_attr in highlighted_parts:
                    if x_pos >= editor_width:
                        break
                    display_text = text_part[:editor_width - x_pos] if x_pos + len(text_part) > editor_width else text_part
                    if display_text:
                        if is_current:
                            self.stdscr.addstr(y, x_pos, display_text, color_attr | curses.A_BOLD)
                        else:
                            self.stdscr.addstr(y, x_pos, display_text, color_attr)
                        x_pos += len(display_text)
            else:
                # Use basic syntax highlighting
                attr = self.get_syntax_highlight_attr(line, 0)
                if is_current:
                    self.stdscr.addstr(y, 4, visible_line, attr | curses.A_BOLD)
                else:
                    self.stdscr.addstr(y, 4, visible_line, attr)
        except curses.error:
            pass
    
    def _should_use_python_highlighting(self, line: str) -> bool:
        """Determine if a line should use Python syntax highlighting."""
        line_stripped = line.strip()
        
        # Don't highlight section headers or commands sections
        if line_stripped.startswith('<') and ('CODE' in line_stripped or 'COMMANDS' in line_stripped):
            return False
        
        # Don't highlight end tags
        if line_stripped.startswith('</'):
            return False
        
        # Check if we're in a Python code context based on the line being drawn
        return self._detect_python_context_for_line(line)
    
    def _detect_python_context_for_line(self, target_line: str) -> bool:
        """Detect if a specific line should be treated as Python code."""
        if not hasattr(self, 'lines') or not self.lines:
            return False
        
        # Find which line number this is
        line_y = -1
        for i, file_line in enumerate(self.lines):
            if file_line == target_line:
                line_y = i
                break
        
        if line_y == -1:
            return False
        
        # Look backwards from this line to find the most recent section header
        current_section = None
        for i in range(line_y, -1, -1):
            line = self.lines[i].strip()
            if line.startswith('<CODE'):
                # Check if it's a Python code section
                if 'PYTHON' in line.upper():
                    current_section = 'python'
                elif ':' in line:
                    # Has a tool specifier, check what it is
                    if any(tool in line.upper() for tool in ['VIM', 'VSCODE', 'SHELL']):
                        current_section = 'other'
                    else:
                        current_section = 'python'  # Unknown tool, default to Python
                else:
                    current_section = 'python'  # No tool specified, default to Python
                break
            elif line.startswith('<COMMANDS'):
                current_section = 'commands'
                break
            elif line.startswith('</'):
                continue  # End tag, keep looking
        
        # Also check if we're before a closing tag
        for i in range(line_y + 1, min(len(self.lines), line_y + 10)):
            line = self.lines[i].strip()
            if line.startswith('</CODE'):
                # We're in a code section, use the section type we found
                break
            elif line.startswith('</COMMANDS'):
                current_section = 'commands'
                break
            elif line.startswith('<'):
                # Found another opening tag, stop looking
                break
        
        return current_section == 'python'
    
    def draw_preview(self):
        """Draw the preview pane showing the simulated final text result."""
        max_y, max_x = self.stdscr.getmaxyx()
        preview_x = max_x // 2
        preview_width = max_x - preview_x - 1
        
        # Draw separator
        for y in range(max_y - 1):
            try:
                self.stdscr.addch(y, preview_x - 1, '│')
            except curses.error:
                pass
        
        # Draw preview header
        try:
            header = "Final Text Preview"
            self.stdscr.addstr(0, preview_x, header[:preview_width], self.COLOR_PREVIEW | curses.A_BOLD)
        except curses.error:
            pass
        
        # Get preview content (simulate execution up to current line)
        content = '\n'.join(self.lines)
        preview_lines = self.simulate_execution(content, self.cursor_y)
        
        # Draw preview lines with Python syntax highlighting
        for i, line in enumerate(preview_lines[self.preview_scroll:]):
            screen_y = i + 1
            if screen_y >= max_y - 2:
                break
            
            try:
                self.stdscr.move(screen_y, preview_x)
                self.stdscr.clrtoeol()
                
                # Truncate line to fit preview pane
                display_line = line[:preview_width]
                
                # Handle cursor indicator specially
                if "│" in display_line:
                    parts = display_line.split("│")
                    x_pos = preview_x
                    
                    for j, part in enumerate(parts):
                        if part:
                            # Apply Python syntax highlighting to this part
                            highlighted_parts = self.get_python_syntax_highlight(part, 0, len(part))
                            for text_part, color_attr in highlighted_parts:
                                if text_part:
                                    try:
                                        self.stdscr.addstr(screen_y, x_pos, text_part, color_attr)
                                        x_pos += len(text_part)
                                    except curses.error:
                                        pass
                        
                        # Draw cursor indicator
                        if j < len(parts) - 1:  # Not the last part
                            try:
                                self.stdscr.addstr(screen_y, x_pos, "│", curses.A_REVERSE | curses.A_BOLD)
                                x_pos += 1
                            except curses.error:
                                pass
                else:
                    # No cursor indicator, just apply syntax highlighting
                    highlighted_parts = self.get_python_syntax_highlight(display_line, 0, len(display_line))
                    x_pos = preview_x
                    for text_part, color_attr in highlighted_parts:
                        if text_part:
                            try:
                                self.stdscr.addstr(screen_y, x_pos, text_part, color_attr)
                                x_pos += len(text_part)
                            except curses.error:
                                pass
                            
            except curses.error:
                pass
    
    def draw_status(self):
        """Draw the status line."""
        max_y, max_x = self.stdscr.getmaxyx()
        status_y = max_y - 1
        
        # Clear status line
        try:
            self.stdscr.move(status_y, 0)
            self.stdscr.clrtoeol()
        except curses.error:
            return
        
        # Status information
        modified_indicator = "*" if self.modified else ""
        filename = self.filename or "Untitled"
        cursor_info = f"L{self.cursor_y + 1}:C{self.cursor_x + 1}"
        
        left_status = f"{filename}{modified_indicator} - {cursor_info}"
        right_status = "Ctrl+S:Save | Ctrl+O:Open | Ctrl+N:New | Ctrl+Q:Quit | ↑↓:Navigate"
        
        # Draw status
        try:
            self.stdscr.addstr(status_y, 0, left_status[:max_x//2], curses.A_REVERSE)
            
            if len(right_status) < max_x - len(left_status) - 1:
                status_x = max_x - len(right_status)
                self.stdscr.addstr(status_y, status_x, right_status, curses.A_REVERSE)
        except curses.error:
            pass
        
        # Draw status message if any
        if self.status_message:
            try:
                msg_y = max_y - 2
                self.stdscr.move(msg_y, 0)
                self.stdscr.clrtoeol()
                self.stdscr.addstr(msg_y, 0, self.status_message[:max_x], self.COLOR_ERROR)
            except curses.error:
                pass
    
    def draw_screen(self):
        """Draw the entire screen."""
        max_y, max_x = self.stdscr.getmaxyx()
        editor_height = max_y - 2  # Reserve space for status
        
        # Clear screen
        self.stdscr.clear()
        
        # Draw editor pane
        for i in range(editor_height):
            line_idx = i + self.scroll_y
            if line_idx < len(self.lines):
                is_current = (line_idx == self.cursor_y)
                self.draw_line(i, self.lines[line_idx], is_current)
            else:
                self.draw_line(i, "", False)
        
        # Draw preview pane
        self.draw_preview()
        
        # Draw status line
        self.draw_status()
        
        # Position cursor
        try:
            screen_y = self.cursor_y - self.scroll_y
            screen_x = 4 + self.cursor_x - self.scroll_x
            if 0 <= screen_y < editor_height:
                self.stdscr.move(screen_y, min(screen_x, max_x // 2 - 2))
        except curses.error:
            pass
        
        self.stdscr.refresh()
    
    def handle_key(self, key: int) -> bool:
        """Handle keyboard input. Returns False to quit."""
        max_y, max_x = self.stdscr.getmaxyx()
        editor_width = max_x // 2 - 4
        
        # Clear status message after a key press
        if self.status_message and key != -1:
            self.status_message = ""
        
        if key == curses.KEY_UP:
            if self.cursor_y > 0:
                self.cursor_y -= 1
                self.cursor_x = min(self.cursor_x, len(self.lines[self.cursor_y]))
                # Scroll up if needed
                if self.cursor_y < self.scroll_y:
                    self.scroll_y = self.cursor_y
        
        elif key == curses.KEY_DOWN:
            if self.cursor_y < len(self.lines) - 1:
                self.cursor_y += 1
                self.cursor_x = min(self.cursor_x, len(self.lines[self.cursor_y]))
                # Scroll down if needed
                if self.cursor_y >= self.scroll_y + max_y - 2:
                    self.scroll_y = self.cursor_y - max_y + 3
        
        elif key == curses.KEY_LEFT:
            if self.cursor_x > 0:
                self.cursor_x -= 1
            elif self.cursor_y > 0:
                self.cursor_y -= 1
                self.cursor_x = len(self.lines[self.cursor_y])
        
        elif key == curses.KEY_RIGHT:
            if self.cursor_x < len(self.lines[self.cursor_y]):
                self.cursor_x += 1
            elif self.cursor_y < len(self.lines) - 1:
                self.cursor_y += 1
                self.cursor_x = 0
        
        elif key == curses.KEY_HOME:
            self.cursor_x = 0
        
        elif key == curses.KEY_END:
            self.cursor_x = len(self.lines[self.cursor_y])
        
        elif key == curses.KEY_BACKSPACE or key == 127:
            if self.cursor_x > 0:
                line = self.lines[self.cursor_y]
                self.lines[self.cursor_y] = line[:self.cursor_x-1] + line[self.cursor_x:]
                self.cursor_x -= 1
                self.modified = True
            elif self.cursor_y > 0:
                # Join with previous line
                prev_len = len(self.lines[self.cursor_y - 1])
                self.lines[self.cursor_y - 1] += self.lines[self.cursor_y]
                del self.lines[self.cursor_y]
                self.cursor_y -= 1
                self.cursor_x = prev_len
                self.modified = True
        
        elif key == curses.KEY_DC:  # Delete key
            line = self.lines[self.cursor_y]
            if self.cursor_x < len(line):
                self.lines[self.cursor_y] = line[:self.cursor_x] + line[self.cursor_x+1:]
                self.modified = True
            elif self.cursor_y < len(self.lines) - 1:
                # Join with next line
                self.lines[self.cursor_y] += self.lines[self.cursor_y + 1]
                del self.lines[self.cursor_y + 1]
                self.modified = True
        
        elif key == 10 or key == 13:  # Enter
            line = self.lines[self.cursor_y]
            # Split line at cursor
            self.lines[self.cursor_y] = line[:self.cursor_x]
            self.lines.insert(self.cursor_y + 1, line[self.cursor_x:])
            self.cursor_y += 1
            self.cursor_x = 0
            self.modified = True
        
        elif key == 19:  # Ctrl+S
            self.save_file()
        
        elif key == 15:  # Ctrl+O
            self.status_message = "Open file: (not implemented in this demo)"
        
        elif key == 14:  # Ctrl+N
            if self.modified:
                self.status_message = "Unsaved changes! Save first."
            else:
                self.new_file()
        
        elif key == 17:  # Ctrl+Q
            if self.modified:
                self.status_message = "Unsaved changes! Save first or press Ctrl+Q again to force quit."
                return True
            return False
        
        elif 32 <= key <= 126:  # Printable characters
            line = self.lines[self.cursor_y]
            char = chr(key)
            self.lines[self.cursor_y] = line[:self.cursor_x] + char + line[self.cursor_x:]
            self.cursor_x += 1
            self.modified = True
        
        return True
    
    def run(self):
        """Main editor loop."""
        # Track previous state to determine if redraw is needed
        prev_cursor_y = self.cursor_y
        prev_cursor_x = self.cursor_x
        prev_scroll_y = self.scroll_y
        prev_scroll_x = self.scroll_x
        prev_modified = self.modified
        prev_status_message = self.status_message
        
        # Initial draw
        self.draw_screen()
        
        while True:
            key = self.stdscr.getch()
            
            if not self.handle_key(key):
                break
            
            # Check if anything changed that requires a redraw
            needs_redraw = (
                self.cursor_y != prev_cursor_y or          # Cursor moved to different line
                self.cursor_x != prev_cursor_x or          # Cursor moved horizontally (affects preview)
                self.scroll_y != prev_scroll_y or          # Vertical scroll changed
                self.scroll_x != prev_scroll_x or          # Horizontal scroll changed
                self.modified != prev_modified or          # Content was modified
                self.status_message != prev_status_message # Status message changed
            )
            
            # Only redraw if there was a meaningful change
            if needs_redraw:
                self.draw_screen()
                
                # Update previous state
                prev_cursor_y = self.cursor_y
                prev_cursor_x = self.cursor_x
                prev_scroll_y = self.scroll_y
                prev_scroll_x = self.scroll_x
                prev_modified = self.modified
                prev_status_message = self.status_message


def main():
    """Main entry point for the struct editor."""
    parser = argparse.ArgumentParser(
        description="Interactive editor for structured typing bot files"
    )
    parser.add_argument(
        "filename",
        nargs="?",
        help="Path to the .struct file to edit",
    )
    
    args = parser.parse_args()
    
    def editor_main(stdscr):
        editor = StructEditor(stdscr, args.filename)
        editor.run()
    
    try:
        curses.wrapper(editor_main)
    except KeyboardInterrupt:
        print("\nEditor interrupted.")
    except Exception as e:
        print(f"Editor error: {e}")


if __name__ == "__main__":
    main()