#!/usr/bin/env python3
# Copyright: 2024 MoinMoin contributors
# License: GNU GPL v2 (or any later version), see LICENSE.txt for details.

"""
MoinMoin - Standalone text search script for finding text across project files.

This script provides VS Code-like text search functionality for the MoinMoin project.
It can be used as a standalone tool without requiring the full MoinMoin installation.
"""

import os
import re
import sys
import argparse
from pathlib import Path
from typing import List, Tuple


def search_in_file(file_path: Path, pattern: str, case_sensitive: bool = False, whole_word: bool = False) -> List[Tuple]:
    """
    Search for a pattern in a single file.
    
    Returns a list of tuples: (line_number, line_content, match_positions)
    """
    matches = []
    flags = 0 if case_sensitive else re.IGNORECASE
    
    if whole_word:
        search_pattern = r'\b' + re.escape(pattern) + r'\b'
    else:
        search_pattern = re.escape(pattern)
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                match_positions = []
                for match in re.finditer(search_pattern, line, flags):
                    match_positions.append((match.start(), match.end()))
                
                if match_positions:
                    matches.append((line_num, line.rstrip(), match_positions))
    except (IOError, UnicodeDecodeError):
        # Skip files that can't be read
        pass
    
    return matches


def get_search_files(root_path: Path, include_patterns: List[str] = None, exclude_patterns: List[str] = None) -> List[Path]:
    """
    Get list of files to search based on include/exclude patterns.
    """
    if include_patterns is None:
        include_patterns = ['*.py', '*.txt', '*.md', '*.rst', '*.html', '*.js', '*.css', '*.json', '*.yaml', '*.yml']
    
    if exclude_patterns is None:
        exclude_patterns = [
            '*.pyc', '*.pyo', '*.pyd', '__pycache__', '.git', '.hg', '.svn', 
            'node_modules', '.tox', '.cache', 'build', 'dist', '*.egg-info'
        ]
    
    files = []
    exclude_dirs = {pattern.strip('*').strip('/') for pattern in exclude_patterns if not pattern.startswith('*.')}
    exclude_exts = {pattern for pattern in exclude_patterns if pattern.startswith('*.')}
    
    for root, dirs, filenames in os.walk(root_path):
        # Remove excluded directories from dirs list to prevent walking into them
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for filename in filenames:
            file_path = Path(root) / filename
            
            # Check if file extension is excluded
            if any(file_path.match(pattern) for pattern in exclude_exts):
                continue
            
            # Check if file matches include patterns
            if any(file_path.match(pattern) for pattern in include_patterns):
                files.append(file_path)
    
    return files


def highlight_match(text: str, start: int, end: int) -> str:
    """
    Add simple text highlighting for matches (for terminals that support it).
    """
    # ANSI color codes for highlighting
    RED_BOLD = '\033[1;31m'
    RESET = '\033[0m'
    
    return text[:start] + RED_BOLD + text[start:end] + RESET + text[end:]


def search_project(search_term: str, root_path: str = ".", include_patterns: List[str] = None, 
                  exclude_patterns: List[str] = None, case_sensitive: bool = False, 
                  whole_word: bool = False, max_results: int = 100, context: int = 0):
    """
    Search for text across project files.
    """
    root_path = Path(root_path).resolve()
    
    if not root_path.exists():
        print(f"Error: Path '{root_path}' does not exist.", file=sys.stderr)
        return 1
    
    if not root_path.is_dir():
        print(f"Error: Path '{root_path}' is not a directory.", file=sys.stderr)
        return 1
    
    print(f"Searching for '{search_term}' in {root_path}")
    if include_patterns:
        print(f"Including: {', '.join(include_patterns)}")
    if exclude_patterns:
        print(f"Excluding: {', '.join(exclude_patterns)}")
    print()
    
    files = get_search_files(root_path, include_patterns, exclude_patterns)
    total_matches = 0
    files_with_matches = 0
    
    for file_path in files:
        matches = search_in_file(file_path, search_term, case_sensitive, whole_word)
        
        if matches:
            files_with_matches += 1
            relative_path = file_path.relative_to(root_path)
            print(f"\n{relative_path}")
            print("=" * len(str(relative_path)))
            
            for line_num, line_content, match_positions in matches:
                total_matches += len(match_positions)
                
                if total_matches > max_results:
                    print(f"\n... truncated at {max_results} matches. Use --max-results to see more.")
                    return 0
                
                # Highlight matches in the line
                highlighted_line = line_content
                offset = 0
                for start, end in match_positions:
                    highlighted_line = highlight_match(highlighted_line, start + offset, end + offset)
                    offset += len('\033[1;31m') + len('\033[0m')  # ANSI code length
                
                print(f"  {line_num:4d}: {highlighted_line}")
                
                # Show context lines if requested
                if context > 0:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            
                        start_line = max(0, line_num - 1 - context)
                        end_line = min(len(lines), line_num + context)
                        
                        for i in range(start_line, end_line):
                            if i != line_num - 1:  # Don't repeat the match line
                                context_line = lines[i].rstrip()
                                print(f"  {i + 1:4d}: {context_line}")
                    except (IOError, UnicodeDecodeError):
                        pass
    
    print(f"\nFound {total_matches} matches in {files_with_matches} files")
    return 0


def main():
    """Main entry point for the standalone script."""
    parser = argparse.ArgumentParser(
        description="Search for text across project files (VS Code-like functionality)",
        epilog="""
Examples:
  python search_files.py "TODO"
  python search_files.py "class User" --include "*.py"
  python search_files.py "config" --exclude "*.pyc" --case-sensitive
  python search_files.py "search" --whole-word --context 2
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("search_term", help="Text to search for")
    parser.add_argument("--path", "-p", default=".", help="Root path to search in (default: current directory)")
    parser.add_argument("--include", "-i", action="append", help="File patterns to include (can be used multiple times)")
    parser.add_argument("--exclude", "-e", action="append", help="File patterns to exclude (can be used multiple times)")
    parser.add_argument("--case-sensitive", "-c", action="store_true", help="Perform case-sensitive search")
    parser.add_argument("--whole-word", "-w", action="store_true", help="Match whole words only")
    parser.add_argument("--max-results", "-m", type=int, default=100, help="Maximum number of results to show")
    parser.add_argument("--context", "-C", type=int, default=0, help="Number of context lines to show around matches")
    
    args = parser.parse_args()
    
    return search_project(
        search_term=args.search_term,
        root_path=args.path,
        include_patterns=args.include,
        exclude_patterns=args.exclude,
        case_sensitive=args.case_sensitive,
        whole_word=args.whole_word,
        max_results=args.max_results,
        context=args.context
    )


if __name__ == "__main__":
    sys.exit(main())