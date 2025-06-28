"""
Unit tests for queue management.
"""

import unittest
import time
import threading
from webshot.queue_manager import QueueManager


class TestQueueManager(unittest.TestCase):
    """Test cases for QueueManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.queue_manager = QueueManager()
        
    def tearDown(self):
        """Clean up test fixtures."""
        if self.queue_manager.running:
            self.queue_manager.stop_workers()
            
    def test_add_urls(self):
        """Test adding URLs to queue."""
        urls = ["http://example1.com", "http://example2.com", "http://example3.com"]
        self.queue_manager.add_urls(urls)
        
        self.assertEqual(self.queue_manager.get_queue_size(), 3)
        self.assertFalse(self.queue_manager.is_empty())
        
    def test_worker_processing(self):
        """Test worker thread processing."""
        processed_urls = []
        
        def mock_worker(url):
            processed_urls.append(url)
            return f"Processed: {url}"
            
        # Add URLs and start workers
        urls = ["http://example1.com", "http://example2.com"]
        self.queue_manager.add_urls(urls)
        self.queue_manager.start_workers(2, mock_worker)
        
        # Wait for processing
        time.sleep(1)
        
        # Check results
        results = self.queue_manager.get_results()
        self.assertEqual(len(results), 2)
        self.assertEqual(len(processed_urls), 2)
        
        # Stop workers
        self.queue_manager.stop_workers()
        
    def test_error_handling(self):
        """Test error handling in worker threads."""
        def failing_worker(url):
            raise Exception("Test error")
            
        # Add URL and start worker
        self.queue_manager.add_urls(["http://example.com"])
        self.queue_manager.start_workers(1, failing_worker)
        
        # Wait for processing
        time.sleep(1)
        
        # Check results
        results = self.queue_manager.get_results()
        self.assertEqual(len(results), 1)
        success, url, error = results[0]
        
        self.assertFalse(success)
        self.assertEqual(url, "http://example.com")
        self.assertIn("Test error", error)
        
        # Stop workers
        self.queue_manager.stop_workers()
        
    def test_multiple_workers(self):
        """Test multiple workers processing concurrently."""
        processing_times = {}
        lock = threading.Lock()
        
        def slow_worker(url):
            with lock:
                processing_times[url] = time.time()
            time.sleep(0.5)  # Simulate slow processing
            return f"Processed: {url}"
            
        # Add multiple URLs
        urls = [f"http://example{i}.com" for i in range(4)]
        self.queue_manager.add_urls(urls)
        
        # Start multiple workers
        start_time = time.time()
        self.queue_manager.start_workers(2, slow_worker)
        
        # Wait for completion
        while not self.queue_manager.is_empty():
            time.sleep(0.1)
        time.sleep(1)  # Extra time for workers to finish
        
        # With 2 workers processing 4 URLs that take 0.5s each,
        # it should take about 1 second (2 batches of 2)
        elapsed = time.time() - start_time
        self.assertLess(elapsed, 1.5)
        
        # Stop workers
        self.queue_manager.stop_workers()


if __name__ == '__main__':
    unittest.main()