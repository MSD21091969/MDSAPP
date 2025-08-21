# MDSAPP/core/logging_config.py

import logging
import os
from google.cloud import logging as google_cloud_logging
from google.cloud.logging.handlers import CloudLoggingHandler, setup_logging as google_setup_logging

def setup_logging():
    """
    Configures logging to use Google Cloud Logging if credentials are available,
    otherwise falls back to standard console logging.
    """
    # Check if we are in a Google Cloud environment
    # A simple check is to see if the GOOGLE_APPLICATION_CREDENTIALS env var is set.
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        try:
            # Set up Google Cloud Logging
            client = google_cloud_logging.Client()
            # The setup_logging function attaches the handler to the root logger
            google_setup_logging(CloudLoggingHandler(client))
            logging.info("Google Cloud Logging has been configured.")
        except Exception as e:
            logging.warning(f"Could not configure Google Cloud Logging: {e}. Falling back to console logging.")
            # Fallback to basic config if Google Cloud setup fails
            logging.basicConfig(level=logging.DEBUG)
    else:
        # If not in a GCP environment, use basic console logging
        logging.basicConfig(level=logging.DEBUG)
        logging.info("Using basic console logging. Set GOOGLE_APPLICATION_CREDENTIALS to use Google Cloud Logging.")
