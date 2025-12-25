"""
SQLReleaseNotes2 Configuration Module

This module handles application configuration, including loading environment variables,
managing paths, and providing a centralized configuration for all modules.
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import logging
from pathlib import Path


class Config:
    """
    Configuration class for SQLReleaseNotes2 application.
    
    Handles loading environment variables, setting up paths, and providing
    configuration values to all modules.
    """
    
    def __init__(self, args=None):
        """
        Initialize configuration with optional command-line arguments.
        
        Args:
            args (argparse.Namespace, optional): Command-line arguments that override defaults.
        """
        # Load environment variables
        load_dotenv()
        
        # Base directories
        self.root_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.module_dir = self.root_dir / "modules"
        self.config_dir = self.root_dir / "config"
        
        # Default output directory
        self.output_dir = self.root_dir / "output"
        
        # Timestamp for file naming
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Set up directories
        self._setup_directories()
        
        # API Configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            logging.error("OPENAI_API_KEY environment variable is required")
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Database Configuration
        self.db_server = os.getenv("DB_SERVER", "localhost")
        self.db_user = os.getenv("DB_USER")
        self.db_password = os.getenv("DB_PASSWORD")
        
        if not self.db_user or not self.db_password:
            logging.error("DB_USER and DB_PASSWORD environment variables are required")
            raise ValueError("DB_USER and DB_PASSWORD environment variables are required")
        
        # Preview Mode
        self.preview_mode = os.getenv("PREVIEW_MODE", "False").lower() == "true"
        
        # Override with command-line args if provided
        if args:
            self._apply_args(args)
        
        # Set up output paths based on final configuration
        self._setup_output_paths()
    
    def _setup_directories(self):
        """Ensure all required directories exist."""
        dirs = [
            self.output_dir,
            self.output_dir / "metadata",
            self.output_dir / "release",
            self.output_dir / "tests",
            self.output_dir / "logs"
        ]
        
        for directory in dirs:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _apply_args(self, args):
        """
        Apply command-line arguments to override default configuration.
        
        Args:
            args (argparse.Namespace): Command-line arguments.
        """
        # Database names
        if hasattr(args, 'new_db') and args.new_db:
            self.new_db = args.new_db
        if hasattr(args, 'old_db') and args.old_db:
            self.old_db = args.old_db
        if hasattr(args, 'target_db') and args.target_db:
            self.target_db = args.target_db
        
        # Database connection
        if hasattr(args, 'server') and args.server:
            self.db_server = args.server
        if hasattr(args, 'user') and args.user:
            self.db_user = args.user
        if hasattr(args, 'password') and args.password:
            self.db_password = args.password
        
        # Output directory
        if hasattr(args, 'output_dir') and args.output_dir:
            self.output_dir = Path(args.output_dir)
            self._setup_directories()
        
        # Preview mode
        if hasattr(args, 'preview') and args.preview:
            self.preview_mode = True
    
    def _setup_output_paths(self):
        """Set up output file paths with timestamps."""
        # Metadata output
        self.metadata_output = self.output_dir / "metadata" / f"METADATA_SCRIPT_{self.timestamp}.sql"
        self.metadata_log = self.output_dir / "logs" / f"metadata_log_{self.timestamp}.txt"
        
        # Release notes output
        self.release_notes_output = self.output_dir / "release" / f"RELEASE_NOTES_{self.timestamp}.md"
        self.release_sql_output = self.output_dir / "release" / f"RELEASE_SQL_{self.timestamp}.md"
        self.release_log = self.output_dir / "logs" / f"release_log_{self.timestamp}.txt"
        
        # Test output
        self.test_procedures_output = self.output_dir / "tests" / f"TEST_PROCEDURES_{self.timestamp}.sql"
        self.test_runner_output = self.output_dir / "tests" / f"TEST_RUNNER_{self.timestamp}.sql"
        self.test_log = self.output_dir / "logs" / f"test_log_{self.timestamp}.txt"
        
        # SQL execution log
        self.sqlexec_log_dir = self.output_dir / "logs" / f"sqlexec_{self.timestamp}"
        self.sqlexec_log_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_version(self, db_name):
        """
        Extract version number from database name.
        
        Args:
            db_name (str): Database name in format <n>_v<version>
            
        Returns:
            str: Extracted version number
        
        Raises:
            ValueError: If database name format is invalid
        """
        import re
        match = re.search(r'_v([\d_]+)$', db_name)
        if match:
            return match.group(1)  # Return the full version string
        raise ValueError(f"Invalid database name format: {db_name}. Expected format: <n>_v<version>")
    
    def get_sqlcmd_args(self, filename, logfilename):
        """
        Get sqlcmd arguments for executing SQL files.
        
        Args:
            filename (str): SQL file to execute
            logfilename (str): Log file to write output
            
        Returns:
            list: List of sqlcmd arguments
        """
        return [
            "sqlcmd",
            "-U", self.db_user,
            "-P", self.db_password,
            "-S", self.db_server,
            "-d", self.target_db if hasattr(self, 'target_db') else self.new_db,
            "-i", filename,
            "-o", logfilename,
            "-h-1",  # No headers
            "-m1"    # Formatted output
        ]
    
    def setup_logging(self, module_name):
        """
        Set up logging for a specific module.
        
        Args:
            module_name (str): Name of the module for log file
            
        Returns:
            logging.Logger: Configured logger
        """
        logger = logging.getLogger(module_name)
        logger.setLevel(logging.DEBUG)
        
        # File handler
        log_file = self.output_dir / "logs" / f"{module_name}_log_{self.timestamp}.txt"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger


# Create a global config instance
config = Config()


def setup_module_config(args=None):
    """
    Set up module configuration with optional command-line arguments.
    
    Args:
        args (argparse.Namespace, optional): Command-line arguments
        
    Returns:
        Config: Configuration instance
    """
    global config
    config = Config(args)
    return config


def get_config():
    """
    Get the current configuration instance.
    
    Returns:
        Config: Configuration instance
    """
    return config
