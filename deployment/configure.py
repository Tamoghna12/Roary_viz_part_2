#!/usr/bin/env python3
import os
import shutil
import argparse
import logging
from pathlib import Path
from typing import Dict, Any
import json
import subprocess

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DeploymentConfigurator:
    """Handles deployment configuration and setup"""
    
    def __init__(self, base_dir: str):
        """Initialize configurator
        
        Args:
            base_dir: Base directory for the application
        """
        self.base_dir = Path(base_dir)
        self.env_file = self.base_dir / '.env'
        self.docker_compose = self.base_dir / 'docker-compose.yml'
    
    def create_directories(self) -> None:
        """Create necessary directories"""
        dirs = ['logs', 'tmp', 'data']
        for dir_name in dirs:
            dir_path = self.base_dir / dir_name
            dir_path.mkdir(exist_ok=True)
            logger.info(f"Created directory: {dir_path}")
    
    def setup_environment(self, config: Dict[str, Any]) -> None:
        """Set up environment configuration
        
        Args:
            config: Configuration dictionary
        """
        if self.env_file.exists():
            backup = self.env_file.with_suffix('.env.backup')
            shutil.copy(self.env_file, backup)
            logger.info(f"Backed up existing .env to {backup}")
        
        with open(self.env_file, 'w') as f:
            for key, value in config.items():
                f.write(f"{key}={value}\n")
        logger.info("Created .env file with configuration")
    
    def check_docker(self) -> bool:
        """Check if Docker and Docker Compose are installed
        
        Returns:
            bool: True if both are installed
        """
        try:
            subprocess.run(['docker', '--version'], check=True, capture_output=True)
            subprocess.run(['docker', 'compose', 'version'], check=True, capture_output=True)
            logger.info("Docker and Docker Compose are installed")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("Docker and/or Docker Compose are not installed")
            return False
    
    def check_python_dependencies(self) -> bool:
        """Check if Python dependencies can be installed
        
        Returns:
            bool: True if dependencies can be installed
        """
        try:
            subprocess.run(
                ['pip', 'install', '-r', str(self.base_dir / 'requirements.txt')],
                check=True,
                capture_output=True
            )
            logger.info("Python dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install Python dependencies: {e.stderr.decode()}")
            return False
    
    def configure_logging(self) -> None:
        """Configure logging settings"""
        log_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                }
            },
            'handlers': {
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': str(self.base_dir / 'logs' / 'app.log'),
                    'maxBytes': 10485760,
                    'backupCount': 5,
                    'formatter': 'standard'
                }
            },
            'root': {
                'level': 'INFO',
                'handlers': ['file']
            }
        }
        
        config_file = self.base_dir / 'config' / 'logging.json'
        with open(config_file, 'w') as f:
            json.dump(log_config, f, indent=4)
        logger.info("Created logging configuration")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Configure Roary Visualizer deployment")
    parser.add_argument(
        '--env',
        choices=['dev', 'prod'],
        default='prod',
        help='Environment to configure'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8501,
        help='Port to run the application on'
    )
    args = parser.parse_args()
    
    base_dir = Path(__file__).parent.parent
    configurator = DeploymentConfigurator(base_dir)
    
    # Create necessary directories
    configurator.create_directories()
    
    # Set up environment configuration
    config = {
        'TEMP_DIR': str(base_dir / 'tmp'),
        'STREAMLIT_SERVER_PORT': str(args.port),
        'STREAMLIT_SERVER_ADDRESS': '0.0.0.0',
        'STREAMLIT_BROWSER_GATHER_USAGE_STATS': 'false',
        'PYTHONPATH': str(base_dir),
        'ENVIRONMENT': args.env,
        'MAX_UPLOAD_SIZE': str(100 * 1024 * 1024),  # 100MB
        'MAX_GENES_DISPLAY': '5000',
        'DEFAULT_PERMUTATIONS': '50'
    }
    
    if args.env == 'dev':
        config.update({
            'ENABLE_DEBUG': 'true',
            'LOG_LEVEL': 'DEBUG'
        })
    else:
        config.update({
            'ENABLE_DEBUG': 'false',
            'LOG_LEVEL': 'INFO'
        })
    
    configurator.setup_environment(config)
    
    # Check dependencies
    if not configurator.check_docker():
        logger.error("Please install Docker and Docker Compose")
        return
    
    if not configurator.check_python_dependencies():
        logger.error("Please fix Python dependency issues")
        return
    
    # Configure logging
    configurator.configure_logging()
    
    logger.info(f"Configuration complete for {args.env} environment")
    logger.info(f"Application will be available at http://localhost:{args.port}")

if __name__ == "__main__":
    main()