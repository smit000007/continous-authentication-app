import multiprocessing
import queue
import time
from vision.face_recognizer import FaceRecognizer

class VisionProcess(multiprocessing.Process):
    """
    Runs face recognition in a separate process to avoid blocking the UI thread (GIL).
    """
    def __init__(self, frame_queue, result_queue, model_path="data/faces/encodings.pkl"):
        super().__init__()
        self.frame_queue = frame_queue
        self.result_queue = result_queue
        self.model_path = model_path
        self.running = multiprocessing.Event()
        self.running.set()

    def run(self):
        # Re-instantiate FaceRecognizer here to ensure own memory space
        face_recognizer = FaceRecognizer(model_path=self.model_path)
        
        while self.running.is_set():
            try:
                # Get frame with timeout (non-blockingish)
                try:
                    # Get most recent frame, discarding old ones if queue is full
                    frame = self.frame_queue.get(timeout=0.1)
                except queue.Empty:
                    continue

                # Run heavy processing
                results = face_recognizer.identify_faces(frame)
                
                # Push results back
                # Clear old results to keep UI fresh
                while not self.result_queue.empty():
                    try:
                        self.result_queue.get_nowait()
                    except queue.Empty:
                        break
                        
                self.result_queue.put(results)
                
            except Exception as e:
                # print(f"Vision Process Error: {e}")
                pass

    def stop(self):
        self.running.clear()
