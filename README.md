# Siteseeing - Website Screenshot Capture Tool

A modular Python application for capturing screenshots of websites with both GUI and batch processing support.

> [!NOTE]
> Coded to life in less than 10 minutes with some help from Claude 4 Opus

## Features

- **Lots of Options**:
  - Viewport-only or full-page capture
  - Customizable viewport size
  - Zoom level adjustment
  - PNG or JPEG output with quality control
- **Batch Processing**: Process multiple URLs with configurable parallel threads
- **Error Handling**: Continues processing even if individual URLs fail

[![screenshot.png](https://i.postimg.cc/j2xVRWyM/screenshot.png)](https://postimg.cc/N9zC4jJX)

## Installation

### Method 1: Direct Run (Recommended)

1. Clone or download this repository
2. Double-click `main.py` or run:
   ```bash
   python main.py
   ```
3. The application will automatically:
   - Create a virtual environment
   - Install required dependencies
   - Launch the GUI

### Method 2: Package Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/siteseeing.git
cd siteseeing

# Install in development mode
pip install -e .

# Run the application
siteseeing
```

## Usage

### GUI Mode

1. **Enter URLs**: Type URLs in the text area (one per line) or load from a file
2. **Configure Options**:
   - Choose between viewport-only or full-page capture
   - Set viewport dimensions
   - Adjust zoom level
   - Select output format (PNG/JPEG)
3. **Select Output Directory**: Choose where to save screenshots
4. **Start Processing**: Click "Start" to begin capturing screenshots

### Batch Processing

- Add multiple URLs to process them sequentially
- Configure parallel threads for faster processing
- Monitor progress in the status panel
- Cancel processing at any time

### URL Format

- URLs can be entered with or without protocol (https:// will be added if missing)
- Comments can be added with # at the start of a line
- Example:
  ```
  https://example.com
  google.com
  # This is a comment
  github.com/user/repo
  ```

## Configuration

Settings are automatically saved to `config.json` and include:
- Output directory
- Viewport dimensions
- Zoom level
- Output format and quality
- Window size and position

## Requirements

- Python 3.8 or higher
- Chrome or Chromium browser (automatically downloaded via webdriver-manager)

## Dependencies

- selenium: Web browser automation
- Pillow: Image processing
- webdriver-manager: Automatic ChromeDriver management

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Project Structure

```
siteseeing/
├── main.py              # Entry point with auto-setup
├── webshot/             # Main package
│   ├── app.py           # Application controller
│   ├── gui.py           # Tkinter interface
│   ├── browser.py       # Selenium browser control
│   ├── config.py        # Settings management
│   ├── queue_manager.py # Batch processing
│   └── utils.py         # Utility functions
└── tests/               # Unit tests
```

## Troubleshooting

### Chrome/Chromium Not Found
The application uses webdriver-manager to automatically download and manage ChromeDriver. If you encounter issues, ensure Chrome or Chromium is installed on your system.

### Permission Errors
On Unix-like systems, you may need to make `main.py` executable:
```bash
chmod +x main.py
```

### Virtual Environment Issues
If the automatic virtual environment setup fails, you can manually create one:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m webshot.app
```

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
