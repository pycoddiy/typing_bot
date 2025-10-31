#!/usr/bin/env python3
"""
High-level wrapper for capture.py that supports structured input files.

This module provides a more readable and maintainable format for typing bot scripts
by introducing <COMMANDS> and <CODE> sections, multi-line command formatting,
and explicit ENTER command encoding.

Usage:
    python structured_capture.py input.struct --active_window_title "VS Code"
"""

import re
import argparse
import tempfile
import os
import sys
from pathlib import Path
from capture import main as capture_main


class StructuredParser:
    """Parser for structured typing bot files."""
    
    def __init__(self):
        # Generic command mappings from readable names to capture.py format
        self.generic_commands = {
            'ARROW_UP': '\au',
            'ARROW_DOWN': '\ad', 
            'ARROW_LEFT': '\al',
            'ARROW_RIGHT': '\ar',
            'SHIFT_PRESS': '\as',
            'SHIFT_RELEASE': '\aS',
            'END': '\ae',
            'HOME': '\ab',
            'CTRL_END': '\aE',
            'CTRL_HOME': '\aB',
            'PAGE_UP': '\aU',
            'PAGE_DOWN': '\aD',
            'ESCAPE': '\aC',
            'BACKSPACE': '\b',
            'ENTER': '\n',
            'SLEEP': '\az',  # 5-second sleep
            'EXIT_ARROW_MODE': '\aQ',
        }
        
        # Tool-specific command mappings
        self.tool_specific_commands = {
            'VIM': {
                # Vim mode shortcuts
                'NORMAL_MODE': '\aC',  # ESC to normal mode
                'INSERT_MODE': 'i',
                'APPEND_MODE': 'a',
                'VISUAL_MODE': 'v',
                'COMMAND_MODE': ':',
                'SAVE': ':w\n',
                'QUIT': ':q\n',
                'SAVE_QUIT': ':wq\n',
                'FORCE_QUIT': ':q!\n',
                'DELETE_LINE': 'dd',
                'YANK_LINE': 'yy',
                'PASTE': 'p',
                'UNDO': 'u',
                'REDO': '\ar',  # Ctrl+R
                'WORD_FORWARD': 'w',
                'WORD_BACKWARD': 'b',
                'LINE_END': '$',
                'LINE_START': '0',
                'FILE_TOP': 'gg',
                'FILE_BOTTOM': 'G',
            },
            'SHELL': {
                # Shell/terminal shortcuts
                'CLEAR': 'clear\n',
                'CTRL_C': '\a',  # Will be handled specially
                'CTRL_D': '\a',  # Will be handled specially
                'TAB_COMPLETE': '\t',
                'HISTORY_UP': '\au',
                'HISTORY_DOWN': '\ad',
                'MOVE_TO_START': '\ab',  # Ctrl+A
                'MOVE_TO_END': '\ae',    # Ctrl+E
                'DELETE_WORD': '\a',     # Will be handled specially
                'KILL_LINE': '\a',       # Will be handled specially
            },
            'VSCODE': {
                # VS Code shortcuts
                'SAVE': '\as',           # Ctrl+S (will be handled specially)
                'COPY': '\ac',           # Ctrl+C (will be handled specially)
                'PASTE': '\av',          # Ctrl+V (will be handled specially)
                'UNDO': '\az',           # Ctrl+Z (will be handled specially)
                'REDO': '\ay',           # Ctrl+Y (will be handled specially)
                'FIND': '\af',           # Ctrl+F (will be handled specially)
                'COMMENT': '\a/',        # Ctrl+/ (will be handled specially)
                'FORMAT': '\aS\af',      # Ctrl+Shift+F (will be handled specially)
                'COMMAND_PALETTE': '\aS\ap',  # Ctrl+Shift+P (will be handled specially)
            },
            'PYTHON': {
                # Python-specific shortcuts (these expand to actual code)
                'IMPORT_NUMPY': 'import numpy as np\n',
                'IMPORT_PANDAS': 'import pandas as pd\n',
                'IMPORT_MATPLOTLIB': 'import matplotlib.pyplot as plt\n',
                'PRINT_DEBUG': 'print(f"DEBUG: {}"))\alllll',  # positions cursor inside braces
                'IF_NAME_MAIN': 'if __name__ == "__main__":\n    ',
                'TRY_EXCEPT': 'try:\n    \nexcept Exception as e:\n    print(f"Error: {e}")\auuuu\ae',
            }
        }
        
    def parse_structured_file(self, filepath: str) -> str:
        """Parse a structured file and convert it to capture.py format."""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Split content into sections
        sections = self._split_into_sections(content)
        
        result = []
        for section_data in sections:
            if len(section_data) == 3:
                section_type, section_content, tool_specifier = section_data
            else:
                # Legacy format compatibility
                section_type, section_content = section_data
                tool_specifier = None
                
            if section_type == 'CODE':
                result.append(self._process_code_section(section_content, tool_specifier))
            elif section_type == 'COMMANDS':
                result.append(self._process_commands_section(section_content, tool_specifier))
            else:
                # Plain text outside sections - treat as code
                result.append(section_content)
                
        return ''.join(result)
    
    def _split_into_sections(self, content: str) -> list:
        """Split content into alternating CODE and COMMANDS sections."""
        sections = []
        
        # Pattern to match section headers with optional tool specifier
        # Matches: <CODE>, <CODE: PYTHON>, <COMMANDS>, <COMMANDS: VIM>, etc.
        section_pattern = r'<(CODE|COMMANDS)(?:\s*:\s*([A-Z]+))?\s*>\s*\n(.*?)\n\s*</\1(?:\s*:\s*[A-Z]+)?>'
        
        last_end = 0
        for match in re.finditer(section_pattern, content, re.DOTALL | re.IGNORECASE):
            # Add any content before this section as plain text
            before = content[last_end:match.start()].strip()
            if before:
                sections.append(('TEXT', before, None))
            
            section_type = match.group(1).upper()
            tool_specifier = match.group(2).upper() if match.group(2) else None
            section_content = match.group(3)
            sections.append((section_type, section_content, tool_specifier))
            
            last_end = match.end()
        
        # Add any remaining content as plain text
        after = content[last_end:].strip()
        if after:
            sections.append(('TEXT', after, None))
            
        return sections
    
    def _process_code_section(self, content: str, tool_specifier: str = None) -> str:
        """Process a CODE section - return content as-is but handle newlines properly."""
        # Strip common indentation from the content
        lines = content.split('\n')
        # Remove empty lines at the beginning and end for indentation calculation
        non_empty_lines = [line for line in lines if line.strip()]
        if not non_empty_lines:
            return content
        
        # Find the minimum indentation level
        min_indent = min(len(line) - len(line.lstrip()) 
                        for line in non_empty_lines if line.strip())
        
        # Remove the common indentation from all lines
        dedented_lines = []
        for line in lines:
            if line.strip():  # Non-empty line
                dedented_lines.append(line[min_indent:] if len(line) >= min_indent else line)
            else:  # Empty line
                dedented_lines.append('')
        
        processed_content = '\n'.join(dedented_lines)
        
        # Apply tool-specific expansions if specified
        if tool_specifier and tool_specifier in self.tool_specific_commands:
            processed_content = self._expand_tool_shortcuts(processed_content, tool_specifier)
        
        return processed_content
    
    def _expand_tool_shortcuts(self, content: str, tool: str) -> str:
        """Expand tool-specific shortcuts in content."""
        if tool not in self.tool_specific_commands:
            return content
            
        tool_commands = self.tool_specific_commands[tool]
        
        # Replace shortcuts with their expanded forms
        # Use word boundaries to avoid partial matches
        for shortcut, expansion in tool_commands.items():
            # Look for {{SHORTCUT}} pattern for explicit expansion
            pattern = r'\{\{' + re.escape(shortcut) + r'\}\}'
            content = re.sub(pattern, expansion, content)
            
        return content
    
    def _process_commands_section(self, content: str, tool_specifier: str = None) -> str:
        """Process a COMMANDS section and convert to capture.py escape sequences."""
        result = []
        
        # Strip common indentation first
        lines = content.strip().split('\n')
        if lines:
            # Find minimum indentation of non-empty, non-comment lines
            non_empty_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
            if non_empty_lines:
                min_indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines)
                # Remove common indentation, but preserve structure for comments
                dedented_lines = []
                for line in lines:
                    if line.strip():  # Non-empty line
                        if line.strip().startswith('#'):
                            # For comments, just remove leading whitespace but preserve the comment
                            dedented_lines.append(line.strip())
                        elif len(line) >= min_indent:
                            # For commands, remove the common indentation
                            dedented_lines.append(line[min_indent:])
                        else:
                            # Line has less indentation than expected, keep as-is
                            dedented_lines.append(line)
                    else:
                        # Empty line
                        dedented_lines.append('')
                lines = dedented_lines
        
        # Get the appropriate command map
        command_map = self.generic_commands.copy()
        if tool_specifier and tool_specifier in self.tool_specific_commands:
            command_map.update(self.tool_specific_commands[tool_specifier])
        
        # Parse commands line by line
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Parse command with optional count
            parts = line.split()
            if not parts:
                continue
                
            command = parts[0].upper()
            count = 1
            
            # Check if there's a count specified
            if len(parts) > 1:
                try:
                    count = int(parts[1])
                except ValueError:
                    # If second part is not a number, treat the whole line as invalid command
                    print(f"Warning: Invalid command format '{line}', skipping")
                    continue
            
            # Convert command to escape sequence
            if command in command_map:
                escape_seq = command_map[command]
                
                # Special handling for certain commands
                if command in ['ARROW_UP', 'ARROW_DOWN', 'ARROW_LEFT', 'ARROW_RIGHT', 
                              'BACKSPACE', 'ENTER']:
                    # These commands can be repeated
                    result.append(escape_seq * count)
                elif command == 'SLEEP':
                    # Sleep command - repeat the sequence
                    result.append(escape_seq * count)
                else:
                    # Other commands don't repeat, but may be tool-specific expansions
                    if count > 1:
                        print(f"Warning: Command '{command}' doesn't support repetition, ignoring count")
                    result.append(escape_seq)
            else:
                print(f"Warning: Unknown command '{command}' in line '{line}', skipping")
                
        return ''.join(result)


