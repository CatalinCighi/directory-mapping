# Directory Mapping Script

This script maps the structure of a directory while respecting `.gitignore` rules, and outputs the mapped structure in the specified format (`JSON`, `YAML`, or `XML`).

## Features
- Automatically parses `.gitignore` to exclude ignored files and directories.
- Outputs directory structure in `JSON`, `YAML`, or `XML` formats.
- Saves the output to the user's home directory with the filename `structure.<format>`.

## Requirements
- Python 3.x
- Required Python libraries:
  - `pathspec`
  - `yaml`

Install the dependencies using:
```bash
pip install pathspec pyyaml
```

## Usage
### Command-line Arguments
- `--format`: Specifies the output format. Accepted values are `json`, `yaml`, or `xml`. Defaults to `json`.

### Example
```bash
python script.py --format yaml
```
This will:
1. Map the current working directory.
2. Respect `.gitignore` rules in the directory.
3. Save the directory structure as a `YAML` file in the user's home directory.

## Output
The script saves the mapped directory structure as `structure.<format>` in the home directory of the user.

### Sample Output (JSON)
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

## Error Handling
- If `.gitignore` is not found, the script proceeds without applying ignore rules.
- Any errors during saving the output are logged to the console.

## Logs
The script logs progress and issues to the console for transparency during execution.

## License
This script is open-source and available for modification and redistribution.

