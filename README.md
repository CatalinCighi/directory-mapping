# dirmap - Directory Mapping Tool

A Python package that maps the structure of a directory while respecting `.gitignore` rules and outputs the mapped structure in your chosen format (JSON, YAML, or XML). By default, it also trims the structure to exclude common unwanted patterns (like venv, .git, etc.).


## Features

- Maps directory structure in JSON, YAML, or XML formats
- Automatically respects `.gitignore` rules
- Automatically trims structures to exclude common patterns (like .git, venv, etc.)
- Configurable exclude patterns via JSON configuration files
- Simple command-line interface
- Can be used programmatically in other Python projects

## Usage

### Command Line

```bash
# Map the current directory in JSON format (default)
# This will use the default exclude patterns to trim the structure
dirmap

# Map a specific directory in YAML format
dirmap --directory /path/to/your/directory --format yaml

# Map without trimming (include everything)
dirmap --no-trim

# Map with a custom exclude patterns configuration
dirmap --exclude-config my_exclude_patterns.json

# Specify custom output path
dirmap --output /path/to/output/structure.json

# Trim an existing structure file with default exclude patterns
dirmap --trim-file structure.json --output trimmed_structure.json

# Trim an existing structure file with custom exclude patterns
dirmap --trim-file structure.json --exclude-config my_exclude_patterns.json

# Show verbose output
dirmap --verbose

# Show help
dirmap --help
```

### As a Python Module

```python
from dirmap import mapper

# Map the current directory (with default trimming)
output_path = mapper.create_map()

# Map a specific directory in YAML format
output_path = mapper.create_map(directory="/path/to/your/directory", output_format="yaml")

# Map without trimming
output_path = mapper.create_map(no_trim=True)

# Map with custom exclude patterns configuration
output_path = mapper.create_map(exclude_config="my_exclude_patterns.json")

# Enable verbose logging
output_path = mapper.create_map(verbose=True)
```

## Configuration

The package uses a JSON configuration file to specify which patterns to exclude when trimming. A default configuration file is included with the package, but you can provide your own.

### Default Exclude Patterns

The default configuration excludes common patterns such as:
- `.git` directories
- Virtual environments (`venv`)
- Python cache (`__pycache__`)
- Package directories (`site-packages`)
- And other common patterns

### Custom Exclude Patterns

You can create your own JSON configuration file with the following structure:

```json
{
  "exclude_patterns": [
    ".git",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "*.egg-info"
  ]
}
```

## Output Examples

### JSON Format

```json
{
    "/path/to/dir": {
        "files": ["file1.txt", "file2.py"],
        "dirs": ["subdir1", "subdir2"]
    },
    "/path/to/dir/subdir1": {
        "files": ["file3.log"],
        "dirs": []
    }
}
```

### YAML Format

```yaml
/path/to/dir:
  files:
  - file1.txt
  - file2.py
  dirs:
  - subdir1
  - subdir2
/path/to/dir/subdir1:
  files:
  - file3.log
  dirs: []
```

### XML Format

```xml
<structure>
  <directory path="/path/to/dir">
    <files>
      <file>file1.txt</file>
      <file>file2.py</file>
    </files>
    <subdirectories>
      <directory>subdir1</directory>
      <directory>subdir2</directory>
    </subdirectories>
  </directory>
  <directory path="/path/to/dir/subdir1">
    <files>
      <file>file3.log</file>
    </files>
    <subdirectories>
    </subdirectories>
  </directory>
</structure>
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.