from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QProgressBar
from PyQt6.QtCore import QTimer
from core.events import get_event_manager
from vision.face_recognizer import FaceRecognizer

class RegistrationWindow(QDialog):
    def __init__(self, face_recognizer, parent=None):
        super().__init__(parent)
        self.face_recognizer = face_recognizer
        self.events = get_event_manager()
        self.events = get_event_manager()
        self.current_frame = None
        self.samples_collected = 0
        self.samples_collected = 0
        self.target_samples = 5
        self.is_registering = False
        
        # Guided Poses
        self.poses = [
            "Look Straight Ahead",
            "Turn Head Slightly LEFT",
            "Turn Head Slightly RIGHT", 
            "Tilt Head Slightly UP",
            "Tilt Head Slightly DOWN"
        ]
        
        self.setWindowTitle("Enroll New User")
        self.setModal(True)
        self.resize(300, 150)
        
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Enter User Name:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)
        
        self.status_label = QLabel("Ready to enroll.")
        layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(self.target_samples)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.capture_btn = QPushButton("Start Guided Enrollment (5 Poses)")
        self.capture_btn.clicked.connect(self.start_enrollment)
        layout.addWidget(self.capture_btn)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.capture_sample)
        
        # Subscribe to frame updates to grab the latest one when button clicked
        self.events.frame_processed.connect(self.update_current_frame)

    def update_current_frame(self, frame):
        self.current_frame = frame

    def start_enrollment(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Input Error", "Please enter a name.")
            return

        if self.current_frame is None:
            QMessageBox.warning(self, "Camera Error", "No camera feed available.")
            return
            
        self.is_registering = True
        self.samples_collected = 0
        self.capture_btn.setEnabled(False)
        self.name_input.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Keep looking at the camera...")
        
        # Trigger first pose immediately
        self.next_pose()

    def next_pose(self):
        if self.samples_collected >= self.target_samples:
            self.finish_enrollment(self.name_input.text().strip())
            return
            
        pose_instruction = self.poses[self.samples_collected]
        self.status_label.setText(f"Pose {self.samples_collected + 1}/{self.target_samples}: {pose_instruction}")
        
        # Give user 2 seconds to comply before capturing
        QTimer.singleShot(2000, self.capture_sample)

    def capture_sample(self):
        if not self.is_registering:
            return

        if self.current_frame is None:
            # Retry in a bit if frame missing
            QTimer.singleShot(500, self.capture_sample)
            return

        name = self.name_input.text().strip()
        
        # Try to register this frame
        success = self.face_recognizer.register_face(self.current_frame, name)
        
        if success:
            self.samples_collected += 1
            self.progress_bar.setValue(self.samples_collected)
            # Proceed to next pose
            self.next_pose()
        else:
            self.status_label.setText("No face detected! Please adjust and try again.")
            # Retry same pose in 1 second
            QTimer.singleShot(1000, self.capture_sample)

    def finish_enrollment(self, name):
        self.timer.stop()
        self.is_registering = False
        QMessageBox.information(self, "Success", f"User '{name}' enrolled successfully with {self.target_samples} samples.")
        self.accept()
    
    def closeEvent(self, event):
        self.timer.stop()
        event.accept()
