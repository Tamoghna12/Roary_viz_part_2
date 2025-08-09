import pytest
import os
import pandas as pd
from unittest.mock import MagicMock, mock_open, patch
from io import StringIO
from roary_visualizer.utils.file_handler import FileHandler
from roary_visualizer.middleware.error_handler import ValidationError

def test_file_handler_initialization(temp_dir):
    """Test FileHandler initialization"""
    handler = FileHandler(temp_dir)
    assert handler.temp_dir == temp_dir
    assert os.path.exists(temp_dir)

def test_save_uploaded_file(file_handler):
    """Test saving uploaded file"""
    mock_file = MagicMock()
    mock_file.read.return_value = b"test content"
    
    file_path = file_handler.save_uploaded_file(mock_file, "test.txt")
    
    assert os.path.exists(file_path)
    with open(file_path, 'rb') as f:
        assert f.read() == b"test content"

def test_save_uploaded_file_error(file_handler):
    """Test error handling when saving file fails"""
    mock_file = MagicMock()
    mock_file.read.side_effect = IOError("Failed to read file")
    
    with pytest.raises(IOError):
        file_handler.save_uploaded_file(mock_file, "test.txt")

def test_read_summary_statistics(file_handler, mock_roary_files):
    """Test reading summary statistics file"""
    df = file_handler.read_summary_statistics(mock_roary_files['stats_path'])
    
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert 'Category' in df.columns
    assert 'Count' in df.columns

def test_read_presence_absence_matrix(file_handler, mock_roary_files):
    """Test reading presence/absence matrix"""
    df = file_handler.read_presence_absence_matrix(mock_roary_files['matrix_path'])
    
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    # Check that matrix contains only 0s and 1s
    assert set(df.values.flatten().tolist()).issubset({0, 1})

def test_read_tree_file(file_handler, mock_roary_files):
    """Test reading tree file"""
    tree = file_handler.read_tree_file(mock_roary_files['tree_path'])
    
    assert tree is not None
    # Check that we can get terminal nodes (genome names)
    terminals = [tip.name for tip in tree.get_terminals()]
    assert len(terminals) > 0

def test_validate_file_extension(file_handler):
    """Test file extension validation"""
    assert file_handler.validate_file("test.txt", ".txt")
    assert file_handler.validate_file("test.csv", ".csv")
    assert not file_handler.validate_file("test.pdf", ".txt")
    assert file_handler.validate_file("TEST.TXT", ".txt")  # Case insensitive

def test_cleanup(temp_dir):
    """Test cleanup functionality"""
    handler = FileHandler(temp_dir)
    test_file = os.path.join(temp_dir, "test.txt")
    
    # Create a test file
    with open(test_file, 'w') as f:
        f.write("test")
    
    assert os.path.exists(test_file)
    handler.cleanup()
    assert not os.path.exists(temp_dir)

def test_context_manager(temp_dir):
    """Test FileHandler as context manager"""
    test_file = os.path.join(temp_dir, "test.txt")
    
    with FileHandler(temp_dir) as handler:
        with open(test_file, 'w') as f:
            f.write("test")
        assert os.path.exists(test_file)
    
    # After context manager exits, directory should be cleaned up
    assert not os.path.exists(temp_dir)