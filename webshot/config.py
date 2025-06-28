"""
Configuration management module.
"""

import json
import logging
from pathlib import Path


class Config:
    """Manages application configuration and settings persistence."""
    
    def __init__(self, config_file="config.json"):
        """Initialize configuration manager."""
        self.logger = logging.getLogger(__name__)
        self.config_file = Path(config_file)
        self.settings = {}
        self.load()
        
    def load(self):
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.settings = json.load(f)
                self.logger.info(f"Configuration loaded from {self.config_file}")
            except Exception as e:
                self.logger.error(f"Failed to load configuration: {str(e)}")
                self.settings = {}
        else:
            self.logger.info("No configuration file found, using defaults")
            self.settings = self._get_defaults()
            
    def save(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            self.logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {str(e)}")
            
    def get(self, key, default=None):
        """Get a configuration value."""
        return self.settings.get(key, default)
        
    def set(self, key, value):
        """Set a configuration value."""
        self.settings[key] = value
        
    def _get_defaults(self):
        """Get default configuration values."""
        return {
            "output_directory": str(Path.cwd() / "screenshots"),
            "shot_type": "viewport",
            "viewport_width": 1920,
            "viewport_height": 1080,
            "zoom_level": 1.0,
            "output_format": "png",
            "jpeg_quality": 85,
            "parallel_threads": 1,
            "window_geometry": "900x700"
        }