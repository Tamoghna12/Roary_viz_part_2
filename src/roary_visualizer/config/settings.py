import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings and configuration"""
    
    # Application paths
    BASE_DIR = Path(__file__).parent.parent.parent.parent
    TEMP_DIR = os.getenv('TEMP_DIR', os.path.join(str(Path.home()), '.roary_visualizer', 'tmp'))
    
    # File settings
    ALLOWED_EXTENSIONS = {
        'summary_statistics': '.txt',
        'gene_presence_absence': '.csv',
        'tree': '.newick'
    }
    
    MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB
    
    # Visualization defaults
    DEFAULT_CONFIG = {
        'core_threshold': 0.99,
        'softcore_threshold': 0.95,
        'shell_threshold': 0.15,
        'cluster_rows': True,
        'cluster_cols': False,
        'log_scale': False
    }
    
    # Performance settings
    MAX_GENES_DISPLAY = 5000
    DEFAULT_PERMUTATIONS = 50
    
    # Analytics settings
    ENABLE_ANALYTICS = os.getenv('ENABLE_ANALYTICS', 'false').lower() == 'true'
    
    @classmethod
    def get_temp_dir(cls) -> str:
        """Get temporary directory path, creating if necessary
        
        Returns:
            str: Path to temporary directory
        """
        os.makedirs(cls.TEMP_DIR, exist_ok=True)
        return cls.TEMP_DIR
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Get configuration dictionary
        
        Returns:
            Dict[str, Any]: Configuration dictionary
        """
        return cls.DEFAULT_CONFIG.copy()
    
    @classmethod
    def validate_file_size(cls, file_size: int) -> bool:
        """Validate file size against maximum allowed
        
        Args:
            file_size: Size of file in bytes
            
        Returns:
            bool: True if file size is within limits
        """
        return file_size <= cls.MAX_UPLOAD_SIZE