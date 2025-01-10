# Enhanced File Merger

A Python script to merge code files into a single file. It can be used for saving, sharing, reviewing source code, or for AI analysis.

## Features

- 💻 **Flexible Configuration**: Customizable with a YAML-based configuration file
- 🌏 **Multi-Encoding Support**: Supports multiple encodings such as UTF-8, Shift-JIS, EUC-JP
- 📝 **Metadata Output**: Includes file information and timestamps
- 🔍 **Line Number Display**: Optionally add line numbers
- ⚡ **Customizable Exclusion Patterns**: Flexibly exclude unnecessary files
- 📊 **Detailed Summary**: Displays statistics of the processing results

## Installation

### Recommended Installation with pipx

1. Install pipx:
```bash
# Install Python first if it's not already installed
python -m pip install --user pipx
python -m pipx ensurepath
```

2. Clone this repository:
```bash
git clone https://github.com/yourusername/enhanced-file-merger.git
cd enhanced-file-merger
```

3. Install enhanced-file-merger:
```bash
pipx install .
```

4. Copy the exclusion list to your home directory:
```bash
cp .enhanced-file-merger-config.yaml.example ~/.enhanced-file-merger-config.yaml
```

After installation, the `merge-files` command will be available globally.

### Uninstallation

To uninstall if installed with pipx, use the following command:

```bash
pipx uninstall enhanced-file-merger
```

## Basic Usage

The simplest usage:
```bash
merge-files source_directory output_filename
```

Example:
```bash
merge-files ./src output.txt
```

## Advanced Usage

### Using a Custom Configuration File

Using a custom configuration file:
```bash
merge-files ./src output.txt --config my_custom_config.yaml
```

### Specifying Additional Exclusion Patterns

```bash
merge-files ./src output.txt --exclude "*.log" --exclude "temp*"
```

### Specifying Encoding

```bash
merge-files ./src output.txt --encoding shift-jis
```

### Other Options

```bash
# Run without summary
merge-files ./src output.txt --no-summary

# Display only errors (silent mode)
merge-files ./src output.txt --silent
```

## Configuration File

The configuration file can customize the following items:

```yaml
output_format:
  add_line_numbers: true    # Display line numbers
  show_file_count: true     # Display file count
  show_summary: true        # Display summary
  separator_line: "="       # Separator character
  separator_length: 80      # Separator line length

exclude_patterns:
  directories:              # Exclude directories
    - node_modules
    - __pycache__
    - .git
  
  files:                    # Exclude files
    - "*.json"
    - "*.pyc"
    - "*.exe"
    
  system_files:             # Exclude system files
    - ".DS_Store"
    - "Thumbs.db"

encoding:
  default: "utf-8"          # Default encoding
  fallback:                 # Fallback encodings
    - "cp932"
    - "shift-jis"
    - "euc-jp"

output:
  add_timestamp: true       # Add timestamp
  timestamp_format: "%Y-%m-%d %H:%M:%S"
  line_ending: "auto"       # Line ending (auto/lf/crlf)
```

## Output Example

```text
MERGED SOURCE CODE FILES
================================================================================
Project Directory: /absolute/path/to/src
Merge Started: 2025-01-09 10:00:00
================================================================================

### FILE: lib/utils.py
================================================================================
METADATA:
  Modified: 2025-01-09 10:00:00
  Size: 1234 bytes
  Full path: /absolute/path/to/src/lib/utils.py
================================================================================

   1 | def hello():
   2 |     print("Hello, World!")
   3 | 
   4 | if __name__ == "__main__":
   5 |     hello()

--------------------------------------------------------------------------------
```

## Running Tests

Developers can run unit tests using `poetry`.

```bash
poetry install
poetry run pytest
```

## Notes

1. **Large Files**: Be mindful of memory usage
2. **Encoding**: Automatic detection is not perfect
3. **Exclusion Patterns**: Ensure no unintended files are included

## Troubleshooting

### Common Issues and Solutions

1. **UnicodeDecodeError occurs**
   - Specify the appropriate encoding with the `--encoding` option
   - Check the fallback encodings in .enhanced-file-merger-config.yaml

2. **Unintended files are included**
   - Check the exclusion patterns in .enhanced-file-merger-config.yaml
   - Specify additional exclusion patterns with the `--exclude` option

3. **Out of memory**
   - Split the directory to be processed
   - Add unnecessary files to the exclusion patterns

## License

MIT License - See the [LICENSE](LICENSE) file for details

## Contribution

1. Fork this repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

## Acknowledgements

- This project is supported by many open-source software
- Thanks to all contributors