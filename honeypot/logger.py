"""Logging helpers for the honeypot."""

import logging
import os

LOG_PATH = "/app/logs/honeypot.log"


def create_logger():
    """
    Creates and returns a configured logger for the honeypot.
    """
    os.makedirs("/app/logs", exist_ok=True)

    logger = logging.getLogger("Honeypot")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )

        file_handler = logging.FileHandler(LOG_PATH)
        file_handler.setFormatter(formatter)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger
