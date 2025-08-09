import streamlit as st
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from roary_visualizer.core.data_processor import DataProcessor
from roary_visualizer.core.visualization import Visualizer
from roary_visualizer.utils.file_handler import FileHandler
from roary_visualizer.models.data_models import VisualizationConfig, GeneDistribution, RoaryDataset
from roary_visualizer.config.settings import Settings
from roary_visualizer.config.logging.config import setup_logging, get_logger
from roary_visualizer.middleware import handle_errors, measure_performance, cache_data, validate_input, ValidationError

# Set up logging
setup_logging()
logger = get_logger(__name__)

@handle_errors
@measure_performance(threshold_ms=500)
def initialize_session_state() -> None:
    """Initialize Streamlit session state variables"""
    if 'file_handler' not in st.session_state:
        st.session_state.file_handler = FileHandler(Settings.get_temp_dir())
    if 'dataset' not in st.session_state:
        st.session_state.dataset = RoaryDataset()
    if 'config' not in st.session_state:
        st.session_state.config = VisualizationConfig(**Settings.get_config())

@handle_errors
@measure_performance()
def handle_file_upload() -> Tuple[bool, str]:
    """Handle file upload process with validation
    
    Returns:
        Tuple[bool, str]: Success status and error message if any
    """
    uploaded_files = st.file_uploader(
        "Upload Roary output files",
        accept_multiple_files=True,
        type=["txt", "csv", "newick"]
    )
    
    if not uploaded_files:
        return False, ""
        
    try:
        for uploaded_file in uploaded_files:
            # Validate file size
            validate_input(
                Settings.validate_file_size(uploaded_file.size),
                f"File {uploaded_file.name} exceeds maximum size limit of {Settings.MAX_UPLOAD_SIZE/1024/1024:.0f}MB"
            )
            
            # Validate file extensions
            validate_input(
                any(uploaded_file.name.lower().endswith(ext) for ext in Settings.ALLOWED_EXTENSIONS.values()),
                f"Invalid file type: {uploaded_file.name}"
            )
            
            st.session_state.file_handler.save_uploaded_file(uploaded_file, uploaded_file.name)
        
        return True, ""
    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        return False, str(e)

@handle_errors
@measure_performance()
@cache_data(ttl_seconds=300)
def process_uploaded_files() -> bool:
    """Process uploaded files and update session state with validation"""
    try:
        # Process summary statistics
        summary_stats = st.session_state.file_handler.read_summary_statistics(
            next(Path(Settings.get_temp_dir()).glob("*statistics.txt"))
        )
        
        # Process presence/absence matrix
        gene_matrix = st.session_state.file_handler.read_presence_absence_matrix(
            next(Path(Settings.get_temp_dir()).glob("*presence_absence.csv"))
        )
        
        validate_input(
            gene_matrix is not None and not gene_matrix.empty,
            "Invalid or empty gene presence/absence matrix"
        )
        
        # Process tree file if available
        tree_files = list(Path(Settings.get_temp_dir()).glob("*.newick"))
        tree = None
        if tree_files:
            tree = st.session_state.file_handler.read_tree_file(tree_files[0])
        
        # Update session state
        st.session_state.dataset = RoaryDataset(
            gene_presence_absence=gene_matrix,
            summary_statistics=summary_stats,
            tree_data=tree
        )
        
        return True
    except Exception as e:
        logger.error(f"File processing error: {str(e)}")
        raise ValidationError(f"Error processing files: {str(e)}")

@handle_errors
@measure_performance()
def render_visualization_settings() -> None:
    """Render visualization settings sidebar with validation"""
    st.sidebar.title("Visualization Settings")
    
    with st.sidebar.expander("Pangenome Category Thresholds", expanded=False):
        core_threshold = st.slider(
            "Core gene threshold (%)", 
            min_value=90, max_value=100, 
            value=int(st.session_state.config.core_threshold * 100)
        ) / 100
        
        softcore_threshold = st.slider(
            "Soft-core gene threshold (%)", 
            min_value=80, max_value=95, 
            value=int(st.session_state.config.softcore_threshold * 100)
        ) / 100
        
        shell_threshold = st.slider(
            "Shell gene threshold (%)", 
            min_value=5, max_value=40, 
            value=int(st.session_state.config.shell_threshold * 100)
        ) / 100
        
        # Validate threshold relationships
        validate_input(
            core_threshold > softcore_threshold > shell_threshold,
            "Invalid thresholds: Core > Soft-core > Shell must be maintained"
        )
        
        st.session_state.config.core_threshold = core_threshold
        st.session_state.config.softcore_threshold = softcore_threshold
        st.session_state.config.shell_threshold = shell_threshold
    
    with st.sidebar.expander("Matrix Visualization", expanded=False):
        st.session_state.config.cluster_rows = st.checkbox(
            "Cluster rows", value=st.session_state.config.cluster_rows
        )
        st.session_state.config.cluster_cols = st.checkbox(
            "Cluster columns", value=st.session_state.config.cluster_cols
        )
        st.session_state.config.log_scale = st.checkbox(
            "Use logarithmic scale", value=st.session_state.config.log_scale
        )

