# Demo Data

This directory contains sample data files to demonstrate the capabilities of the Roary Visualizer.

## Files Included

### gene_presence_absence.csv
Sample pangenome matrix with 20 bacterial genomes and 500 representative genes. This file demonstrates:
- Core genes (present in >99% of genomes)
- Accessory genes (variable presence across genomes)
- Strain-specific genes (present in few genomes)

### summary_statistics.txt
Statistical summary of the pangenome analysis including:
- Total number of genes in different categories
- Genome-specific gene counts
- Pangenome size metrics

### accessory_binary_genes.fa.newick (optional)
Phylogenetic tree showing relationships between the sample genomes, used for ordering strains in visualizations.

## How to Use Demo Data

1. Start the Roary Visualizer application
2. Upload all three files using the file uploader
3. Explore the different visualization tabs:
   - **Gene Categories**: Bar chart of core/accessory/unique genes
   - **Pangenome Distribution**: Pie chart showing gene distribution
   - **Gene Frequency**: Histogram of gene frequencies across genomes
   - **Rarefaction Curve**: Analysis of pangenome saturation
   - **Presence/Absence Matrix**: Interactive heatmap with clustering

## Expected Results

With this demo data, you should see:
- **Core genes**: ~200 genes present in all genomes
- **Accessory genes**: ~250 genes with variable presence
- **Unique genes**: ~50 genes present in single genomes
- **Clear clustering** of related bacterial strains
- **Publication-quality** visualizations ready for export

## Data Source

This demo data is based on publicly available bacterial genome sequences and has been anonymized for demonstration purposes. The data represents typical results from a pangenome analysis of closely related bacterial strains.