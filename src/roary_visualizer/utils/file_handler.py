import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Optional, List
import pandas as pd
from Bio import Phylo
from io import StringIO

class FileHandler:
    """Handles file operations for Roary output files"""
    
    def __init__(self, temp_dir: Optional[str] = None):
        """Initialize FileHandler with optional temporary directory
        
        Args:
            temp_dir: Optional path to temporary directory
        """
        self.temp_dir = temp_dir or tempfile.mkdtemp()
        self._ensure_temp_dir()
    
    def _ensure_temp_dir(self) -> None:
        """Ensure temporary directory exists"""
        Path(self.temp_dir).mkdir(parents=True, exist_ok=True)
    
    def save_uploaded_file(self, uploaded_file, filename: str) -> str:
        """Save uploaded file to temporary directory
        
        Args:
            uploaded_file: Streamlit uploaded file object
            filename: Name to save the file as
            
        Returns:
            str: Path to saved file
        
        Raises:
            IOError: If file cannot be saved
        """
        try:
            file_path = os.path.join(self.temp_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.read())
            return file_path
        except Exception as e:
            raise IOError(f"Failed to save file {filename}: {str(e)}")
    
    def read_summary_statistics(self, file_path: str) -> pd.DataFrame:
        """Read Roary summary statistics file
        
        Args:
            file_path: Path to summary statistics file
            
        Returns:
            pd.DataFrame: Processed summary statistics
            
        Raises:
            ValueError: If file format is invalid
        """
        try:
            return pd.read_csv(file_path, sep='\t')
        except Exception as e:
            raise ValueError(f"Invalid summary statistics file format: {str(e)}")
    
    def read_presence_absence_matrix(self, file_path: str) -> pd.DataFrame:
        """Read gene presence/absence matrix
        
        Args:
            file_path: Path to gene presence/absence CSV
            
        Returns:
            pd.DataFrame: Processed presence/absence matrix
            
        Raises:
            ValueError: If file format is invalid
        """
        try:
            roary = pd.read_csv(file_path, low_memory=False)
            gene_pa = roary.iloc[:, 14:]  # Columns after 14 contain presence/absence data
            return gene_pa.notna().astype(int)  # Convert to binary format
        except Exception as e:
            raise ValueError(f"Invalid gene presence/absence matrix format: {str(e)}")
    
    def read_tree_file(self, file_path: str) -> Optional[object]:
        """Read phylogenetic tree file
        
        Args:
            file_path: Path to Newick tree file
            
        Returns:
            Optional[object]: Phylo tree object if successful, None otherwise
        """
        try:
            return Phylo.read(file_path, 'newick')
        except Exception as e:
            return None
    
    def validate_file(self, filename: str, expected_extension: str) -> bool:
        """Validate file extension
        
        Args:
            filename: Name of file to validate
            expected_extension: Expected file extension
            
        Returns:
            bool: True if file has correct extension
        """
        return filename.lower().endswith(expected_extension)
    
    def cleanup(self) -> None:
        """Clean up temporary directory"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        self.cleanup()