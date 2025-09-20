# Copyright: 2024 MoinMoin contributors
# License: GNU GPL v2 (or any later version), see LICENSE.txt for details.

"""
MoinMoin - CLI search functionality for finding text across project files.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Set

import click


def search_in_file(file_path: Path, pattern: str, case_sensitive: bool = False, whole_word: bool = False) -> List[tuple]:
    """
    Search for a pattern in a single file.
    
    Returns a list of tuples: (line_number, line_content, match_positions)
    """
    matches = []
    flags = 0 if case_sensitive else re.IGNORECASE
    
    if whole_word:
        pattern = r'\b' + re.escape(pattern) + r'\b'
    else:
        pattern = re.escape(pattern)
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                match_positions = []
                for match in re.finditer(pattern, line, flags):
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


@click.command("search-text")
@click.argument("search_term")
@click.option("--path", "-p", default=".", help="Root path to search in (default: current directory)")
@click.option("--include", "-i", multiple=True, help="File patterns to include (default: common text files)")
@click.option("--exclude", "-e", multiple=True, help="File patterns to exclude")
@click.option("--case-sensitive", "-c", is_flag=True, help="Perform case-sensitive search")
@click.option("--whole-word", "-w", is_flag=True, help="Match whole words only")
@click.option("--max-results", "-m", default=100, help="Maximum number of results to show")
@click.option("--context", "-C", default=0, help="Number of context lines to show around matches")
def search_text(search_term, path, include, exclude, case_sensitive, whole_word, max_results, context):
    """
    Search for text across project files.
    
    This command searches for the specified SEARCH_TERM across all text files
    in the project, similar to VS Code's "Search in Files" functionality.
    
    Examples:
        moin search-text "TODO"
        moin search-text "class User" --include "*.py"
        moin search-text "config" --exclude "*.pyc" --case-sensitive
        moin search-text "search" --whole-word --context 2
    """
    root_path = Path(path).resolve()
    
    if not root_path.exists():
        click.echo(f"Error: Path '{path}' does not exist.", err=True)
        sys.exit(1)
    
    if not root_path.is_dir():
        click.echo(f"Error: Path '{path}' is not a directory.", err=True)
        sys.exit(1)
    
    include_patterns = list(include) if include else None
    exclude_patterns = list(exclude) if exclude else None
    
    click.echo(f"Searching for '{search_term}' in {root_path}")
    if include_patterns:
        click.echo(f"Including: {', '.join(include_patterns)}")
    if exclude_patterns:
        click.echo(f"Excluding: {', '.join(exclude_patterns)}")
    click.echo()
    
    files = get_search_files(root_path, include_patterns, exclude_patterns)
    total_matches = 0
    files_with_matches = 0
    
    for file_path in files:
        matches = search_in_file(file_path, search_term, case_sensitive, whole_word)
        
        if matches:
            files_with_matches += 1
            relative_path = file_path.relative_to(root_path)
            click.echo(f"\n{click.style(str(relative_path), fg='blue', bold=True)}")
            
            for line_num, line_content, match_positions in matches:
                total_matches += len(match_positions)
                
                if total_matches > max_results:
                    click.echo(f"\n... truncated at {max_results} matches. Use --max-results to see more.")
                    return
                
                # Highlight matches in the line
                highlighted_line = line_content
                offset = 0
                for start, end in match_positions:
                    match_text = line_content[start:end]
                    highlighted_match = click.style(match_text, fg='red', bold=True)
                    highlighted_line = (highlighted_line[:start + offset] + 
                                      highlighted_match + 
                                      highlighted_line[end + offset:])
                    offset += len(highlighted_match) - len(match_text)
                
                click.echo(f"  {click.style(str(line_num), fg='green')}:{' ' if line_num < 10 else ''} {highlighted_line}")
                
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
                                click.echo(f"  {click.style(str(i + 1), fg='yellow')}:{' ' if i + 1 < 10 else ''} {context_line}")
                    except (IOError, UnicodeDecodeError):
                        pass
    
    click.echo(f"\nFound {total_matches} matches in {files_with_matches} files")


if __name__ == "__main__":
    search_text()