def convert_structured_to_legacy(input_file: str, output_file: str = None) -> str:
    """Convert a structured file to legacy capture.py format."""
    parser = StructuredParser()
    converted_content = parser.parse_structured_file(input_file)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(converted_content)
        return output_file
    else:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(converted_content)
            return f.name


def main():
    """Main entry point for structured capture."""
    parser = argparse.ArgumentParser(
        description="Structured typing recorder - high-level wrapper for capture.py"
    )
    parser.add_argument(
        "input_file",
        help="Path to the structured input file (.struct or .txt)",
    )
    parser.add_argument(
        "--active_window_title",
        "-t",
        dest="active_window_title", 
        default="PowerShell",
        help="Expected window title substring to wait for before typing (default: PowerShell)",
    )
    parser.add_argument(
        "--no-delay",
        action="store_true",
        help="Disable random delays for faster testing",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output the converted legacy format to this file instead of running",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview the converted content without running",
    )
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.")
        return 1
    
    try:
        # Convert structured file to legacy format
        if args.output:
            # Save to specified output file
            legacy_file = convert_structured_to_legacy(args.input_file, args.output)
            print(f"Converted structured file to legacy format: {legacy_file}")
            return 0
        elif args.preview:
            # Preview the converted content
            parser = StructuredParser()
            converted_content = parser.parse_structured_file(args.input_file)
            print("=== Converted Content (Legacy Format) ===")
            # Show escaped characters visually
            preview_content = repr(converted_content)[1:-1]  # Remove outer quotes
            print(preview_content)
            return 0
        else:
            # Create temporary file and run capture.py
            legacy_file = convert_structured_to_legacy(args.input_file)
            
            try:
                # Prepare arguments for capture.py
                capture_args = [
                    legacy_file,
                    "--active_window_title", args.active_window_title,
                ]
                
                if args.no_delay:
                    capture_args.append("--no-delay")
                
                # Temporarily modify sys.argv to pass arguments to capture.py
                original_argv = sys.argv[:]
                sys.argv = ["capture.py"] + capture_args
                
                # Run capture.py
                capture_main()
                
                # Restore original argv
                sys.argv = original_argv
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(legacy_file)
                except OSError:
                    pass
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())