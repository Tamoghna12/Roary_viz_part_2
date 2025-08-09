import pytest
import pandas as pd
import numpy as np
from roary_visualizer.core.data_processor import DataProcessor
from roary_visualizer.models.data_models import VisualizationConfig

@pytest.fixture
def sample_data():
    """Create sample gene presence/absence matrix"""
    # Create a sample 10x5 matrix (10 genes, 5 genomes)
    data = np.random.choice([0, 1], size=(10, 5), p=[0.3, 0.7])
    return pd.DataFrame(
        data,
        columns=[f'genome_{i}' for i in range(5)],
        index=[f'gene_{i}' for i in range(10)]
    )

@pytest.fixture
def data_processor():
    """Create DataProcessor instance with default config"""
    config = VisualizationConfig()
    return DataProcessor(config)

def test_process_gene_distribution(data_processor, sample_data):
    """Test gene distribution calculation"""
    distribution = data_processor.process_gene_distribution(sample_data)
    
    assert distribution.total_genes == 10
    assert isinstance(distribution.core_genes, int)
    assert isinstance(distribution.softcore_genes, int)
    assert isinstance(distribution.shell_genes, int)
    assert isinstance(distribution.cloud_genes, int)
    assert isinstance(distribution.genes_per_genome, float)
    
    # Check that all genes are accounted for
    total = (distribution.core_genes + distribution.softcore_genes + 
             distribution.shell_genes + distribution.cloud_genes)
    assert total == distribution.total_genes

def test_calculate_gene_frequencies(data_processor, sample_data):
    """Test gene frequency calculation"""
    freq_df = data_processor.calculate_gene_frequencies(sample_data)
    
    assert isinstance(freq_df, pd.DataFrame)
    assert len(freq_df) == len(sample_data)
    assert all(col in freq_df.columns for col in ['Gene', 'Present_in_genomes', 'Percentage'])
    assert all(freq_df['Percentage'] <= 100)
    assert all(freq_df['Percentage'] >= 0)

def test_generate_rarefaction_data(data_processor, sample_data):
    """Test rarefaction curve data generation"""
    genome_counts, gene_counts = data_processor.generate_rarefaction_data(
        sample_data, num_permutations=10
    )
    
    assert len(genome_counts) == sample_data.shape[1]
    assert len(gene_counts) == len(genome_counts)
    assert all(isinstance(x, (int, float)) for x in gene_counts)
    assert all(x <= sample_data.shape[0] for x in gene_counts)

def test_analyze_gene_patterns(data_processor, sample_data):
    """Test gene pattern analysis"""
    # Test different pattern types
    pattern_types = ['rare', 'common', 'variable', 'all']
    
    for pattern_type in pattern_types:
        result = data_processor.analyze_gene_patterns(sample_data, pattern_type)
        
        assert isinstance(result, pd.DataFrame)
        assert all(col in result.columns for col in ['Gene', 'Present_in_genomes', 'Percentage'])
        assert len(result) <= len(sample_data)
        
        if pattern_type == 'rare':
            assert all(result['Percentage'] <= 10)
        elif pattern_type == 'common':
            assert all(result['Percentage'] >= 90)
        elif pattern_type == 'variable':
            assert all((result['Percentage'] > 30) & (result['Percentage'] < 70))