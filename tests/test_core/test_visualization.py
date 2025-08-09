import pytest
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from roary_visualizer.core.visualization import Visualizer
from roary_visualizer.models.data_models import VisualizationConfig, GeneDistribution

@pytest.fixture
def sample_data():
    """Create sample data for visualization tests"""
    data = pd.DataFrame({
        'Category': ['Core', 'Soft-core', 'Shell', 'Cloud'],
        'Count': [100, 50, 30, 20],
        'Percentage': [50, 25, 15, 10]
    })
    data.set_index('Category', inplace=True)
    return data

@pytest.fixture
def gene_distribution():
    """Create sample gene distribution"""
    return GeneDistribution(
        total_genes=200,
        core_genes=100,
        softcore_genes=50,
        shell_genes=30,
        cloud_genes=20,
        genes_per_genome=150.5
    )

@pytest.fixture
def visualizer():
    """Create Visualizer instance with default config"""
    return Visualizer(VisualizationConfig())

def test_create_bar_plot(visualizer, sample_data):
    """Test bar plot creation"""
    fig = visualizer.create_bar_plot(sample_data, "Test Plot")
    
    assert isinstance(fig, go.Figure)
    assert fig.layout.title.text == "Test Plot"
    assert len(fig.data) == 1
    assert fig.data[0].type == "bar"
    
    # Test log scale
    visualizer.config.log_scale = True
    fig_log = visualizer.create_bar_plot(sample_data, "Test Plot")
    assert fig_log.layout.yaxis.type == "log"

def test_create_pie_chart(visualizer, gene_distribution):
    """Test pie chart creation"""
    fig = visualizer.create_pie_chart(gene_distribution)
    
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].type == "pie"
    assert len(fig.data[0].values) == 4  # Core, Soft-core, Shell, Cloud
    assert fig.data[0].hole == 0.3  # Donut chart

def test_create_frequency_plot(visualizer):
    """Test frequency plot creation"""
    gene_freq = pd.DataFrame({
        'Gene': ['gene1', 'gene2', 'gene3'],
        'Present_in_genomes': [10, 5, 2],
        'Percentage': [100, 50, 20]
    })
    
    fig = visualizer.create_frequency_plot(gene_freq)
    
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].type == "bar"
    assert len(fig.data[0].x) == 3

def test_create_rarefaction_plot(visualizer):
    """Test rarefaction plot creation"""
    genome_counts = [1, 2, 3, 4, 5]
    gene_counts = [100, 150, 175, 190, 200]
    
    fig = visualizer.create_rarefaction_plot(genome_counts, gene_counts)
    
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].type == "scatter"
    assert len(fig.data[0].x) == len(genome_counts)
    assert len(fig.data[0].y) == len(gene_counts)

def test_create_matrix_plot(visualizer):
    """Test matrix plot creation"""
    # Create sample presence/absence matrix
    data = np.random.choice([0, 1], size=(10, 5))
    matrix = pd.DataFrame(
        data,
        columns=[f'genome_{i}' for i in range(5)],
        index=[f'gene_{i}' for i in range(10)]
    )
    
    fig = visualizer.create_matrix_plot(matrix)
    
    assert fig is not None
    assert hasattr(fig, 'get_size_inches')  # Check if it's a matplotlib figure