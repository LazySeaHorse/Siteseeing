"""
Unit tests for configuration management.
"""

import unittest
import tempfile
import json
from pathlib import Path
from webshot.config import Config


class TestConfig(unittest.TestCase):
    """Test cases for Config class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "test_config.json"
        
    def tearDown(self):
        """Clean up test fixtures."""
        if self.config_file.exists():
            self.config_file.unlink()
            
    def test_load_default_config(self):
        """Test loading default configuration."""
        config = Config(self.config_file)
        
        # Check some default values
        self.assertEqual(config.get("shot_type"), "viewport")
        self.assertEqual(config.get("viewport_width"), 1920)
        self.assertEqual(config.get("output_format"), "png")
        
    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        # Create and save config
        config1 = Config(self.config_file)
        config1.set("test_key", "test_value")
        config1.set("viewport_width", 1280)
        config1.save()
        
        # Load config in new instance
        config2 = Config(self.config_file)
        
        self.assertEqual(config2.get("test_key"), "test_value")
        self.assertEqual(config2.get("viewport_width"), 1280)
        
    def test_get_with_default(self):
        """Test getting configuration value with default."""
        config = Config(self.config_file)
        
        self.assertEqual(config.get("nonexistent_key", "default"), "default")
        self.assertIsNone(config.get("nonexistent_key"))
        
    def test_corrupted_config_file(self):
        """Test handling of corrupted configuration file."""
        # Write invalid JSON
        with open(self.config_file, 'w') as f:
            f.write("{ invalid json")
            
        # Should fall back to defaults
        config = Config(self.config_file)
        self.assertEqual(config.get("shot_type"), "viewport")


if __name__ == '__main__':
    unittest.main()