# Repository Structure Analyzer

A Python tool that generates a tree-like representation of your repository's structure and optionally includes file contents. Perfect for sharing codebase context with LLMs for debugging and analysis purposes.

## Features

- 🌳 Tree-like directory structure visualization
- 📄 Optional file content inclusion
- 🎯 Multiple file/directory exclusion patterns
- 🔍 Smart path matching for nested files
- ⚡ Compatible with uv package manager for fast installation
- 🙈 Respects .gitignore patterns
- ⚙️ Configurable file content inclusion

## Prerequisites

- Python 3.12 or higher
- uv (recommended) or pip

## Installation

### Using uv (Recommended)

1. First, install uv if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create a new virtual environment and install dependencies:
```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
.venv\Scripts\activate     # On Windows
uv pip install -r requirements.txt
```

### Using pip

```bash
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
.venv\Scripts\activate     # On Windows
pip install -r requirements.txt
```

## Usage

### Basic Usage

Generate a directory structure:
```bash
python repo_analyzer.py /path/to/repo output.txt
```

### Including File Contents

Include specific files:
```bash
# Include a single file
python repo_analyzer.py /path/to/repo output.txt -i "main.py"

# Include multiple files
python repo_analyzer.py /path/to/repo output.txt -i "main.py" -i "config.json"

# Include files in nested directories
python repo_analyzer.py /path/to/repo output.txt -i "src/client/app.py"

# Include all Python files in a specific directory
python repo_analyzer.py /path/to/repo output.txt -i "src/client/*.py"

# Include a file regardless of its location
python repo_analyzer.py /path/to/repo output.txt -i "**/config.yaml"
```

### Excluding Directories/Files

The tool automatically excludes common unnecessary directories (.git, __pycache__, etc.). You can add additional exclusions:

```bash
# Exclude specific directories
python repo_analyzer.py /path/to/repo output.txt -e "tests" -e "docs"

# Combine exclusions with includes
python repo_analyzer.py /path/to/repo output.txt -e "tests" -i "src/**/*.py"
```

### Pattern Matching

The tool supports several ways to specify files:

1. Exact filename:
   ```bash
   -i "config.json"
   ```

2. Exact path:
   ```bash
   -i "src/client/app.py"
   ```

3. Recursive match (any subdirectory):
   ```bash
   -i "**/app.py"
   ```

### Example Output

```
Directory Structure:
-------------------
/
├── src/
│   ├── client/
│   │   ├── app.py
│   │   └── utils.py
│   └── server/
│       └── main.py
├── tests/
│   └── test_app.py
└── README.md

File Contents:
-------------
File: src/client/app.py
=====================
def main():
    print("Hello, World!")

if __name__ == '__main__':
    main()
```

## Default Exclusions

The following directories are excluded by default:
- .git
- __pycache__
- node_modules
- .pytest_cache
- .venv
- venv
- .env
- .idea
- .vscode

## Advanced Usage

### Combining Multiple Patterns

You can combine multiple include and exclude patterns:

```bash
python repo_analyzer.py /path/to/repo output.txt \
    -i "src/**/*.py" \
    -i "config/*.yaml" \
    -e "tests" \
    -e "examples"
```

### Using with LLMs

When using the output with LLMs for debugging or analysis, you might want to:

1. Include relevant configuration files:
```bash
python repo_analyzer.py /path/to/repo output.txt \
    -i "**/config.yaml" \
    -i "**/settings.json" \
    -i "requirements.txt"
```

2. Include specific modules and their tests:
```bash
python repo_analyzer.py /path/to/repo output.txt \
    -i "src/auth/*.py" \
    -i "tests/test_auth.py"
```

## Performance

- The tool uses Python's pathlib for efficient path handling
- .gitignore patterns are parsed once and cached
- Directory traversal is optimized to skip excluded paths early
- When using uv for package management, dependency installation is significantly faster than pip

## Known Limitations

- Wildcard patterns (*) are only supported at the file level, not for intermediate directories
- Binary files are skipped when including file contents
- Very large repositories might take longer to process
