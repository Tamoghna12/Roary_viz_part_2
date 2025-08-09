# Installation Guide

## Quick Installation

### Option 1: Using pip (Recommended)
```bash
# Clone the repository
git clone <repository_url>
cd roary-visualizer

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .

# Run the application
streamlit run src/roary_visualizer/app/main.py
```

### Option 2: Using Docker
```bash
# Build and run with Docker Compose
make deploy

# Or build manually
docker build -t roary-visualizer .
docker run -p 8501:8501 roary-visualizer
```

### Option 3: Development Setup
```bash
# Install with development dependencies
make install

# Run tests
make test

# Format code
make format

# Run linting
make lint
```

## System Requirements

- Python 3.8 or higher
- 2GB RAM minimum (4GB recommended)
- 100MB disk space
- Modern web browser (Chrome, Firefox, Safari, Edge)

## Dependencies

### Core Dependencies
- **Streamlit** (>=1.32.0) - Web application framework
- **Pandas** (>=2.2.0) - Data manipulation and analysis
- **NumPy** (>=1.26.0) - Numerical computing
- **Plotly** (>=5.19.0) - Interactive visualizations
- **BioPython** (>=1.83) - Biological data processing
- **Matplotlib** (>=3.8.0) - Static plotting
- **Seaborn** (>=0.13.0) - Statistical visualizations

### Optional Dependencies
- **Prometheus Client** - Metrics and monitoring
- **PSUtil** - System resource monitoring
- **Python-dotenv** - Environment variable management

## Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` to customize settings:
   - `STREAMLIT_SERVER_PORT`: Port for the web application
   - `MAX_UPLOAD_SIZE`: Maximum file upload size
   - `ENABLE_CACHE`: Enable result caching for better performance

## Troubleshooting

### Common Issues

**ImportError: No module named 'roary_visualizer'**
- Solution: Install the package with `pip install -e .`

**Port already in use**
- Solution: Change `STREAMLIT_SERVER_PORT` in `.env` file

**Out of memory errors with large datasets**
- Solution: Increase `MAX_MEMORY_MB` in configuration

**File upload fails**
- Solution: Check file size against `MAX_UPLOAD_SIZE` limit

### Getting Help

- Check the [README.md](README.md) for usage instructions
- Report issues on GitHub
- Review logs in the `logs/` directory

## Performance Tips

1. **Enable caching** by setting `ENABLE_CACHE=true`
2. **Limit file sizes** to under 100MB for optimal performance
3. **Close browser tabs** when processing large datasets
4. **Use Docker** for consistent performance across systems