@handle_errors
@measure_performance(threshold_ms=2000)
def render_visualizations() -> None:
    """Render visualization components with performance monitoring"""
    data_processor = DataProcessor(st.session_state.config)
    visualizer = Visualizer(st.session_state.config)
    
    # Calculate distributions
    gene_dist = data_processor.process_gene_distribution(st.session_state.dataset.gene_presence_absence)
    
    # Basic dataset information
    st.markdown("### Dataset Information")
    st.markdown(f"""
    - **Number of genomes**: {st.session_state.dataset.gene_presence_absence.shape[1]:,}
    - **Total genes**: {st.session_state.dataset.gene_presence_absence.shape[0]:,}
    - **Core genes**: {gene_dist.core_genes:,}
    - **Average genes per genome**: {gene_dist.genes_per_genome:.1f}
    """)
    
    # Create visualization tabs
    tabs = st.tabs([
        "Gene Categories",
        "Pangenome Distribution",
        "Gene Frequency",
        "Rarefaction Curve",
        "Presence/Absence Matrix"
    ])
    
    with tabs[0]:
        with st.spinner("Generating gene category plot..."):
            st.plotly_chart(
                visualizer.create_bar_plot(
                    pd.DataFrame(st.session_state.dataset.summary_statistics),
                    "Gene Category Distribution"
                ),
                use_container_width=True
            )
    
    with tabs[1]:
        with st.spinner("Generating pangenome distribution plot..."):
            st.plotly_chart(
                visualizer.create_pie_chart(gene_dist),
                use_container_width=True
            )
    
    with tabs[2]:
        with st.spinner("Generating gene frequency plot..."):
            gene_freq = data_processor.calculate_gene_frequencies(
                st.session_state.dataset.gene_presence_absence
            )
            st.plotly_chart(
                visualizer.create_frequency_plot(gene_freq),
                use_container_width=True
            )
    
    with tabs[3]:
        with st.spinner("Generating rarefaction curve..."):
            genome_counts, gene_counts = data_processor.generate_rarefaction_data(
                st.session_state.dataset.gene_presence_absence,
                Settings.DEFAULT_PERMUTATIONS
            )
            st.plotly_chart(
                visualizer.create_rarefaction_plot(genome_counts, gene_counts),
                use_container_width=True
            )
    
    with tabs[4]:
        if st.session_state.dataset.gene_presence_absence.shape[0] > Settings.MAX_GENES_DISPLAY:
            st.warning(
                f"Large matrix detected ({st.session_state.dataset.gene_presence_absence.shape[0]:,} genes). "
                f"Sampling {Settings.MAX_GENES_DISPLAY:,} genes for visualization."
            )
        
        with st.spinner("Generating presence/absence matrix..."):
            fig = visualizer.create_matrix_plot(
                st.session_state.dataset.gene_presence_absence,
                st.session_state.dataset.tree_data
            )
            st.pyplot(fig)

@handle_errors
def main() -> None:
    """Main application entry point with error handling"""
    st.set_page_config(
        page_title="Roary Output Visualizer",
        layout="wide",
        page_icon="🧬"
    )
    
    st.title("🧬 Roary Output Visualizer")
    st.markdown("""
    This application visualizes the output files from [Roary](https://sanger-pathogens.github.io/Roary/), 
    a tool for pan-genome analysis. Upload your Roary output files to generate interactive visualizations.
    """)
    
    # Initialize session state
    initialize_session_state()
    
    # File upload section
    st.markdown("### Upload Your Roary Output Files")
    st.markdown("""
    Please upload the following files from your Roary output:
    - **summary_statistics.txt** (required): Contains gene category counts
    - **gene_presence_absence.csv** (required): Contains the gene presence/absence matrix
    - **accessory_binary_genes.fa.newick** (optional): Phylogenetic tree for strain ordering
    """)
    
    success, error = handle_file_upload()
    
    if error:
        st.error(error)
        return
    
    if success and process_uploaded_files():
        # Render visualization settings
        render_visualization_settings()
        
        # Render visualizations
        render_visualizations()
    
    # Cleanup on session end
    if st.session_state.file_handler:
        st.session_state.file_handler.cleanup()

if __name__ == "__main__":
    main()