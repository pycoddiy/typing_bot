# Short Command Syntax

## Overview
The structured format now supports concise short command syntax for common repetitive commands, making files more readable and easier to write.

## Short Command Format

### Basic Syntax
Short commands use the format `<letter><optional_number>` where:
- `letter` is a single character representing the command
- `optional_number` is the repeat count (defaults to 1 if omitted)

### Supported Short Commands

| Short | Full Command | Description | Examples |
|-------|-------------|-------------|-----------|
| `<u>` | `ARROW_UP` | Move cursor up | `<u>` = up 1, `<u5>` = up 5 |
| `<d>` | `ARROW_DOWN` | Move cursor down | `<d>` = down 1, `<d3>` = down 3 |
| `<l>` | `ARROW_LEFT` | Move cursor left | `<l>` = left 1, `<l3>` = left 3 |
| `<r>` | `ARROW_RIGHT` | Move cursor right | `<r>` = right 1, `<r10>` = right 10 |
| `<e>` | `ENTER` | Insert newline | `<e>` = 1 enter, `<e2>` = 2 enters |
| `<b>` | `BACKSPACE` | Delete character | `<b>` = 1 backspace, `<b3>` = 3 backspaces |
| `<s>` | `SLEEP` | Pause execution | `<s>` = 1 sleep, `<s3>` = 3 sleeps |
| `<h>` | `HOME` | Move to line start | `<h>` = go home |
| `<E>` | `END` | Move to line end | `<E>` = go to end |
| `<h>` | `HOME` | Move to line start | `<h>` = home (no repeat) |
| `<E>` | `END` | Move to line end | `<E>` = end (no repeat) |

## Usage Examples

### Before (Verbose)
```
<COMMANDS>
    ARROW_LEFT 3
    ENTER 2
    ARROW_UP 5
    ARROW_RIGHT 10
    BACKSPACE 2
</COMMANDS>
```

### After (Concise)
```
<COMMANDS>
    <l3>
    <e2>
    <u5>
    <r10>
    <b2>
</COMMANDS>
```

### Mixed Usage
You can mix short and long syntax in the same file:
```
<COMMANDS>
    CTRL_END      # Use full name for clarity
    <l3>          # Use short syntax for common repeats
    HOME          # Use full name for special commands
    <e2>          # Use short syntax for brevity
</COMMANDS>
```

## Benefits

1. **Readability**: Much easier to scan and understand command sequences
2. **Conciseness**: Reduces file size and typing effort
3. **Consistency**: Familiar `<>` bracket syntax
4. **Flexibility**: Can specify any repeat count
5. **Backward Compatible**: Old syntax continues to work
6. **Self-Documenting**: Short commands are intuitive (u=up, l=left, etc.)

## Technical Details

### Expansion Process
1. Short commands are expanded during parsing before normal command processing
2. `<u5>` becomes `ARROW_UP 5` internally
3. Then processed normally through the existing command system
4. Results in the same escape sequences as the verbose syntax

### Pattern Matching
- Case insensitive: `<U5>` and `<u5>` both work
- Whitespace ignored: `< u5 >` works (though not recommended)
- Must be complete tokens: `<<u5>>` won't match

### Error Handling
- Unknown command letters are left as-is: `<x5>` stays `<x5>`
- Invalid numbers default to 1: `<uabc>` becomes `<u>`
- Malformed syntax is preserved: `<>` stays `<>`

## Migration Guide

### Converting Existing Files
Replace common patterns:
- `ARROW_LEFT 3` → `<l3>`
- `ARROW_UP 5` → `<u5>`
- `ENTER 2` → `<e2>`
- `BACKSPACE` → `<b>`

### Best Practices
1. Use short syntax for repetitive commands (>1 count)
2. Use full syntax for special commands (CTRL_END, HOME, etc.)
3. Add comments to explain complex sequences
4. Prefer short syntax in templates and examples for readability

## Compatibility
- ✅ Fully backward compatible - old syntax still works
- ✅ Works with all existing tools and templates
- ✅ No changes needed to existing files
- ✅ Can gradually migrate files as needed