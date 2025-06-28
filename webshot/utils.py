"""
Utility functions for the Siteseeing application.
"""

import re
from urllib.parse import urlparse


def validate_url(url: str) -> bool:
    """
    Validate if a string is a valid URL.
    
    Args:
        url: The URL string to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        # Add scheme if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        result = urlparse(url)
        
        # Check if all required parts are present
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a string to be used as a filename.
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
        
    return filename


def format_bytes(size: int) -> str:
    """
    Format bytes into human-readable format.
    
    Args:
        size: Size in bytes
        
    Returns:
        Formatted string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def parse_url_list(text: str) -> list:
    """
    Parse a text containing URLs into a list.
    
    Args:
        text: Text containing URLs (one per line)
        
    Returns:
        List of valid URLs
    """
    urls = []
    
    for line in text.strip().split('\n'):
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue
            
        # Add scheme if missing
        if not line.startswith(('http://', 'https://')):
            line = 'https://' + line
            
        if validate_url(line):
            urls.append(line)
            
    return urls