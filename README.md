# Roary Output Visualizer

A production-ready web application for visualizing Roary pangenome analysis output, built with Streamlit. This application provides interactive visualizations for pangenome data, including gene presence/absence matrices, gene frequency distributions, and phylogenetic trees.

## Features

- Interactive visualization of Roary output files
- Gene presence/absence matrix visualization with clustering options
- Pangenome category distribution plots
- Gene frequency analysis
- Rarefaction curve generation
- Integrated phylogenetic tree visualization
- Performance monitoring and caching
- Docker containerization support
- Comprehensive error handling
- Production-ready deployment configuration

## Requirements

- Python 3.8 or higher
- Docker (for containerized deployment)
- Make (optional, for using Makefile commands)

## Quick Start

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd roary-visualizer
   ```

2. Install dependencies:
   ```bash
   make install
   ```

3. Run the application locally:
   ```bash
   make run
   ```

4. Or deploy with Docker:
   ```bash
   make deploy
   ```

The application will be available at http://localhost:8501

## Input Files

The application expects the following Roary output files:
- `gene_presence_absence.csv`: Gene presence/absence matrix
- `summary_statistics.txt`: Summary of gene categories
- `accessory_binary_genes.fa.newick` (optional): Phylogenetic tree

## Development

### Setting Up Development Environment

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Running Tests

Run the test suite:
```bash
make test
```

Run linting checks:
```bash
make lint
```

Format code:
```bash
make format
```

### Docker Development

Build the Docker image:
```bash
make build
```

Run the containerized application:
```bash
make deploy
```

## Production Deployment

### Configuration

1. Create environment configuration:
   ```bash
   python deployment/configure.py --env prod
   ```

2. Adjust environment variables in `.env` file if needed.

3. Deploy the application:
   ```bash
   make deploy
   ```

### Maintenance

Create backup:
```bash
make backup
```

Restore from backup:
```bash
make restore path=<backup_path>
```

View logs:
```bash
make logs
```

### Performance Monitoring

The application includes built-in performance monitoring:
- Memory usage tracking
- CPU usage monitoring
- Execution time measurements
- Resource limit monitoring

### Error Handling

- Comprehensive error handling for file operations
- Input validation
- Resource usage monitoring
- Graceful degradation under load

## Project Structure

```
.
├── src/
│   └── roary_visualizer/
│       ├── app/            # Main application code
│       ├── core/           # Core functionality
│       ├── config/         # Configuration
│       ├── middleware/     # Middleware components
│       ├── models/         # Data models
│       └── utils/          # Utility functions
├── tests/                  # Test suite
├── deployment/             # Deployment configuration
├── docker-compose.yml      # Docker composition
├── Dockerfile             # Docker build configuration
├── Makefile              # Development commands
└── README.md             # This file
```

## Configuration Options

### Environment Variables

- `STREAMLIT_SERVER_PORT`: Port to run the application (default: 8501)
- `ENABLE_CACHE`: Enable result caching (default: true)
- `MAX_MEMORY_MB`: Maximum memory usage (default: 1024)
- `MAX_WORKERS`: Maximum worker processes (default: 4)
- `ENVIRONMENT`: Deployment environment (dev/prod)

### Performance Settings

- Cache TTL: 300 seconds (configurable)
- Maximum file size: 100MB (configurable)
- Batch processing: 5000 records (configurable)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.