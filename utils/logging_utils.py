"""
Logging utility for SuShe NG.

This module provides a centralized logging configuration for the application,
enabling consistent logging across all modules with options for console and file output.
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Union, Dict, Any

# Import Qt for integration with Qt's message handler
from PyQt6.QtCore import QtMsgType, QMessageLogContext, qInstallMessageHandler


# Define log levels mapping for easier reference
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}


class SusheNGLogger:
    """
    Centralized logger for the SuShe NG application.
    
    This class configures logging for both console and file output with
    appropriate formatting and log levels.
    """
    
    # Class-level variables to maintain the logger state
    _initialized = False
    _logger = None
    _log_file = None
    _console_level = logging.INFO
    _file_level = logging.DEBUG
    
    @classmethod
    def initialize(cls, 
                  app_name: str = "SusheNG",
                  console_level: Union[str, int] = "INFO", 
                  file_level: Union[str, int] = "DEBUG",
                  log_dir: Optional[Path] = None,
                  log_to_file: bool = True) -> logging.Logger:
        """
        Initialize the logging system.
        
        Args:
            app_name: Name of the application for the logger
            console_level: Minimum level for console output (string or int)
            file_level: Minimum level for file output (string or int)
            log_dir: Directory to store log files (default: user's log directory)
            log_to_file: Whether to log to a file
            
        Returns:
            The configured logger instance
        """
        if cls._initialized:
            return cls._logger
            
        # Create the root logger
        logger = logging.getLogger(app_name)
        logger.setLevel(logging.DEBUG)  # Base level - handlers will filter
        
        # Convert string levels to int if needed
        if isinstance(console_level, str):
            cls._console_level = LOG_LEVELS.get(console_level.upper(), logging.INFO)
        else:
            cls._console_level = console_level
            
        if isinstance(file_level, str):
            cls._file_level = LOG_LEVELS.get(file_level.upper(), logging.DEBUG)
        else:
            cls._file_level = file_level
        
        # Console handler with colored output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(cls._console_level)
        
        # Create formatters
        console_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler (optional)
        if log_to_file:
            # Determine log directory
            if log_dir is None:
                if sys.platform == 'win32':
                    base_dir = Path(os.environ.get('APPDATA', '.'))
                elif sys.platform == 'darwin':
                    base_dir = Path.home() / 'Library' / 'Logs'
                else:  # Linux/Unix
                    base_dir = Path.home() / '.local' / 'share'
                
                log_dir = base_dir / app_name / 'logs'
            
            # Ensure log directory exists
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # Create log file name based on date
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = log_dir / f"{app_name}_{timestamp}.log"
            cls._log_file = log_file
            
            # Set up file handler
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(cls._file_level)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        # Store the logger
        cls._logger = logger
        cls._initialized = True
        
        logger.info(f"Logging initialized. Console level: {logging.getLevelName(cls._console_level)}, "
                    f"File level: {logging.getLevelName(cls._file_level)}")
        
        if log_to_file:
            logger.info(f"Log file: {cls._log_file}")
        
        return logger
    
    @classmethod
    def get_logger(cls, name: Optional[str] = None) -> logging.Logger:
        """
        Get a logger instance.
        
        Args:
            name: Name of the logger (usually the module name)
            
        Returns:
            A configured logger instance
        """
        if not cls._initialized:
            cls.initialize()
        
        if name:
            return logging.getLogger(f"{cls._logger.name}.{name}")
        return cls._logger
    
    @classmethod
    def set_console_level(cls, level: Union[str, int]) -> None:
        """
        Set the console output log level.
        
        Args:
            level: The log level (string name or int value)
        """
        if not cls._initialized:
            cls.initialize()
        
        # Convert string level to int if needed
        if isinstance(level, str):
            level_value = LOG_LEVELS.get(level.upper(), logging.INFO)
        else:
            level_value = level
        
        # Update the console handler level
        for handler in cls._logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                handler.setLevel(level_value)
                cls._console_level = level_value
                cls._logger.info(f"Console log level set to {logging.getLevelName(level_value)}")
                break
    
    @classmethod
    def set_file_level(cls, level: Union[str, int]) -> None:
        """
        Set the file output log level.
        
        Args:
            level: The log level (string name or int value)
        """
        if not cls._initialized:
            cls.initialize()
        
        # Convert string level to int if needed
        if isinstance(level, str):
            level_value = LOG_LEVELS.get(level.upper(), logging.DEBUG)
        else:
            level_value = level
        
        # Update the file handler level
        for handler in cls._logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.setLevel(level_value)
                cls._file_level = level_value
                cls._logger.info(f"File log level set to {logging.getLevelName(level_value)}")
                break
    
    @classmethod
    def get_log_file(cls) -> Optional[Path]:
        """
        Get the current log file path.
        
        Returns:
            The path to the current log file or None if not logging to file
        """
        return cls._log_file


# Qt message handler integration
def qt_message_handler(msg_type: QtMsgType, context: QMessageLogContext, message: str) -> None:
    """
    Handle Qt log messages and redirect them to Python's logging system.
    
    Args:
        msg_type: The type of message (debug, info, warning, critical, fatal)
        context: The context of the message (file, line, function)
        message: The message text
    """
    logger = SusheNGLogger.get_logger("Qt")
    
    # Map Qt log levels to Python logging levels
    if msg_type == QtMsgType.QtDebugMsg:
        logger.debug(message)
    elif msg_type == QtMsgType.QtInfoMsg:
        logger.info(message)
    elif msg_type == QtMsgType.QtWarningMsg:
        logger.warning(message)
    elif msg_type == QtMsgType.QtCriticalMsg:
        logger.critical(message)
    elif msg_type == QtMsgType.QtFatalMsg:
        logger.critical(f"FATAL: {message}")
    else:
        logger.debug(message)


def setup_qt_logging() -> None:
    """
    Set up Qt message redirection to Python logging.
    
    This should be called after initializing the logger and before creating the QApplication.
    """
    qInstallMessageHandler(qt_message_handler)


# Convenience functions
def get_module_logger(module_name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger for a specific module.
    
    Args:
        module_name: The name of the module (defaults to calling module name)
        
    Returns:
        A configured logger for the module
    """
    if module_name is None:
        # Get the calling module's name
        import inspect
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        if module:
            module_name = module.__name__
        else:
            module_name = "__main__"
    
    # Strip __main__ prefix if it exists
    if module_name.startswith("__main__."):
        module_name = module_name[9:]
    
    return SusheNGLogger.get_logger(module_name)