# File: backend/app/logger.py

import logging

def setup_logger():
    """
    Sets up centralized logging configuration that logs messages
    to both the console and a file named 'app.log'.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler()
        ]
    )
