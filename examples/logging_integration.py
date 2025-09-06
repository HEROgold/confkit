"""
Examples demonstrating how to use confkit with Python's logging module.

This example shows:
1. Configuring logging with confkit
2. Dynamic log level changes
3. Handler configuration via confkit
4. Custom formatters with confkit settings

Run with: python logging_integration.py
"""

import logging
import sys
from configparser import ConfigParser
from enum import StrEnum
from pathlib import Path

from confkit import Config
from confkit.data_types import StrEnum as ConfigStrEnum


class LogLevel(StrEnum):
    """Enum for standard logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# Set up confkit
parser = ConfigParser()
Config.set_parser(parser)
Config.set_file(Path("config.ini"))


class LoggingConfig:
    """Configuration for the logging system."""
    
    # Log level as a string enum
    level = Config(ConfigStrEnum(LogLevel.INFO))
    
    # File logging settings
    log_to_file = Config(True)
    log_file = Config("app.log")
    file_level = Config(ConfigStrEnum(LogLevel.DEBUG))
    
    # Console logging settings
    log_to_console = Config(True)
    console_level = Config(ConfigStrEnum(LogLevel.INFO))
    
    # Format settings
    date_format = Config("%Y-%m-%d %H:%M:%S")
    file_format = Config("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_format = Config("%(levelname)s: %(message)s")


class LoggingManager:
    """Class to manage logging configuration with confkit."""
    
    def __init__(self, name: str) -> None:
        """Initialize the logging manager with a logger name."""
        self.config = LoggingConfig()
        self.logger = logging.getLogger(name)
        self.configure()
    
    def configure(self) -> None:
        """Configure the logger based on current config settings."""
        # Reset handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Set root level to the most verbose needed
        self.logger.setLevel(getattr(logging, str(self.config.level)))
        
        # Configure file handler if enabled
        if self.config.log_to_file:
            file_formatter = logging.Formatter(
                self.config.file_format,
                datefmt=self.config.date_format
            )
            file_handler = logging.FileHandler(self.config.log_file)
            file_handler.setLevel(getattr(logging, str(self.config.file_level)))
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        
        # Configure console handler if enabled
        if self.config.log_to_console:
            console_formatter = logging.Formatter(
                self.config.console_format
            )
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, str(self.config.console_level)))
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
    
    def update_level(self, level: LogLevel) -> None:
        """Update the root log level."""
        self.config.level = level
        self.configure()
    
    def update_file_level(self, level: LogLevel) -> None:
        """Update the file handler log level."""
        self.config.file_level = level
        self.configure()
    
    def update_console_level(self, level: LogLevel) -> None:
        """Update the console handler log level."""
        self.config.console_level = level
        self.configure()


def main():
    # Set up our logging manager
    log_manager = LoggingManager("example")
    logger = log_manager.logger
    
    # Log at different levels
    print("=== Initial Logging Configuration ===")
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    # Change log level and log again
    print("\n=== After Changing to DEBUG Level ===")
    log_manager.update_level(LogLevel.DEBUG)
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    
    # Change console format
    print("\n=== After Changing Console Format ===")
    log_manager.config.console_format = "%(asctime)s - %(levelname)s - %(message)s"
    log_manager.configure()
    logger.debug("This is a debug message with timestamp")
    logger.info("This is an info message with timestamp")
    
    # Disable console logging
    print("\n=== After Disabling Console Logging ===")
    log_manager.config.log_to_console = False
    log_manager.configure()
    logger.debug("This debug message won't appear in console")
    logger.info("This info message won't appear in console")
    logger.warning("This warning message won't appear in console")
    
    # Enable console logging again
    log_manager.config.log_to_console = True
    log_manager.configure()
    
    # Change both file and console levels
    print("\n=== With Different Console and File Levels ===")
    log_manager.update_console_level(LogLevel.WARNING)
    log_manager.update_file_level(LogLevel.DEBUG)
    logger.debug("This debug message only goes to file")
    logger.info("This info message only goes to file")
    logger.warning("This warning message goes to console and file")
    logger.error("This error message goes to console and file")
    
    print("\nCheck the log file for all messages.")


if __name__ == "__main__":
    main()
