from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel

class GeneDistribution(BaseModel):
    """Model for gene distribution statistics"""
    total_genes: int
    core_genes: int
    softcore_genes: int
    shell_genes: int
    cloud_genes: int
    genes_per_genome: float

class VisualizationConfig(BaseModel):
    """Model for visualization configuration"""
    core_threshold: float = 0.99
    softcore_threshold: float = 0.95
    shell_threshold: float = 0.15
    cluster_rows: bool = True
    cluster_cols: bool = False
    log_scale: bool = False

@dataclass
class RoaryDataset:
    """Container for processed Roary data"""
    gene_presence_absence: Optional[Dict[str, List[int]]] = None
    summary_statistics: Optional[Dict[str, int]] = None
    tree_data: Optional[str] = None
    timestamp: datetime = datetime.now()