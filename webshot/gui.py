"""
GUI module for Siteseeing using Tkinter.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import queue
import logging
from pathlib import Path
from .browser import BrowserEngine
from .queue_manager import QueueManager
from .utils import validate_url


class SiteseeingGUI:
    """Main GUI class for the Siteseeing application."""
    
    def __init__(self, config):
        """Initialize the GUI."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.root = tk.Tk()
        self.root.title("Siteseeing - Website Screenshot Tool")
        
        # Set window geometry from config
        geometry = self.config.get("window_geometry", "900x700")
        self.root.geometry(geometry)
        
        # Queue for thread communication
        self.message_queue = queue.Queue()
        self.queue_manager = QueueManager()
        self.browser_engine = None
        self.processing = False
        
        self._setup_ui()
        self._load_settings()
        self._start_message_handler()
        
    def _setup_ui(self):
        """Set up the user interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Top section - URL input
        url_frame = ttk.LabelFrame(main_frame, text="URLs", padding="5")
        url_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        url_frame.columnconfigure(0, weight=1)
        
        # URL text area
        self.url_text = scrolledtext.ScrolledText(url_frame, height=5, width=50)
        self.url_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # URL buttons
        url_button_frame = ttk.Frame(url_frame)
        url_button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Button(url_button_frame, text="Load from File", 
                  command=self._load_urls_from_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(url_button_frame, text="Clear", 
                  command=lambda: self.url_text.delete(1.0, tk.END)).pack(side=tk.LEFT)
        
        # Middle section - Options
        options_frame = ttk.Frame(main_frame)
        options_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Screenshot options
        shot_frame = ttk.LabelFrame(options_frame, text="Screenshot Options", padding="5")
        shot_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 10))
        
        # Type
        ttk.Label(shot_frame, text="Type:").grid(row=0, column=0, sticky=tk.W)
        self.shot_type = tk.StringVar(value="viewport")
        ttk.Radiobutton(shot_frame, text="Viewport Only", variable=self.shot_type, 
                       value="viewport").grid(row=0, column=1, sticky=tk.W)
        ttk.Radiobutton(shot_frame, text="Full Page", variable=self.shot_type, 
                       value="fullpage").grid(row=0, column=2, sticky=tk.W)
        
        # Viewport size
        ttk.Label(shot_frame, text="Viewport:").grid(row=1, column=0, sticky=tk.W)
        viewport_frame = ttk.Frame(shot_frame)
        viewport_frame.grid(row=1, column=1, columnspan=2, sticky=tk.W)
        
        self.width_var = tk.IntVar(value=1920)
        self.height_var = tk.IntVar(value=1080)
        
        ttk.Entry(viewport_frame, textvariable=self.width_var, width=8).pack(side=tk.LEFT)
        ttk.Label(viewport_frame, text=" × ").pack(side=tk.LEFT)
        ttk.Entry(viewport_frame, textvariable=self.height_var, width=8).pack(side=tk.LEFT)
        
        # Zoom level
        ttk.Label(shot_frame, text="Zoom:").grid(row=2, column=0, sticky=tk.W)
        self.zoom_var = tk.DoubleVar(value=1.0)
        zoom_frame = ttk.Frame(shot_frame)
        zoom_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E))
        
        self.zoom_scale = ttk.Scale(zoom_frame, from_=0.5, to=2.0, 
                                   variable=self.zoom_var, orient=tk.HORIZONTAL)
        self.zoom_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.zoom_label = ttk.Label(zoom_frame, text="100%")
        self.zoom_label.pack(side=tk.LEFT, padx=(5, 0))
        
        self.zoom_scale.bind("<Motion>", self._update_zoom_label)
        
        # Format options
        format_frame = ttk.LabelFrame(options_frame, text="Output Format", padding="5")
        format_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N))
        
        self.format_var = tk.StringVar(value="png")
        ttk.Radiobutton(format_frame, text="PNG", variable=self.format_var, 
                       value="png", command=self._on_format_change).grid(row=0, column=0)
        ttk.Radiobutton(format_frame, text="JPEG", variable=self.format_var, 
                       value="jpeg", command=self._on_format_change).grid(row=0, column=1)
        
        # JPEG quality
        self.quality_frame = ttk.Frame(format_frame)
        self.quality_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Label(self.quality_frame, text="Quality:").pack(side=tk.LEFT)
        self.quality_var = tk.IntVar(value=85)
        self.quality_scale = ttk.Scale(self.quality_frame, from_=1, to=100, 
                                      variable=self.quality_var, orient=tk.HORIZONTAL)
        self.quality_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.quality_label = ttk.Label(self.quality_frame, text="85")
        self.quality_label.pack(side=tk.LEFT)
        
        self.quality_scale.bind("<Motion>", self._update_quality_label)
        self.quality_frame.grid_remove()  # Hide initially
        
        # Output directory
        output_frame = ttk.LabelFrame(main_frame, text="Output Directory", padding="5")
        output_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        
        self.output_dir_var = tk.StringVar(value=str(Path.cwd() / "screenshots"))
        ttk.Entry(output_frame, textvariable=self.output_dir_var, 
                 state="readonly").grid(row=0, column=0, sticky=(tk.W, tk.E))
        ttk.Button(output_frame, text="Browse", 
                  command=self._browse_output_dir).grid(row=0, column=1, padx=(5, 0))
        
        # Batch processing options
        batch_frame = ttk.LabelFrame(main_frame, text="Batch Processing", padding="5")
        batch_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(batch_frame, text="Parallel threads:").pack(side=tk.LEFT)
        self.threads_var = tk.IntVar(value=1)
        ttk.Spinbox(batch_frame, from_=1, to=5, textvariable=self.threads_var, 
                   width=5).pack(side=tk.LEFT, padx=(5, 20))
        
        # Control buttons
        self.start_button = ttk.Button(batch_frame, text="Start", command=self._start_processing)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.pause_button = ttk.Button(batch_frame, text="Pause", command=self._pause_processing, 
                                      state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.cancel_button = ttk.Button(batch_frame, text="Cancel", command=self._cancel_processing, 
                                       state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT)
        
        # Status panel
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="5")
        status_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=10, width=50)
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, 
                                           mode='determinate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
    def _load_settings(self):
        """Load saved settings from config."""
        # Output directory
        output_dir = self.config.get("output_directory", str(Path.cwd() / "screenshots"))
        self.output_dir_var.set(output_dir)
        
        # Screenshot options
        self.shot_type.set(self.config.get("shot_type", "viewport"))
        self.width_var.set(self.config.get("viewport_width", 1920))
        self.height_var.set(self.config.get("viewport_height", 1080))
        self.zoom_var.set(self.config.get("zoom_level", 1.0))
        
        # Format options
        self.format_var.set(self.config.get("output_format", "png"))
        self.quality_var.set(self.config.get("jpeg_quality", 85))
        self._on_format_change()
        
        # Batch options
        self.threads_var.set(self.config.get("parallel_threads", 1))
        
    def _save_settings(self):
        """Save current settings to config."""
        self.config.set("output_directory", self.output_dir_var.get())
        self.config.set("shot_type", self.shot_type.get())
        self.config.set("viewport_width", self.width_var.get())
        self.config.set("viewport_height", self.height_var.get())
        self.config.set("zoom_level", self.zoom_var.get())
        self.config.set("output_format", self.format_var.get())
        self.config.set("jpeg_quality", self.quality_var.get())
        self.config.set("parallel_threads", self.threads_var.get())
        self.config.set("window_geometry", self.root.geometry())
        
    def _start_message_handler(self):
        """Start the message queue handler."""
        self._process_message_queue()
        
    def _process_message_queue(self):
        """Process messages from worker threads."""
        try:
            while True:
                msg_type, msg_data = self.message_queue.get_nowait()
                
                if msg_type == "log":
                    self._add_status_message(msg_data)
                elif msg_type == "progress":
                    self.progress_var.set(msg_data)
                elif msg_type == "complete":
                    self._on_processing_complete()
                    
        except queue.Empty:
            pass
            
        self.root.after(100, self._process_message_queue)
        
    def _add_status_message(self, message):
        """Add a message to the status panel."""
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        
    def _update_zoom_label(self, event=None):
        """Update the zoom percentage label."""
        zoom = self.zoom_var.get()
        self.zoom_label.config(text=f"{int(zoom * 100)}%")
        
    def _update_quality_label(self, event=None):
        """Update the quality label."""
        quality = self.quality_var.get()
        self.quality_label.config(text=str(int(quality)))
        
    def _on_format_change(self):
        """Handle format change."""
        if self.format_var.get() == "jpeg":
            self.quality_frame.grid()
        else:
            self.quality_frame.grid_remove()
            
    def _browse_output_dir(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_dir_var.get()
        )
        if directory:
            self.output_dir_var.set(directory)
            
    def _load_urls_from_file(self):
        """Load URLs from a text file."""
        filename = filedialog.askopenfilename(
            title="Select URL file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    urls = f.read()
                    self.url_text.insert(tk.END, urls)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")
                
    def _start_processing(self):
        """Start processing screenshots."""
        # Get URLs from text widget
        urls_text = self.url_text.get(1.0, tk.END).strip()
        if not urls_text:
            messagebox.showwarning("No URLs", "Please enter at least one URL.")
            return
            
        # Parse and validate URLs
        urls = []
        for line in urls_text.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                if validate_url(line):
                    urls.append(line)
                else:
                    self._add_status_message(f"Invalid URL skipped: {line}")
                    
        if not urls:
            messagebox.showwarning("No Valid URLs", "No valid URLs found.")
            return
            
        # Create output directory
        output_dir = Path(self.output_dir_var.get())
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Update UI state
        self.processing = True
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.NORMAL)
        
        # Clear status
        self.status_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        
        # Save settings
        self._save_settings()
        
        # Prepare options
        options = {
            'type': self.shot_type.get(),
            'width': self.width_var.get(),
            'height': self.height_var.get(),
            'zoom': self.zoom_var.get(),
            'format': self.format_var.get(),
            'quality': self.quality_var.get() if self.format_var.get() == 'jpeg' else None,
            'output_dir': output_dir
        }
        
        # Start processing in thread
        thread = threading.Thread(
            target=self._process_urls,
            args=(urls, options),
            daemon=True
        )
        thread.start()
        
    def _process_urls(self, urls, options):
        """Process URLs in a worker thread."""
        try:
            # Initialize browser engine
            self.browser_engine = BrowserEngine(options)
            self.browser_engine.start()
            
            total_urls = len(urls)
            
            for i, url in enumerate(urls):
                if not self.processing:
                    break
                    
                self.message_queue.put(("log", f"Processing {i+1}/{total_urls}: {url}"))
                
                try:
                    filename = self.browser_engine.capture_screenshot(url)
                    self.message_queue.put(("log", f"✓ Saved: {filename}"))
                except Exception as e:
                    self.message_queue.put(("log", f"✗ Error: {url} - {str(e)}"))
                    
                progress = ((i + 1) / total_urls) * 100
                self.message_queue.put(("progress", progress))
                
        except Exception as e:
            self.message_queue.put(("log", f"Fatal error: {str(e)}"))
            
        finally:
            if self.browser_engine:
                self.browser_engine.stop()
                
            self.message_queue.put(("complete", None))
            
    def _pause_processing(self):
        """Pause processing (placeholder)."""
        messagebox.showinfo("Pause", "Pause functionality not implemented in this version.")
        
    def _cancel_processing(self):
        """Cancel processing."""
        self.processing = False
        self._add_status_message("Cancelling...")
        
    def _on_processing_complete(self):
        """Handle processing completion."""
        self.processing = False
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.DISABLED)
        self._add_status_message("Processing complete!")
        
    def _on_closing(self):
        """Handle window closing."""
        if self.processing:
            if messagebox.askokcancel("Quit", "Processing is in progress. Are you sure you want to quit?"):
                self.processing = False
                self._save_settings()
                self.root.destroy()
        else:
            self._save_settings()
            self.root.destroy()
            
    def run(self):
        """Run the GUI application."""
        self.root.mainloop()