"""
Main application module for Siteseeing.
"""

import sys
import logging
from pathlib import Path
from .gui import SiteseeingGUI
from .config import Config


def setup_logging():
    """Configure application logging."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "siteseeing.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Main application entry point."""
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting Siteseeing application")
    
    # Load configuration
    config = Config()
    
    # Create and run GUI
    app = SiteseeingGUI(config)
    app.run()
    
    # Save configuration on exit
    config.save()
    logger.info("Siteseeing application closed")


if __name__ == "__main__":
    main()