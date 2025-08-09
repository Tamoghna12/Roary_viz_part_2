#!/bin/bash
set -e

# Configure application environment
if [ "$ENVIRONMENT" = "dev" ]; then
    export ENABLE_DEBUG=true
    export LOG_LEVEL=DEBUG
else
    export ENABLE_DEBUG=false
    export LOG_LEVEL=INFO
fi

# Create required directories if they don't exist
mkdir -p /app/logs /app/tmp /app/data

# Set proper permissions
chmod -R 755 /app/logs /app/tmp /app/data

# Check if we need to install additional dependencies
if [ -f "/app/requirements.local.txt" ]; then
    echo "Installing additional dependencies..."
    pip install -r /app/requirements.local.txt
fi

# Run database migrations or other setup tasks here if needed

# Function to check streamlit health
check_health() {
    curl -f "http://localhost:${STREAMLIT_SERVER_PORT:-8501}/_stcore/health" || return 1
}

# Start the application with proper error handling
exec "$@" || {
    EXIT_CODE=$?
    echo "Application failed with exit code ${EXIT_CODE}"
    exit ${EXIT_CODE}
}