import cv2
import threading
import time
from utils.logger import logger

class Camera:
    """
    Handles video capture from the webcam in a thread-safe manner.
    """
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None
        self.running = False
        self.lock = threading.Lock()

    def start(self):
        """Starts the camera capture."""
        if self.running:
            return

        logger.info(f"Starting camera at index {self.camera_index}...")
        self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW) # CAP_DSHOW for faster startup on Windows
        
        # Force 640x480 for performance (Fixes GUI lag on 1080p cams)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 60)
        
        if not self.cap.isOpened():
            logger.error(f"Failed to open camera index {self.camera_index}")
            raise RuntimeError("Could not open webcam.")

        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        logger.info("Camera started successfully.")

    def stop(self):
        """Stops the camera capture and releases resources."""
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join(timeout=0.2)
            
        with self.lock:
            if self.cap and self.cap.isOpened():
                self.cap.release()
            self.cap = None
        logger.info("Camera stopped.")

    def _capture_loop(self):
        """Continuously captures frames in a background thread."""
        while self.running and self.cap:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.current_frame = frame
            else:
                time.sleep(0.1)
                
            # Crucial: Sleep extremely briefly to release GIL but minimize latency
            time.sleep(0.001)

    def get_frame(self):
        """
        Returns the latest captured frame. Non-blocking.
        """
        with self.lock:
            if not getattr(self, 'current_frame', None) is None:
                return self.current_frame.copy()
            return None

    def is_active(self):
        return self.running and self.cap and self.cap.isOpened()
