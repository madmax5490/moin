# Text Search Functionality

## Overview

MoinMoin includes a powerful text search feature that allows you to find specific text across all project files, similar to VS Code's "Search in Files" functionality.

## Usage

### Standalone Script

The easiest way to search for text across the project is using the standalone script:

```bash
python search_files.py "search_term"
```

### CLI Command (when MoinMoin is installed)

If you have MoinMoin installed, you can use the CLI command:

```bash
moin search-text "search_term"
```

## Options

- `--path`, `-p`: Root path to search in (default: current directory)
- `--include`, `-i`: File patterns to include (can be used multiple times)
- `--exclude`, `-e`: File patterns to exclude (can be used multiple times)
- `--case-sensitive`, `-c`: Perform case-sensitive search
- `--whole-word`, `-w`: Match whole words only
- `--max-results`, `-m`: Maximum number of results to show (default: 100)
- `--context`, `-C`: Number of context lines to show around matches

## Examples

### Basic Search
```bash
python search_files.py "TODO"
```

### Search in Python Files Only
```bash
python search_files.py "class User" --include "*.py"
```

### Case-Sensitive Search with Exclusions
```bash
python search_files.py "Config" --exclude "*.pyc" --case-sensitive
```

### Whole Word Search with Context
```bash
python search_files.py "search" --whole-word --context 2
```

### Search in Documentation Files
```bash
python search_files.py "installation" --include "*.md" --include "*.rst"
```

## Default File Patterns

### Included by Default
- `*.py` - Python files
- `*.txt` - Text files
- `*.md` - Markdown files
- `*.rst` - reStructuredText files
- `*.html` - HTML files
- `*.js` - JavaScript files
- `*.css` - CSS files
- `*.json` - JSON files
- `*.yaml`, `*.yml` - YAML files

### Excluded by Default
- `*.pyc`, `*.pyo`, `*.pyd` - Compiled Python files
- `__pycache__` - Python cache directories
- `.git`, `.hg`, `.svn` - Version control directories
- `node_modules` - Node.js dependencies
- `.tox`, `.cache` - Build and cache directories
- `build`, `dist` - Build output directories
- `*.egg-info` - Python package metadata

## Features

- **Fast file-based search**: Efficiently searches through text files
- **Pattern matching**: Supports glob patterns for including/excluding files
- **Syntax highlighting**: Highlights search matches in the output
- **Context display**: Shows surrounding lines for better understanding
- **Case sensitivity**: Optional case-sensitive search
- **Whole word matching**: Option to match only complete words
- **Result limiting**: Prevents overwhelming output with too many results
- **UTF-8 support**: Handles various text encodings gracefully

## Implementation Notes

The search functionality is implemented using Python's built-in `re` module for pattern matching and `pathlib` for file system operations. It recursively walks through the directory tree, applying include/exclude filters, and searches each matching file for the specified pattern.

The search results are formatted with ANSI color codes for terminals that support them, making it easy to spot matches in the output.