import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from typing import Tuple, List, Optional
from ..models.data_models import GeneDistribution, VisualizationConfig

class Visualizer:
    """Handles visualization of Roary data"""
    
    def __init__(self, config: VisualizationConfig):
        """Initialize visualizer with configuration
        
        Args:
            config: Visualization configuration object
        """
        self.config = config
    
    def create_bar_plot(self, df: pd.DataFrame, title: str) -> go.Figure:
        """Create bar plot of gene categories
        
        Args:
            df: DataFrame with gene categories
            title: Plot title
            
        Returns:
            go.Figure: Plotly figure object
        """
        fig = px.bar(
            df,
            x=df.index,
            y=df.columns[2],  # Assumes third column contains counts
            title=title,
            labels={'index': 'Category', 'y': 'Number of genes'}
        )
        
        if self.config.log_scale:
            fig.update_layout(yaxis_type="log")
        
        fig.update_layout(
            xaxis_tickangle=-45,
            showlegend=False,
            height=500
        )
        
        return fig
    
    def create_pie_chart(self, dist: GeneDistribution) -> go.Figure:
        """Create pie chart of pangenome distribution
        
        Args:
            dist: Gene distribution statistics
            
        Returns:
            go.Figure: Plotly figure object
        """
        fig = go.Figure(data=[go.Pie(
            labels=['Core', 'Soft-core', 'Shell', 'Cloud'],
            values=[dist.core_genes, dist.softcore_genes, dist.shell_genes, dist.cloud_genes],
            hole=.3,
            hovertemplate="<b>%{label}</b><br>" +
                         "Genes: %{value}<br>" +
                         "Percentage: %{percent}<br>"
        )])
        
        fig.update_layout(
            title='Pangenome Distribution',
            annotations=[dict(text='Genes', x=0.5, y=0.5, font_size=20, showarrow=False)],
            height=600
        )
        
        return fig
    
    def create_frequency_plot(self, gene_freq: pd.DataFrame) -> go.Figure:
        """Create gene frequency distribution plot
        
        Args:
            gene_freq: Gene frequency DataFrame
            
        Returns:
            go.Figure: Plotly figure object
        """
        fig = px.bar(
            gene_freq,
            x='Present_in_genomes',
            y='Gene',
            title='Gene Frequency Distribution',
            labels={'Present_in_genomes': 'Number of genomes', 'Gene': 'Number of genes'}
        )
        
        fig.update_layout(
            xaxis_title="Number of genomes containing the gene",
            yaxis_title="Number of genes",
            height=500
        )
        
        return fig
    
    def create_rarefaction_plot(self, genome_counts: List[int], gene_counts: List[float]) -> go.Figure:
        """Create rarefaction curve plot
        
        Args:
            genome_counts: List of genome counts
            gene_counts: List of gene counts
            
        Returns:
            go.Figure: Plotly figure object
        """
        fig = px.line(
            x=genome_counts,
            y=gene_counts,
            title='Gene Accumulation Curve',
            labels={'x': 'Number of genomes', 'y': 'Number of genes'}
        )
        
        fig.update_layout(
            xaxis_title="Number of genomes sampled",
            yaxis_title="Total number of genes",
            height=500
        )
        
        return fig
    
    def create_matrix_plot(self, roary_df: pd.DataFrame, tree: Optional[object] = None) -> plt.Figure:
        """Create presence/absence matrix heatmap
        
        Args:
            roary_df: Gene presence/absence matrix
            tree: Optional phylogenetic tree object
            
        Returns:
            plt.Figure: Matplotlib figure object
        """
        plt.rcParams['svg.fonttype'] = 'none'
        
        if self.config.cluster_rows and self.config.cluster_cols:
            g = sns.clustermap(
                roary_df.T,
                cmap='Blues',
                figsize=(15, 10),
                xticklabels=False,
                yticklabels=True,
                cbar_pos=(0.02, 0.8, 0.03, 0.2)
            )
            fig = g.fig
            fig.suptitle("Presence/Absence Matrix (Clustered)", fontsize=16, y=1.02)
        else:
            fig, ax = plt.subplots(figsize=(15, 10))
            
            if tree:
                leaf_names = [tip.name for tip in tree.get_terminals()]
                valid_names = [name for name in leaf_names if name in roary_df.columns]
                
                if valid_names:
                    roary_sorted = roary_df[valid_names].T
                else:
                    roary_sorted = roary_df.T
            else:
                roary_sorted = roary_df.T
            
            sns.heatmap(
                roary_sorted,
                cmap='Blues',
                cbar=True,
                ax=ax,
                xticklabels=False
            )
            ax.set_title("Presence/Absence Matrix")
            ax.set_xlabel("Genes")
            ax.set_ylabel("Genomes")
        
        plt.tight_layout()
        return fig