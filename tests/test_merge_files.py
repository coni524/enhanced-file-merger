import pytest
import os
import tempfile
import yaml
from merge_files import FileMerger
from unittest.mock import patch
from merge_files.merge_files import main  # Add this import

@pytest.fixture
def temp_dir():
    """Fixture to create a temporary directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def sample_config():
    """Fixture to provide test configuration"""
    return {
        "output_format": {
            "add_line_numbers": True,
            "show_file_count": True,
            "show_summary": True,
            "separator_line": "=",
            "separator_length": 80
        },
        "exclude_patterns": {
            "directories": ["node_modules", "__pycache__"],
            "files": ["*.pyc", "*.tmp"],
            "system_files": [".DS_Store"]
        },
        "encoding": {
            "default": "utf-8",
            "fallback": ["cp932", "shift-jis"]
        },
        "output": {
            "add_timestamp": True,
            "timestamp_format": "%Y-%m-%d %H:%M:%S",
            "line_ending": "auto",
            "max_total_size_kb": 200  # 200KB
        }
    }

@pytest.fixture
def config_file(temp_dir, sample_config):
    """Fixture to create configuration file"""
    config_path = os.path.join(temp_dir, "test_config.yaml")
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(sample_config, f)
    return config_path

@pytest.fixture
def merger(config_file):
    """Fixture to provide FileMerger instance"""
    return FileMerger(config_file)

def create_test_files(base_dir):
    """Helper function to create test file structure"""
    # Create regular Python file
    with open(os.path.join(base_dir, "test1.py"), 'w', encoding='utf-8') as f:
        f.write("def test():\n    return True")
    
    # .pyc file that should be excluded
    with open(os.path.join(base_dir, "test1.pyc"), 'w', encoding='utf-8') as f:
        f.write("compiled python")
    
    # Subdirectory and files
    os.makedirs(os.path.join(base_dir, "subdir"), exist_ok=True)
    with open(os.path.join(base_dir, "subdir", "test2.py"), 'w', encoding='utf-8') as f:
        f.write("def another_test():\n    return False")
    
    # Directory that should be excluded
    os.makedirs(os.path.join(base_dir, "node_modules"), exist_ok=True)
    with open(os.path.join(base_dir, "node_modules", "package.js"), 'w', encoding='utf-8') as f:
        f.write("console.log('test')")

def test_config_loading(merger, sample_config):
    """Test configuration file loading"""
    # Check basic configuration values
    assert merger.config["output_format"]["separator_line"] == sample_config["output_format"]["separator_line"]
    assert merger.config["encoding"]["default"] == sample_config["encoding"]["default"]

def test_should_exclude(merger):
    """Test exclusion pattern determination"""
    # Files that should be excluded
    assert merger.should_exclude("test.pyc")
    assert merger.should_exclude("node_modules/test.js")
    # Files that should not be excluded
    assert not merger.should_exclude("test.py")
    assert not merger.should_exclude("src/test.js")

def test_read_file_with_fallback(merger, temp_dir):
    """Test file reading with encoding fallback"""
    test_file = os.path.join(temp_dir, "test.txt")
    test_content = "Hello, World!"
    
    # Test UTF-8 file
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    assert merger.read_file_with_fallback(test_file) == test_content

def test_merge_files(merger, temp_dir):
    """Integration test for file merging process"""
    # Create test files
    create_test_files(temp_dir)
    
    output_file = os.path.join(temp_dir, "output.txt")
    total_files = merger.merge_files(temp_dir, output_file)
    
    # Verify the correct number of files were processed
    assert total_files == 3  # test1.py and subdir/test2.py, test_config.yaml
    
    # Verify the output file was created
    assert os.path.exists(output_file)
    
    # Verify the content of the output file
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "MERGED SOURCE CODE FILES" in content
        assert "Project Directory:" in content
        assert "FILE:" in content
        assert "METADATA:" in content
        assert "Modified:" in content
        assert "Size:" in content
        assert "1 |" in content  # line numbers check
        assert "def test():" in content
        assert "def another_test():" in content
        assert "compiled python" not in content  # Verify excluded file content is not present

def test_error_handling(merger, temp_dir):
    """Test error handling"""
    non_existent_file = os.path.join(temp_dir, "non_existent.txt")
    result = merger.read_file_with_fallback(non_existent_file)
    assert result is None

def test_encoding_fallback(merger, temp_dir):
    """Test encoding fallback mechanism"""
    test_file = os.path.join(temp_dir, "shift_jis.txt")
    test_content = "こんにちは"
    
    # Create file in SHIFT-JIS
    with open(test_file, 'w', encoding='shift-jis') as f:
        f.write(test_content)
    
    # Verify the read content is correct
    assert merger.read_file_with_fallback(test_file) == test_content

def test_file_size_limit(merger, temp_dir):
    """Test file size limit"""
    # Create test files
    create_test_files(temp_dir)
    
    # Add large file
    large_file = os.path.join(temp_dir, "large_file.txt")
    with open(large_file, 'w', encoding='utf-8') as f:
        f.write("A" * 300 * 1024)  # 300KB file
    
    output_file = os.path.join(temp_dir, "output.txt")
    total_files = merger.merge_files(temp_dir, output_file)
    
    # Verify the process was aborted due to file size limit
    assert total_files == 0
    assert not os.path.exists(output_file)

def test_command_line_args():
    """Test command line argument processing"""
    with patch('sys.argv', ['merge-files', 'src', 'output.txt', '--encoding', 'utf-8', '--exclude', '*.log']):
        with patch('merge_files.FileMerger.merge_files') as mock_merge:
            main()
            mock_merge.assert_called_once()

def test_merge_files_from_list(merger, temp_dir):
    """Test merging from a list of files"""
    # Create test files
    file1 = os.path.join(temp_dir, "test1.txt")
    file2 = os.path.join(temp_dir, "test2.txt")
    
    with open(file1, 'w') as f:
        f.write("content1")
    with open(file2, 'w') as f:
        f.write("content2")
    
    output_file = os.path.join(temp_dir, "output.txt")
    total_files = merger.merge_files_from_list([file1, file2], output_file)
    
    assert total_files == 2
    assert os.path.exists(output_file)
    
    # Verify the new output format
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "MERGED SOURCE CODE FILES" in content
        assert "Project Directory:" in content
        assert "FILE:" in content
        assert "METADATA:" in content
        assert "content1" in content
        assert "content2" in content
        assert "SUMMARY" in content

def test_error_handling_extended(merger, temp_dir):
    """Test additional error cases"""
    # Non-existent directory
    assert merger.merge_files("/nonexistent", "output.txt") == 0
    
    # Test in a directory without write permissions
    if os.name != 'nt':  # Unix systems
        readonly_dir = os.path.join(temp_dir, "readonly")
        os.mkdir(readonly_dir, mode=0o444)
        output_file = os.path.join(readonly_dir, "output.txt")
        assert merger.merge_files(temp_dir, output_file) == 0

def test_invalid_config():
    """Test handling of invalid configuration file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as f:
        f.write("invalid: yaml: content}}")
        f.flush()
        with pytest.raises(SystemExit):
            FileMerger(f.name)

def test_walk_directory(merger, temp_dir):
    """Test directory walking functionality"""
    # Create complex directory structure
    os.makedirs(os.path.join(temp_dir, "dir1/dir2"))
    os.makedirs(os.path.join(temp_dir, "node_modules"))
    
    with open(os.path.join(temp_dir, "dir1/test1.py"), 'w') as f:
        f.write("test1")
    with open(os.path.join(temp_dir, "dir1/dir2/test2.py"), 'w') as f:
        f.write("test2")
    with open(os.path.join(temp_dir, "node_modules/ignored.js"), 'w') as f:
        f.write("ignored")
        
    files = list(merger._walk_directory(temp_dir))
    # Adjust the expected number of files to account for the config file
    assert len(files) == 3
    assert any("test1.py" in f for f in files)
    assert any("test2.py" in f for f in files)
    assert any("test_config.yaml" in f for f in files)