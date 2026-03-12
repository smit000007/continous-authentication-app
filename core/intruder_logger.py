import os
import cv2
import threading
import queue
import time
import csv
from datetime import datetime
from utils.logger import logger

class IntruderLogger:
    """
    Handles saving intruder photographs and logging events asynchronously.
    Runs in a background thread to prevent UI or Camera lag.
    """
    def __init__(self, log_dir="data/logs"):
        self.log_dir = log_dir
        self.photos_dir = os.path.join(log_dir, "photos")
        self.csv_path = os.path.join(log_dir, "intruders.csv")
        
        # Ensure directories exist
        os.makedirs(self.photos_dir, exist_ok=True)
        
        # Initialize CSV header if new file
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Status", "Message", "Photo_File"])

        # Threading setup
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.running = True
        self.thread.start()
        
        # Cooldown Tracker (1 photo per minute)
        self.last_log_time = 0
        self.cooldown_seconds = 60

    def log_intruder(self, frame_bgr, message="Unauthorized Face Detected"):
        """
        Public method to submit an intruder frame for logging.
        """
        now = time.time()
        if now - self.last_log_time < self.cooldown_seconds:
            logger.warning("IntruderLogger: Skipping photo capture due to cooldown.")
            return
            
        self.last_log_time = now
        logger.warning(f"IntruderLogger: Queuing intruder event - {message}")
        frame_copy = frame_bgr.copy() if frame_bgr is not None else None
        
        self.queue.put((frame_copy, message, datetime.now()))

    def _worker(self):
        """Background thread that actually writes to disk."""
        while self.running:
            try:
                frame, message, timestamp = self.queue.get(timeout=1.0)
                
                if frame is None:
                    logger.error("IntruderLogger: Received None frame! Cannot save photo.")
                else:
                    logger.debug(f"IntruderLogger: Received frame of shape {frame.shape}")
                
                # Format timestamp
                time_str = timestamp.strftime("%Y%m%d_%H%M%S")
                date_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                
                # 1. Save Photo
                photo_filename = f"intruder_{time_str}.jpg"
                photo_path = os.path.join(self.photos_dir, photo_filename)
                
                if frame is not None:
                    # Save as compressed JPG to save space
                    success = cv2.imwrite(photo_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                    if not success:
                        photo_filename = "ERROR_SAVING_IMAGE"
                else:
                    photo_filename = "NO_IMAGE_PROVIDED"
                    
                # 2. Write to CSV
                try:
                    with open(self.csv_path, mode='a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([date_str, "INTRUDER", message, photo_filename])
                    logger.warning(f"Intruder logged to {self.csv_path} and photo saved to {photo_filename}")
                except Exception as e:
                    logger.error(f"Failed to write to intruder CSV: {e}")
                    
                self.queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"IntruderLogger worker error: {e}")

    def stop(self):
        self.running = False
        self.thread.join(timeout=2.0)
