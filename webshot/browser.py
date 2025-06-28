"""
Browser engine module for capturing screenshots using Selenium.
"""

import logging
from pathlib import Path
from urllib.parse import urlparse
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import io


class BrowserEngine:
    """Manages the headless browser for screenshot capture."""
    
    def __init__(self, options):
        """Initialize the browser engine with given options."""
        self.options = options
        self.logger = logging.getLogger(__name__)
        self.driver = None
        
    def start(self):
        """Start the browser engine."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"--window-size={self.options['width']},{self.options['height']}")
        
        # Set up service
        service = Service(ChromeDriverManager().install())
        
        # Create driver
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.logger.info("Browser engine started")
        
    def stop(self):
        """Stop the browser engine."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.logger.info("Browser engine stopped")
            
    def capture_screenshot(self, url):
        """Capture a screenshot of the given URL."""
        if not self.driver:
            raise RuntimeError("Browser engine not started")
            
        try:
            # Navigate to URL
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(2)  # Simple wait, could be improved with WebDriverWait
            
            # Apply zoom
            zoom = self.options['zoom']
            if zoom != 1.0:
                self.driver.execute_script(f"document.body.style.zoom='{zoom}'")
                
            # Capture screenshot
            if self.options['type'] == 'fullpage':
                screenshot_data = self._capture_full_page()
            else:
                screenshot_data = self.driver.get_screenshot_as_png()
                
            # Save screenshot
            filename = self._save_screenshot(url, screenshot_data)
            return filename
            
        except Exception as e:
            self.logger.error(f"Failed to capture screenshot for {url}: {str(e)}")
            raise
            
    def _capture_full_page(self):
        """Capture a full-page screenshot by scrolling and stitching."""
        # Get page dimensions
        total_height = self.driver.execute_script("return document.body.scrollHeight")
        viewport_height = self.driver.execute_script("return window.innerHeight")
        viewport_width = self.options['width']
        
        # Calculate number of scrolls needed
        scrolls = (total_height + viewport_height - 1) // viewport_height
        
        # Capture screenshots at each scroll position
        screenshots = []
        for i in range(scrolls):
            # Scroll to position
            scroll_y = i * viewport_height
            self.driver.execute_script(f"window.scrollTo(0, {scroll_y})")
            time.sleep(0.5)  # Wait for scroll to complete
            
            # Capture screenshot
            screenshot_data = self.driver.get_screenshot_as_png()
            screenshots.append(Image.open(io.BytesIO(screenshot_data)))
            
        # Stitch screenshots together
        full_image = Image.new('RGB', (viewport_width, total_height))
        y_offset = 0
        
        for i, img in enumerate(screenshots):
            # For the last image, only use the visible part
            if i == len(screenshots) - 1:
                remaining_height = total_height - y_offset
                if remaining_height < viewport_height:
                    img = img.crop((0, 0, viewport_width, remaining_height))
                    
            full_image.paste(img, (0, y_offset))
            y_offset += img.height
            
        # Convert to bytes
        output = io.BytesIO()
        full_image.save(output, format='PNG')
        return output.getvalue()
        
    def _save_screenshot(self, url, screenshot_data):
        """Save the screenshot to file."""
        # Generate filename from URL
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '').replace('.', '_')
        if not domain:
            domain = 'screenshot'
            
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        ext = self.options['format']
        filename = f"{domain}_{timestamp}.{ext}"
        
        # Full path
        filepath = self.options['output_dir'] / filename
        
        # Save image
        img = Image.open(io.BytesIO(screenshot_data))
        
        if self.options['format'] == 'jpeg':
            # Convert RGBA to RGB for JPEG
            if img.mode == 'RGBA':
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[3])
                img = rgb_img
                
            img.save(filepath, 'JPEG', quality=self.options['quality'])
        else:
            img.save(filepath, 'PNG')
            
        return filepath