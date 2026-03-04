import face_recognition
import pickle
import os
import cv2
import numpy as np
from utils.logger import logger

class FaceRecognizer:
    """
    Handles face detection and recognition logic.
    Manages known face encodings.
    """
    def __init__(self, model_path="data/faces/encodings.pkl", confidence_threshold=0.5):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.known_face_encodings = []
        self.known_face_names = []
        self.load_encodings()

    def load_encodings(self):
        """Loads face encodings from disk."""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, "rb") as f:
                    data = pickle.load(f)
                    self.known_face_encodings = data.get("encodings", [])
                    self.known_face_names = data.get("names", [])
                logger.info(f"Loaded {len(self.known_face_names)} known faces from {self.model_path}")
            except Exception as e:
                logger.error(f"Failed to load encodings: {e}")
        else:
            logger.info("No existing encodings found. Starting fresh.")

    def save_encodings(self):
        """Saves current face encodings to disk."""
        data = {
            "encodings": self.known_face_encodings,
            "names": self.known_face_names
        }
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            with open(self.model_path, "wb") as f:
                pickle.dump(data, f)
            logger.info(f"Saved {len(self.known_face_names)} faces to {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to save encodings: {e}")

    def register_face(self, frame, name):
        """
        Detects and encodes a face from the frame, associating it with a name.
        Returns:
            bool: True if successful, False otherwise.
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb_frame)

        if len(boxes) == 0:
            logger.warning("Registration failed: No faces found")
            return False
            
        # Select largest face if multiple
        target_box = boxes[0]
        if len(boxes) > 1:
            logger.warning(f"Registration: Found {len(boxes)} faces. Selecting largest.")
            max_area = 0
            for box in boxes:
                top, right, bottom, left = box
                area = (bottom - top) * (right - left)
                if area > max_area:
                    max_area = area
                    target_box = box
            boxes = [target_box] # Restrict to just the largest one

        try:
            encoding = face_recognition.face_encodings(rgb_frame, boxes)[0]
            self.known_face_encodings.append(encoding)
            self.known_face_names.append(name)
            self.save_encodings()
            logger.info(f"Registered new face: {name}")
            return True
        except Exception as e:
            logger.error(f"Error during registration: {e}")
            return False

    def identify_faces(self, frame):
        """
        Identifies faces in the given frame.
        Returns:
            list[dict]: A list of results [{'name': 'Unknown'|'Name', 'location': (top, right, bottom, left)}]
        """
        # Use full resolution (640x480). 
        # Revert: Enable upsampling (default=1) to ensure we find faces accurately.
        # Multiprocessing handles the speed, so we can afford the CPU cost for better accuracy.
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        face_locations = face_recognition.face_locations(rgb_frame)
        if not face_locations:
            return []

        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        results = []

        for encoding, location in zip(face_encodings, face_locations):
            name = "Unknown"
            if self.known_face_encodings:
                matches = face_recognition.compare_faces(
                    self.known_face_encodings, encoding, tolerance=self.confidence_threshold
                )
                face_distances = face_recognition.face_distance(self.known_face_encodings, encoding)
                
                if True in matches:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
            
            results.append({"name": name, "location": location})

        return results

    def get_enrolled_faces(self):
        """Returns a list of unique enrolled names."""
        return sorted(list(set(self.known_face_names)))

    def delete_face(self, name):
        """
        Deletes all encodings associated with a specific name.
        """
        if name not in self.known_face_names:
            return False
            
        # Filter out the indices to remove
        new_encodings = []
        new_names = []
        
        for encoding, known_name in zip(self.known_face_encodings, self.known_face_names):
            if known_name != name:
                new_encodings.append(encoding)
                new_names.append(known_name)
                
        self.known_face_encodings = new_encodings
        self.known_face_names = new_names
        self.save_encodings()
        logger.info(f"Deleted user: {name}")
        return True
