# Scripts Directory

This directory contains utility scripts for the typing bot project.

## Code Generation Scripts (.sxt)

### Code Typing Utilities
- **`code_to_type_test.sxt`** - Basic code typing utility script
- **`code_to_type_vim.sxt`** - VIM-specific code typing utility
- **`code_to_type_vscode.sxt`** - VS Code-specific code typing utility

## Output Files (.txt)

Generated output files from the code typing utilities:
- **`code_to_type_test.txt`** - Generated output from basic utility
- **`code_to_type_vim.txt`** - Generated output from VIM utility
- **`code_to_type_vscode.txt`** - Generated output from VS Code utility

## Usage

These scripts are primarily used for:
1. **Code Generation** - Create typing sequences for different editors
2. **Utility Functions** - Generate sample outputs for demonstration
3. **Editor Testing** - Test editor-specific command sequences

### Running Utilities

```bash
# Generate code typing samples
python structured_capture.py scripts/code_to_type_vim.sxt --output scripts/code_to_type_vim.txt
python structured_capture.py scripts/code_to_type_vscode.sxt --output scripts/code_to_type_vscode.txt

# Preview utilities
python structured_capture.py scripts/code_to_type_test.sxt --preview
```

### Organization

Scripts are focused on development utilities:
- **Development tests** are now in `./tests/` directory
- **User examples** are in `./examples/` directory

For test files, see [../tests/README.md](../tests/README.md)
