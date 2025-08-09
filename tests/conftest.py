import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from pathlib import Path

from roary_visualizer.models.data_models import VisualizationConfig
from roary_visualizer.utils.file_handler import FileHandler

@pytest.fixture(scope="session")
def temp_dir():
    """Create a temporary directory for test files"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup after tests
    if os.path.exists(temp_dir):
        for file in Path(temp_dir).glob("*"):
            file.unlink()
        os.rmdir(temp_dir)

@pytest.fixture
def file_handler(temp_dir):
    """Create a FileHandler instance for tests"""
    return FileHandler(temp_dir)

@pytest.fixture
def sample_presence_absence_matrix():
    """Create a sample gene presence/absence matrix"""
    data = np.random.choice([0, 1], size=(20, 10), p=[0.3, 0.7])
    return pd.DataFrame(
        data,
        columns=[f'genome_{i}' for i in range(10)],
        index=[f'gene_{i}' for i in range(20)]
    )

@pytest.fixture
def sample_summary_stats():
    """Create sample summary statistics"""
    return pd.DataFrame({
        'Category': ['Core genes', 'Soft-core', 'Shell', 'Cloud'],
        'Count': [100, 50, 30, 20],
        'Percentage': [50, 25, 15, 10]
    })

@pytest.fixture
def visualization_config():
    """Create a default visualization configuration"""
    return VisualizationConfig(
        core_threshold=0.99,
        softcore_threshold=0.95,
        shell_threshold=0.15,
        cluster_rows=True,
        cluster_cols=False,
        log_scale=False
    )

@pytest.fixture
def mock_roary_files(temp_dir, sample_presence_absence_matrix, sample_summary_stats):
    """Create mock Roary output files for testing"""
    # Create presence/absence matrix file
    matrix_path = os.path.join(temp_dir, "gene_presence_absence.csv")
    sample_presence_absence_matrix.to_csv(matrix_path)
    
    # Create summary statistics file
    stats_path = os.path.join(temp_dir, "summary_statistics.txt")
    sample_summary_stats.to_csv(stats_path, sep='\t', index=False)
    
    # Create a dummy tree file
    tree_path = os.path.join(temp_dir, "accessory_binary_genes.fa.newick")
    with open(tree_path, 'w') as f:
        f.write("(genome_1:0.1,(genome_2:0.2,genome_3:0.3):0.4);")
    
    return {
        'matrix_path': matrix_path,
        'stats_path': stats_path,
        'tree_path': tree_path
    }