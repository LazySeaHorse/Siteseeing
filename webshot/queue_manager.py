"""
Queue management module for batch processing.
"""

import queue
import threading
import logging
from typing import List, Callable, Any


class QueueManager:
    """Manages URL processing queue for batch operations."""
    
    def __init__(self):
        """Initialize the queue manager."""
        self.logger = logging.getLogger(__name__)
        self.task_queue = queue.Queue()
        self.results_queue = queue.Queue()
        self.workers = []
        self.running = False
        
    def add_urls(self, urls: List[str]):
        """Add URLs to the processing queue."""
        for url in urls:
            self.task_queue.put(url)
        self.logger.info(f"Added {len(urls)} URLs to queue")
        
    def start_workers(self, num_workers: int, worker_func: Callable[[str], Any]):
        """Start worker threads for processing."""
        self.running = True
        
        for i in range(num_workers):
            worker = threading.Thread(
                target=self._worker,
                args=(worker_func,),
                daemon=True,
                name=f"Worker-{i+1}"
            )
            worker.start()
            self.workers.append(worker)
            
        self.logger.info(f"Started {num_workers} worker threads")
        
    def stop_workers(self):
        """Stop all worker threads."""
        self.running = False
        
        # Add stop signals to queue
        for _ in self.workers:
            self.task_queue.put(None)
            
        # Wait for workers to finish
        for worker in self.workers:
            worker.join(timeout=5)
            
        self.workers.clear()
        self.logger.info("All workers stopped")
        
    def _worker(self, worker_func: Callable[[str], Any]):
        """Worker thread function."""
        thread_name = threading.current_thread().name
        self.logger.info(f"{thread_name} started")
        
        while self.running:
            try:
                url = self.task_queue.get(timeout=1)
                
                if url is None:  # Stop signal
                    break
                    
                # Process URL
                try:
                    result = worker_func(url)
                    self.results_queue.put((True, url, result))
                except Exception as e:
                    self.results_queue.put((False, url, str(e)))
                    
                self.task_queue.task_done()
                
            except queue.Empty:
                continue
                
        self.logger.info(f"{thread_name} stopped")
        
    def get_results(self):
        """Get all available results."""
        results = []
        
        while True:
            try:
                result = self.results_queue.get_nowait()
                results.append(result)
            except queue.Empty:
                break
                
        return results
        
    def is_empty(self):
        """Check if the task queue is empty."""
        return self.task_queue.empty()
        
    def get_queue_size(self):
        """Get the current size of the task queue."""
        return self.task_queue.qsize()