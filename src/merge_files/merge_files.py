#!/usr/bin/env python

"""
Enhanced File Merger
Usage:
  python merge_files.py <directory_path> <output_filename> [--config CONFIG_PATH]

Note: Place `.enhanced-file-merger-config.yaml` in the project root or specify a custom path with --config.

Options:
  --config CONFIG_PATH    Path to configuration file (default: .enhanced-file-merger-config.yaml)
  --encoding ENCODING     Override default encoding
  --exclude PATTERN      Additional exclude pattern
  --no-summary          Disable summary output
  --silent              Suppress all output except errors
"""

import os
import sys
import fnmatch
import datetime
import yaml
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional

class FileMerger:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(Path.home(), ".enhanced-file-merger-config.yaml")
        self.config = self._load_config(config_path)
        self.setup_logging()

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logging.warning(f"Config file not found at {config_path}, using defaults")
            return self._get_default_config()
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            sys.exit(1)

    def _get_default_config(self) -> Dict:
        """Return default configuration"""
        return {
            "output_format": {
                "add_line_numbers": True,
                "show_file_count": True,
                "show_summary": True,
                "separator_line": "=",
                "separator_length": 80
            },
            "exclude_patterns": {
                "directories": ["node_modules", "__pycache__", ".git"],
                "files": ["*.pyc", "*.pyo", "*.exe"],
                "system_files": [".DS_Store", "Thumbs.db"]
            },
            "encoding": {
                "default": "utf-8",
                "fallback": ["cp932", "shift-jis", "euc-jp"]
            },
            "output": {
                "add_timestamp": True,
                "timestamp_format": "%Y-%m-%d %H:%M:%S",
                "line_ending": "auto",
                "max_total_size_kb": 300  # 300 KB
            }
        }

    def setup_logging(self):
        """Set up logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def should_exclude(self, filepath: str) -> bool:
        """Check if the file should be excluded based on patterns from the config."""
        path_parts = Path(filepath).parts
        filename = os.path.basename(filepath)

        # Check directory patterns
        for dir_pattern in self.config["exclude_patterns"]["directories"]:
            if dir_pattern in path_parts:
                return True

        # Check file patterns
        for pattern in (self.config["exclude_patterns"]["files"] + 
                        self.config["exclude_patterns"]["system_files"]):
            if fnmatch.fnmatch(filename, pattern):
                return True

        return False

    def read_file_with_fallback(self, filepath: str) -> Optional[str]:
        """Attempt to read file with multiple encodings"""
        encodings = [self.config["encoding"]["default"]] + \
                   self.config["encoding"]["fallback"]
        
        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logging.error(f"Error reading {filepath}: {e}")
                return None
        
        logging.error(f"Failed to read {filepath} with all encodings")
        return None

    def merge_files(self, input_dir: str, output_file: str) -> int:
        """Merge files from input_dir into output_file, respecting size limits and exclusion patterns."""
        max_size = self.config["output"]["max_total_size_kb"] * 1024  # Convert KB to bytes

        # Pre-scan files
        candidate_files = []
        total_size = 0
        
        for root, _, files in os.walk(input_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if not self.should_exclude(file_path):
                    file_size = os.path.getsize(file_path)
                    if total_size + file_size > max_size:
                        logging.warning("Total size limit exceeded, aborting merge.")
                        return 0
                    total_size += file_size
                    candidate_files.append(file_path)

        total_size = sum(os.path.getsize(f) for f in candidate_files)
        print(f"Total size: {total_size}")
        print(f"Max size: {max_size}")
        if total_size > max_size:
            logging.warning("Total size limit exceeded, aborting merge.")
            return 0

        total_files = 0
        try:
            with open(output_file, 'w', encoding='utf-8') as outfile:
                self._write_header(outfile, input_dir, datetime.datetime.now())

                for file_path in candidate_files:
                    if not self._process_file(file_path, input_dir, outfile):
                        continue
                    total_files += 1

                if self.config["output_format"]["show_summary"]:
                    self._write_summary(outfile, total_files, datetime.datetime.now())

            return total_files

        except Exception as e:
            logging.error(f"Error during merge: {e}")
            return 0

    def merge_files_from_list(self, file_list: List[str], output_filename: str) -> int:
        """Merge files from the specified file list"""
        total_files = 0
        start_time = datetime.datetime.now()

        with open(output_filename, 'w', encoding=self.config["encoding"]["default"]) as out:
            # Write header information
            self._write_header(out, "file list", start_time)

            # Process files
            for filepath in file_list:
                if self._process_file(filepath, "", out):
                    total_files += 1

            # Write summary
            if self.config["output_format"]["show_summary"]:
                self._write_summary(out, total_files, start_time)

        return total_files

    def _walk_directory(self, directory: str):
        """Walk through directory and list files"""
        for root, dirs, files in os.walk(directory):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if not self.should_exclude(os.path.join(root, d))]
            
            for filename in files:
                filepath = os.path.join(root, filename)
                if not self.should_exclude(filepath):
                    yield filepath

    def _write_header(self, out, directory: str, start_time: datetime):
        """Write header information"""
        separator = "=" * self.config["output_format"]["separator_length"]
        out.write("MERGED SOURCE CODE FILES\n")
        out.write(f"{separator}\n")
        out.write(f"Project Directory: {os.path.abspath(directory)}\n")
        out.write(f"Merge Started: {start_time.strftime(self.config['output']['timestamp_format'])}\n")
        out.write(f"{separator}\n\n")

    def _process_file(self, filepath: str, base_dir: str, out) -> bool:
        """Process a single file"""
        try:
            content = self.read_file_with_fallback(filepath)
            if content is None:
                return False

            separator = "=" * self.config["output_format"]["separator_length"]
            abs_path = os.path.abspath(filepath)
            rel_path = os.path.relpath(filepath, base_dir)
            file_stat = os.stat(filepath)
            modified_time = datetime.datetime.fromtimestamp(file_stat.st_mtime)

            # Write file header
            out.write(f"### FILE: {rel_path}\n")
            out.write(f"{separator}\n")
            out.write("METADATA:\n")
            out.write(f"  Modified: {modified_time.strftime(self.config['output']['timestamp_format'])}\n")
            out.write(f"  Size: {file_stat.st_size} bytes\n")
            out.write(f"  Full path: {abs_path}\n")
            out.write(f"{separator}\n\n")

            # Write content with line numbers
            lines = content.splitlines()
            for i, line in enumerate(lines, 1):
                out.write(f"{i:4d} | {line}\n")
            out.write("\n")

            return True

        except Exception as e:
            logging.error(f"Error processing {filepath}: {e}")
            return False

    def _write_summary(self, out, total_files: int, start_time: datetime):
        """Write summary information"""
        separator = "=" * self.config["output_format"]["separator_length"]
        end_time = datetime.datetime.now()
        out.write(f"{separator}\n")
        out.write("SUMMARY\n")
        out.write(f"{separator}\n")
        out.write(f"Files processed: {total_files}\n")
        out.write(f"Duration: {(end_time - start_time).total_seconds():.2f} seconds\n")
        out.write(f"Completed: {end_time.strftime(self.config['output']['timestamp_format'])}\n")
        out.write(f"{separator}\n")

def main():
    parser = argparse.ArgumentParser(description='Enhanced File Merger')
    parser.add_argument('directory', help='Source directory path')
    parser.add_argument('output', help='Output file path')
    parser.add_argument('--config', help='Path to config file')
    parser.add_argument('--encoding', help='Override default encoding')
    parser.add_argument('--exclude', action='append', help='Additional exclude patterns')
    parser.add_argument('--no-summary', action='store_true', help='Disable summary output')
    parser.add_argument('--silent', action='store_true', help='Suppress non-error output')

    args = parser.parse_args()

    # Initialize merger
    merger = FileMerger(args.config)

    # Override with command line arguments
    if args.encoding:
        merger.config["encoding"]["default"] = args.encoding
    if args.exclude:
        merger.config["exclude_patterns"]["files"].extend(args.exclude)
    if args.no_summary:
        merger.config["output_format"]["show_summary"] = False
    if args.silent:
        logging.getLogger().setLevel(logging.ERROR)

    # Merge files
    try:
        total_files = merger.merge_files(args.directory, args.output)
        if not args.silent:
            print(f'Successfully merged {total_files} files into {args.output}')
    except Exception as e:
        logging.error(f"Error during merge: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()