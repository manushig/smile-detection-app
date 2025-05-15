import logging

def setup_logger():
    """
    Sets up centralized logging configuration that logs messages
    to both the console and a file named 'app.log'.

    Uses:
    - INFO level for general messages
    - WARNING/ERROR levels for error conditions
    - A consistent format including timestamp, severity, and message
    """
    logging.basicConfig(
        level=logging.INFO,  # Set default logging level
        format='%(asctime)s | %(levelname)s | %(message)s',  # Log format
        handlers=[
            logging.FileHandler("app.log"),  # Log to file
            logging.StreamHandler()          # Also log to console
        ]
    )
