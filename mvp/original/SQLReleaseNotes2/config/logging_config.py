"""
Logging configuration for SQLReleaseNotes2.

This module provides logging configuration for the application, including
console and file logging, and colored output.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
import colorama

# Initialize colorama for colored console output
colorama.init()


def setup_logging(output_dir=None, module_name="app", timestamp=None):
    """
    Set up logging for a module with both file and console handlers.
    
    Args:
        output_dir (str, optional): Directory for log files. Defaults to 'output/logs'.
        module_name (str, optional): Name of the module. Defaults to 'app'.
        timestamp (str, optional): Timestamp for log filename. Defaults to current datetime.
        
    Returns:
        logging.Logger: Configured logger
    """
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if output_dir is None:
        output_dir = Path(os.getcwd()) / "output" / "logs"
    else:
        output_dir = Path(output_dir)
    
    # Ensure log directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.DEBUG)
    logger.handlers = []  # Clear existing handlers
    
    # File handler - logs everything to file
    log_file = output_dir / f"{module_name}_{timestamp}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler - only logs INFO and above to console
    console_handler = ColoredConsoleHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    
    # Add formatters to handlers
    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def setup_prompt_logging(output_dir=None, module_name="prompts", timestamp=None):
    """
    Set up logging for AI prompts and responses.
    
    Args:
        output_dir (str, optional): Directory for log files. Defaults to 'output/logs'.
        module_name (str, optional): Name of the module. Defaults to 'prompts'.
        timestamp (str, optional): Timestamp for log filename. Defaults to current datetime.
        
    Returns:
        callable: Function to log prompts and responses
    """
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if output_dir is None:
        output_dir = Path(os.getcwd()) / "output" / "logs"
    else:
        output_dir = Path(output_dir)
    
    # Ensure log directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    log_file = output_dir / f"{module_name}_{timestamp}.log"
    
    def log_prompt(content, obj_name, content_type="PROMPT"):
        """
        Log a prompt or response to the log file.
        
        Args:
            content (str): The content to log
            obj_name (str): The object name for context
            content_type (str, optional): Type of content (PROMPT or RESPONSE). Defaults to "PROMPT".
        """
        try:
            with open(log_file, 'a', encoding='utf-8') as log:
                log.write(f"\n{'-' * 80}\n")
                log.write(f"OBJECT: {obj_name} | TYPE: {content_type} | TIME: {datetime.now()}\n")
                log.write(f"{'-' * 80}\n\n")
                log.write(f"{content}\n\n")
        except Exception as e:
            logging.error(f"Failed to log {content_type.lower()} for {obj_name}: {e}")
    
    return log_prompt


class ColoredConsoleHandler(logging.StreamHandler):
    """
    Custom logging handler that applies colors to console output based on log level.
    """
    
    COLORS = {
        logging.DEBUG: colorama.Fore.CYAN,
        logging.INFO: colorama.Fore.GREEN,
        logging.WARNING: colorama.Fore.YELLOW,
        logging.ERROR: colorama.Fore.RED,
        logging.CRITICAL: colorama.Fore.RED + colorama.Style.BRIGHT
    }
    
    def emit(self, record):
        """
        Emit a record with color based on log level.
        
        Args:
            record: Log record to emit
        """
        # Get color based on log level
        color = self.COLORS.get(record.levelno, colorama.Fore.WHITE)
        
        # Add color to message
        record.msg = f"{color}{record.msg}{colorama.Style.RESET_ALL}"
        
        # Call parent emit
        super().emit(record)
