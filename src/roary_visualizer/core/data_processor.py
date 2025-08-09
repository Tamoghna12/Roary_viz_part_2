from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np
from ..models.data_models import GeneDistribution, RoaryDataset, VisualizationConfig

class DataProcessor:
    """Processes Roary output data for visualization"""
    
    def __init__(self, config: VisualizationConfig):
        """Initialize data processor with configuration
        
        Args:
            config: Visualization configuration object
        """
        self.config = config
    
    def process_gene_distribution(self, roary_df: pd.DataFrame) -> GeneDistribution:
        """Calculate gene distribution statistics
        
        Args:
            roary_df: Gene presence/absence matrix
            
        Returns:
            GeneDistribution: Calculated statistics
        """
        total_genomes = roary_df.shape[1]
        total_genes = roary_df.shape[0]
        gene_freq = roary_df.sum(axis=1)
        
        core_genes = (gene_freq >= total_genomes * self.config.core_threshold).sum()
        softcore_genes = ((gene_freq >= total_genomes * self.config.softcore_threshold) & 
                         (gene_freq < total_genomes * self.config.core_threshold)).sum()
        shell_genes = ((gene_freq >= total_genomes * self.config.shell_threshold) & 
                      (gene_freq < total_genomes * self.config.softcore_threshold)).sum()
        cloud_genes = (gene_freq < total_genomes * self.config.shell_threshold).sum()
        
        return GeneDistribution(
            total_genes=total_genes,
            core_genes=core_genes,
            softcore_genes=softcore_genes,
            shell_genes=shell_genes,
            cloud_genes=cloud_genes,
            genes_per_genome=gene_freq.mean()
        )
    
    def calculate_gene_frequencies(self, roary_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate gene frequency statistics
        
        Args:
            roary_df: Gene presence/absence matrix
            
        Returns:
            pd.DataFrame: Gene frequency statistics
        """
        gene_freq = roary_df.sum(axis=1)
        return pd.DataFrame({
            'Gene': gene_freq.index,
            'Present_in_genomes': gene_freq.values,
            'Percentage': (gene_freq.values / roary_df.shape[1] * 100).round(2)
        }).sort_values('Present_in_genomes', ascending=False)
    
    def generate_rarefaction_data(self, roary_df: pd.DataFrame, num_permutations: int = 50) -> Tuple[List[int], List[float]]:
        """Generate rarefaction curve data
        
        Args:
            roary_df: Gene presence/absence matrix
            num_permutations: Number of random permutations
            
        Returns:
            Tuple[List[int], List[float]]: Genome counts and corresponding gene counts
        """
        genome_counts = list(range(1, roary_df.shape[1] + 1))
        gene_counts = []
        
        for i in genome_counts:
            sizes = []
            for _ in range(num_permutations):
                sample = roary_df.sample(n=i, axis=1)
                size = (sample.sum(axis=1) > 0).sum()
                sizes.append(size)
            gene_counts.append(np.mean(sizes))
        
        return genome_counts, gene_counts
    
    def analyze_gene_patterns(self, roary_df: pd.DataFrame, pattern_type: str = 'all') -> pd.DataFrame:
        """Analyze specific gene presence/absence patterns
        
        Args:
            roary_df: Gene presence/absence matrix
            pattern_type: Type of pattern to analyze ('rare', 'common', 'variable', 'all')
            
        Returns:
            pd.DataFrame: Analysis results
        """
        gene_freq = roary_df.sum(axis=1)
        total_genomes = roary_df.shape[1]
        
        if pattern_type == 'rare':
            mask = gene_freq <= total_genomes * 0.1
        elif pattern_type == 'common':
            mask = gene_freq >= total_genomes * 0.9
        elif pattern_type == 'variable':
            mask = (gene_freq > total_genomes * 0.3) & (gene_freq < total_genomes * 0.7)
        else:  # 'all'
            mask = pd.Series([True] * len(gene_freq), index=gene_freq.index)
        
        filtered_genes = gene_freq[mask]
        return pd.DataFrame({
            'Gene': filtered_genes.index,
            'Present_in_genomes': filtered_genes.values,
            'Percentage': (filtered_genes.values / total_genomes * 100).round(2)
        }).sort_values('Present_in_genomes', ascending=(pattern_type == 'rare'))