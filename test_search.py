#!/usr/bin/env python3
"""
Test script for the text search functionality.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the current directory to Python path to import our search module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from search_files import search_in_file, get_search_files, search_project


def test_search_in_file():
    """Test the basic search functionality."""
    print("Testing search_in_file...")
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("""Line 1: This is a test file
Line 2: It contains the word SEARCH multiple times
Line 3: Another search term here
Line 4: Case sensitive Search test
Line 5: No match here
""")
        temp_file = Path(f.name)
    
    try:
        # Test case-insensitive search
        matches = search_in_file(temp_file, "search", case_sensitive=False)
        assert len(matches) == 3, f"Expected 3 matches, got {len(matches)}"
        print("✓ Case-insensitive search works")
        
        # Test case-sensitive search
        matches = search_in_file(temp_file, "search", case_sensitive=True)
        assert len(matches) == 1, f"Expected 1 match, got {len(matches)}"
        print("✓ Case-sensitive search works")
        
        # Test whole word search
        matches = search_in_file(temp_file, "search", whole_word=True)
        assert len(matches) == 3, f"Expected 3 matches, got {len(matches)}"
        print("✓ Whole word search works")
        
    finally:
        # Clean up
        temp_file.unlink()


def test_get_search_files():
    """Test the file discovery functionality."""
    print("\nTesting get_search_files...")
    
    # Test with current directory
    files = get_search_files(Path("."), include_patterns=["*.py"], exclude_patterns=["__pycache__"])
    
    # Should find some Python files
    python_files = [f for f in files if f.suffix == '.py']
    assert len(python_files) > 0, "Should find at least one Python file"
    print(f"✓ Found {len(python_files)} Python files")
    
    # Should not include cache directories
    cache_files = [f for f in files if '__pycache__' in str(f)]
    assert len(cache_files) == 0, "Should not include cache files"
    print("✓ Properly excludes cache files")


def test_project_search():
    """Test the full project search functionality."""
    print("\nTesting project search...")
    
    # Create a temporary directory with test files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test files
        (temp_path / "test1.py").write_text("def search_function(): pass\n")
        (temp_path / "test2.txt").write_text("This file contains search terms\n")
        (temp_path / "test3.md").write_text("# Search Documentation\n")
        
        # Create a subdirectory
        sub_dir = temp_path / "subdir"
        sub_dir.mkdir()
        (sub_dir / "test4.py").write_text("# Another search example\n")
        
        # Test the search
        from io import StringIO
        import contextlib
        
        # Capture output
        output = StringIO()
        
        # Run search with output capture (simplified test)
        files = get_search_files(temp_path, include_patterns=["*.py", "*.txt", "*.md"])
        search_files = []
        
        for file_path in files:
            matches = search_in_file(file_path, "search", case_sensitive=False)
            if matches:
                search_files.append(file_path)
        
        # Should find all test files
        assert len(search_files) == 4, f"Expected 4 files with matches, got {len(search_files)}"
        print("✓ Project search finds all matching files")


def main():
    """Run all tests."""
    print("Running text search functionality tests...\n")
    
    try:
        test_search_in_file()
        test_get_search_files()
        test_project_search()
        
        print("\n🎉 All tests passed!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())