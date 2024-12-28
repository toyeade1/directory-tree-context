# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "click",
#     "gitignore-parser",
# ]
# ///

import click
from pathlib import Path
from typing import List, Optional, Set
from gitignore_parser import parse_gitignore
import sys

DEFAULT_EXCLUDES = {
    '.git', '__pycache__', 'node_modules', '.pytest_cache',
    '.venv', 'venv', '.env', '.idea', '.vscode'
}

def get_gitignore_matcher(repo_path: Path):
    """Create a matcher function from .gitignore if it exists."""
    gitignore_path = repo_path / '.gitignore'
    if gitignore_path.exists():
        return parse_gitignore(gitignore_path)
    return lambda x: False

def should_exclude(path: Path, exclude_patterns: Set[str], gitignore_matcher) -> bool:
    """Check if a path should be excluded based on patterns and .gitignore."""
    # Check if any parent directory is in exclude patterns
    for parent in path.parents:
        if parent.name in exclude_patterns:
            return True
    
    # Check if current file/directory is in exclude patterns
    if path.name in exclude_patterns:
        return True
    
    # Check if path is ignored by .gitignore
    return gitignore_matcher(str(path))

def generate_tree(
    path: Path,
    exclude_patterns: Set[str],
    gitignore_matcher,
    prefix: str = "",
    is_last: bool = True,
    ) -> List[str]:
    """Generate tree structure of the directory."""
    lines = []
    
    # Skip if path should be excluded
    if should_exclude(path, exclude_patterns, gitignore_matcher):
        return lines
    
    # Add current path to tree
    connector = "└── " if is_last else "├── "
    lines.append(f"{prefix}{connector}{path.name}")
    
    # Handle directory contents
    if path.is_dir():
        # Prepare new prefix for children
        new_prefix = prefix + ("    " if is_last else "│   ")
        
        # Get and sort directory contents
        contents = sorted(list(path.iterdir()), key=lambda x: (x.is_file(), x.name))
        
        # Process each item
        for i, item in enumerate(contents):
            is_last_item = i == len(contents) - 1
            lines.extend(generate_tree(
                item,
                exclude_patterns,
                gitignore_matcher,
                new_prefix,
                is_last_item
            ))
    
    return lines

def matches_pattern(path: Path, patterns: Set[str]) -> bool:
    """Check if path matches any of the include patterns."""
    # Convert path to string for comparison
    path_str = str(path)
    
    for pattern in patterns:
        # Handle exact matches
        if pattern == path_str or pattern == path.name:
            return True
            
        # Handle wildcard patterns
        if pattern.startswith("**/"):
            # Match file in any subdirectory
            if path.name == pattern[3:]:
                return True
        elif "/" in pattern:
            # Handle relative path patterns
            if path_str.endswith(pattern):
                return True
    
    return False

def get_file_contents(
    path: Path,
    include_patterns: Set[str],
    exclude_patterns: Set[str],
    gitignore_matcher
    ) -> List[str]:
    """Get contents of specified files that aren't excluded."""
    contents = []
    
    if path.is_file():
        if (matches_pattern(path, include_patterns) and 
            not should_exclude(path, exclude_patterns, gitignore_matcher)):
            contents.append(f"\nFile: {path}\n{'=' * (len(str(path)) + 6)}\n")
            try:
                contents.extend(path.read_text().splitlines())
            except Exception as e:
                contents.append(f"Error reading file: {e}")
    elif path.is_dir():
        for item in sorted(path.iterdir()):
            contents.extend(get_file_contents(
                item,
                include_patterns,
                exclude_patterns,
                gitignore_matcher
            ))
    
    return contents

@click.command()
@click.argument('repo_path', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
@click.option('--exclude', '-e', multiple=True, help='Additional patterns to exclude')
@click.option('--include-content', '-i', multiple=True, 
              help='Patterns of files to include contents')
def main(
    repo_path: str,
    output_file: str,
    exclude: tuple[str, ...],
    include_content: tuple[str, ...]
    ):
    """Generate repository structure and file contents for LLM analysis."""
    repo_path = Path(repo_path)
    exclude_patterns = DEFAULT_EXCLUDES.union(set(exclude))
    include_patterns = set(include_content)
    
    # Get gitignore matcher
    gitignore_matcher = get_gitignore_matcher(repo_path)
    
    # Generate tree structure
    tree_lines = ["Directory Structure:", "-------------------"]
    tree_lines.extend(generate_tree(repo_path, exclude_patterns, gitignore_matcher))
    
    # Get file contents if specified
    if include_patterns:
        content_lines = ["\nFile Contents:", "-------------"]
        content_lines.extend(get_file_contents(
            repo_path,
            include_patterns,
            exclude_patterns,
            gitignore_matcher
        ))
    else:
        content_lines = []
    
    # Write output
    output_path = Path(output_file)
    try:
        output_path.write_text('\n'.join(tree_lines + content_lines))
        click.echo(f"Output written to {output_file}")
    except Exception as e:
        click.echo(f"Error writing output: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    main()