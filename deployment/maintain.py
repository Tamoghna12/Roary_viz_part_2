#!/usr/bin/env python3
import os
import sys
import argparse
import logging
import subprocess
from pathlib import Path
from datetime import datetime
import shutil

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MaintenanceManager:
    """Handles deployment maintenance tasks"""
    
    def __init__(self, base_dir: str):
        """Initialize maintenance manager
        
        Args:
            base_dir: Base directory for the application
        """
        self.base_dir = Path(base_dir)
        self.backup_dir = self.base_dir / 'backups'
        self.data_dir = self.base_dir / 'data'
        self.logs_dir = self.base_dir / 'logs'
    
    def create_backup(self) -> str:
        """Create backup of data and configuration
        
        Returns:
            str: Path to backup directory
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.backup_dir / f'backup_{timestamp}'
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Backup environment file
        env_file = self.base_dir / '.env'
        if env_file.exists():
            shutil.copy2(env_file, backup_path / '.env')
        
        # Backup data directory
        if self.data_dir.exists():
            shutil.copytree(self.data_dir, backup_path / 'data')
        
        # Backup logs
        if self.logs_dir.exists():
            shutil.copytree(self.logs_dir, backup_path / 'logs')
        
        logger.info(f"Created backup at {backup_path}")
        return str(backup_path)
    
    def restore_backup(self, backup_path: str) -> bool:
        """Restore from backup
        
        Args:
            backup_path: Path to backup directory
            
        Returns:
            bool: True if restore successful
        """
        try:
            backup_dir = Path(backup_path)
            if not backup_dir.exists():
                logger.error(f"Backup directory {backup_path} does not exist")
                return False
            
            # Stop running containers
            self.stop_containers()
            
            # Restore environment file
            env_backup = backup_dir / '.env'
            if env_backup.exists():
                shutil.copy2(env_backup, self.base_dir / '.env')
            
            # Restore data directory
            data_backup = backup_dir / 'data'
            if data_backup.exists():
                if self.data_dir.exists():
                    shutil.rmtree(self.data_dir)
                shutil.copytree(data_backup, self.data_dir)
            
            # Restore logs
            logs_backup = backup_dir / 'logs'
            if logs_backup.exists():
                if self.logs_dir.exists():
                    shutil.rmtree(self.logs_dir)
                shutil.copytree(logs_backup, self.logs_dir)
            
            logger.info(f"Successfully restored from backup {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore backup: {str(e)}")
            return False
    
    def rotate_logs(self, max_size_mb: int = 100, max_files: int = 5) -> None:
        """Rotate log files
        
        Args:
            max_size_mb: Maximum size of log files in MB
            max_files: Maximum number of log files to keep
        """
        try:
            log_files = list(self.logs_dir.glob('*.log'))
            for log_file in log_files:
                size_mb = log_file.stat().st_size / (1024 * 1024)
                if size_mb > max_size_mb:
                    # Rotate existing rotated logs
                    for i in range(max_files - 1, 0, -1):
                        old = log_file.with_suffix(f'.log.{i}')
                        new = log_file.with_suffix(f'.log.{i + 1}')
                        if old.exists():
                            if i == max_files - 1:
                                old.unlink()
                            else:
                                old.rename(new)
                    
                    # Rotate current log
                    log_file.rename(log_file.with_suffix('.log.1'))
                    
                    # Create new empty log file
                    log_file.touch()
            
            logger.info("Log rotation completed")
        except Exception as e:
            logger.error(f"Failed to rotate logs: {str(e)}")
    
    def cleanup_temp_files(self, max_age_days: int = 7) -> None:
        """Clean up old temporary files
        
        Args:
            max_age_days: Maximum age of files to keep in days
        """
        try:
            temp_dir = self.base_dir / 'tmp'
            if not temp_dir.exists():
                return
            
            now = datetime.now().timestamp()
            max_age_seconds = max_age_days * 24 * 60 * 60
            
            for item in temp_dir.iterdir():
                age_seconds = now - item.stat().st_mtime
                if age_seconds > max_age_seconds:
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
            
            logger.info(f"Cleaned up temporary files older than {max_age_days} days")
        except Exception as e:
            logger.error(f"Failed to clean up temporary files: {str(e)}")
    
    def stop_containers(self) -> None:
        """Stop running Docker containers"""
        try:
            subprocess.run(
                ['docker', 'compose', '-f', str(self.base_dir / 'docker-compose.yml'), 'down'],
                check=True,
                capture_output=True
            )
            logger.info("Stopped running containers")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to stop containers: {e.stderr.decode()}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Maintain Roary Visualizer deployment")
    parser.add_argument(
        'action',
        choices=['backup', 'restore', 'rotate-logs', 'cleanup'],
        help='Maintenance action to perform'
    )
    parser.add_argument(
        '--backup-path',
        help='Path to backup directory for restore action'
    )
    parser.add_argument(
        '--max-age',
        type=int,
        default=7,
        help='Maximum age in days for cleanup action'
    )
    args = parser.parse_args()
    
    base_dir = Path(__file__).parent.parent
    manager = MaintenanceManager(base_dir)
    
    if args.action == 'backup':
        manager.create_backup()
    elif args.action == 'restore':
        if not args.backup_path:
            logger.error("--backup-path is required for restore action")
            sys.exit(1)
        if not manager.restore_backup(args.backup_path):
            sys.exit(1)
    elif args.action == 'rotate-logs':
        manager.rotate_logs()
    elif args.action == 'cleanup':
        manager.cleanup_temp_files(args.max_age)

if __name__ == "__main__":
    main()