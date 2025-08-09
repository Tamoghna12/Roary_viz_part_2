.PHONY: install test lint format clean build deploy backup restore logs stop help

# Development
install:
	python -m pip install -r requirements.txt
	python -m pip install -e .[dev]
	pre-commit install

test:
	pytest --cov=src/roary_visualizer --cov-report=html

lint:
	pre-commit run --all-files

format:
	black src/ tests/
	isort src/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +

# Docker
build:
	docker build -t roary-visualizer:latest .

deploy:
	docker-compose up -d

stop:
	docker-compose down

# Maintenance
backup:
	@echo "Creating backup..."
	@timestamp=$$(date +%Y%m%d_%H%M%S); \
	tar -czf "backup_$$timestamp.tar.gz" data/ logs/ .env \
	&& echo "Backup created: backup_$$timestamp.tar.gz"

restore:
	@if [ -z "$(path)" ]; then \
		echo "Please specify backup path: make restore path=<backup_path>"; \
		exit 1; \
	fi
	@echo "Restoring from $(path)..."
	@tar -xzf "$(path)"
	@echo "Restore complete"

logs:
	docker-compose logs -f

# Help
help:
	@echo "Available commands:"
	@echo "  install    - Install dependencies and set up development environment"
	@echo "  test       - Run tests with coverage report"
	@echo "  lint       - Run linting checks"
	@echo "  format     - Format code using black and isort"
	@echo "  clean      - Clean up temporary files and build artifacts"
	@echo "  build      - Build Docker image"
	@echo "  deploy     - Deploy application using Docker Compose"
	@echo "  stop       - Stop running containers"
	@echo "  backup     - Create backup of data and configuration"
	@echo "  restore    - Restore from backup (use: make restore path=<backup_path>)"
	@echo "  logs       - View application logs"