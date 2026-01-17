import logging
import sys
from config.config import Config


class Logger:
    def __init__(self):
        self.config = Config()
        self._setup_logger()

    def _setup_logger(self):
        """Setup the logger with appropriate formatting and level."""
        self.logger = logging.getLogger("campusguide")
        self.logger.setLevel(getattr(logging, self.config.LOG_LEVEL.upper()))

        # Remove any existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.logger.level)

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)

        # Add handler to logger
        self.logger.addHandler(console_handler)

    def get_logger(self):
        """Get the configured logger instance."""
        return self.logger


# Global logger instance
logger = Logger().get_logger()
