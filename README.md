# dirmap - Directory Mapping Tool

A Python package that maps the structure of a directory while respecting `.gitignore` rules and outputs the mapped structure in your chosen format (JSON, YAML, or XML).

## Installation

You can install the package directly from GitHub:

```bash
# Install directly from the repository
pip install git+https://github.com/yourusername/dirmap.git

# Or after cloning the repository
git clone https://github.com/yourusername/dirmap.git
cd dirmap
pip install .
```

## Features

- Maps directory structure in JSON, YAML, or XML formats
- Automatically respects `.gitignore` rules
- Simple command-line interface
- Can be used programmatically in other Python projects

## Usage

### Command Line

```bash
# Map the current directory in JSON format (default)
dirmap

# Map a specific directory in YAML format
dirmap --directory /path/to/your/directory --format yaml

# Show verbose output
dirmap --verbose

# Show help
dirmap --help
```

### As a Python Module

```python
from dirmap import mapper

# Map the current directory
output_path = mapper.create_map()

# Map a specific directory in YAML format
output_path = mapper.create_map(directory="/path/to/your/directory", output_format="yaml")

# Enable verbose logging
output_path = mapper.create_map(verbose=True)
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