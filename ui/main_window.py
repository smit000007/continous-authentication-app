import sys
import multiprocessing
import queue
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QStatusBar
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSlot, pyqtSignal

from ui.webcam_widget import WebcamWidget
from ui.registration_window import RegistrationWindow
from ui.face_manager import FaceManagerDialog
from core.events import get_event_manager
from core.presence_monitor import PresenceMonitor
from vision.camera import Camera
from vision.face_recognizer import FaceRecognizer
from system.lock_screen import SystemLocker
from utils.logger import logger
from core.vision_worker import VisionProcess
from core.intruder_logger import IntruderLogger

# Background Thread for Heavy Vision Processing
# Helper thread to pull results from Queue back to Main Thread
class ResultReader(QThread):
    faces_detected = pyqtSignal(object) 
    
    def __init__(self, result_queue):
        super().__init__()
        self.result_queue = result_queue
        self.running = True
        
    def run(self):
        while self.running:
            try:
                # Blocking get is fine here as it's a separate thread just waiting for results
                # But use timeout to allow checking self.running
                faces = self.result_queue.get(timeout=0.1)
                self.faces_detected.emit(faces)
            except queue.Empty:
                continue
    
    def stop(self):
        self.running = False
        self.wait()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Continuous Authentication Using Face Presence")
        self.resize(1000, 700)
        
        # Components
        self.events = get_event_manager()
        self.camera = Camera(camera_index=0)
        self.face_recognizer = FaceRecognizer()
        self.monitor = PresenceMonitor()
        self.locker = SystemLocker()
        self.intruder_logger = IntruderLogger()
        
        # State
        self.cached_faces = [] # Store last known faces for drawing
        
        # UI Setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        # Header
        self.header_layout = QHBoxLayout()
        self.status_label = QLabel("Status: INITIALIZING")
        self.status_label.setObjectName("StatusLabel")
        self.header_layout.addWidget(self.status_label)
        self.header_layout.addStretch()
        
        self.manage_btn = QPushButton("Manage Faces")
        self.manage_btn.clicked.connect(self.open_face_manager)
        self.header_layout.addWidget(self.manage_btn)
        
        self.enroll_btn = QPushButton("Enroll New User")
        self.enroll_btn.clicked.connect(self.open_registration)
        self.header_layout.addWidget(self.enroll_btn)
        self.layout.addLayout(self.header_layout)
        
        # Webcam
        self.webcam_widget = WebcamWidget()
        self.layout.addWidget(self.webcam_widget)
        
        # Footer / Log
        self.footer_label = QLabel("Ready.")
        self.layout.addWidget(self.footer_label)
        
        # Apply Styles
        try:
            with open("ui/styles.qss", "r") as f:
                self.setStyleSheet(f.read())
        except:
            pass
            
        # Connect Signals
        self.events.status_changed.connect(self.update_status)
        self.events.lock_requested.connect(self.locker.lock_workstation)
        self.events.warning_requested.connect(self.show_warning)
        self.events.intruder_detected.connect(self.handle_intruder)
        
        # Start Camera (Internal thread triggers)
        self.camera.start()
        
        # Setup Multiprocessing
        self.frame_queue = multiprocessing.Queue(maxsize=2) # Keep it small to avoid lag
        self.result_queue = multiprocessing.Queue()
        
        self.vision_process = VisionProcess(self.frame_queue, self.result_queue)
        self.vision_process.start()
        
        # Reader thread to bring results back to UI
        self.result_reader = ResultReader(self.result_queue)
        self.result_reader.faces_detected.connect(self.handle_vision_results)
        self.result_reader.start()
        
        # Setup Display Timer (UI Loop - 30 FPS)
        self.display_timer = QTimer()
        self.display_timer.timeout.connect(self.update_display)
        self.display_timer.start(16)

    @pyqtSlot(object)
    def handle_vision_results(self, faces):
        """
        Called when Vision Thread finishes processing a frame.
        """
        self.cached_faces = faces
        self.monitor.process_faces(faces)

    def update_display(self):
        """
        Runs at 30 FPS.
        Zero-Copy Pipeline: Passes raw frame and metadata to widget.
        """
        frame = self.camera.get_frame()
        if frame is None:
            return

        # 1. Update Metadata (Overlay)
        self.webcam_widget.update_faces(self.cached_faces)
        
        # 2. Update Video (Raw BGR)
        self.webcam_widget.update_frame(frame)
        
        # Emit for Registration Window if needed
        self.events.frame_processed.emit(frame)

        # 3. Send to Vision Process
        # Only if queue has space (drop frames if vision is too slow)
        if not self.frame_queue.full():
            try:
                # Put a copy so we don't have race conditions with the UI array
                self.frame_queue.put_nowait(frame.copy())
            except queue.Full:
                pass

    @pyqtSlot(str, str)
    def update_status(self, status, message):
        self.status_label.setText(f"Status: {status}")
        self.status_label.setProperty("state", status)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        self.footer_label.setText(message)

    @pyqtSlot(str)
    def show_warning(self, reason):
        # Could show a dialog or flash the screen
        self.footer_label.setText(f"WARNING: {reason}")
    
    @pyqtSlot(str)
    def handle_intruder(self, reason):
        """Called when PresenceMonitor confirms an intruder before locking."""
        logger.error(f"MainWindow received intruder signal! Reason: {reason}")
        frame = self.camera.get_frame()
        self.intruder_logger.log_intruder(frame, reason)

    def open_registration(self):
        # Pause monitoring so the system doesn't lock while an unauthorized person is registering
        self.monitor.is_paused = True
        
        reg_win = RegistrationWindow(self.face_recognizer, self)
        reg_win.exec()
        
        self.monitor.is_paused = False
        self.monitor.cooldown_until = __import__('time').time() + self.monitor.grace_period_seconds # Reset grace period

    def open_face_manager(self):
        self.monitor.is_paused = True
        
        manager = FaceManagerDialog(self.face_recognizer, self)
        manager.exec()
        
        # Signal process to reload? It reloads on init.
        # Let's restart the process to be safe and load new faces
        self.restart_vision_process()
        
        self.monitor.is_paused = False
        self.monitor.cooldown_until = __import__('time').time() + self.monitor.grace_period_seconds # Reset grace period

    def restart_vision_process(self):
        if self.vision_process.is_alive():
            self.vision_process.terminate()
            self.vision_process.join()
        
        # Drain queues
        while not self.frame_queue.empty(): self.frame_queue.get()
        while not self.result_queue.empty(): self.result_queue.get()
            
        self.vision_process = VisionProcess(self.frame_queue, self.result_queue)
        self.vision_process.start()

    def closeEvent(self, event):
        self.result_reader.stop()
        if self.vision_process.is_alive():
            self.vision_process.terminate()
            self.vision_process.join()
        self.camera.stop()
        self.intruder_logger.stop()
        event.accept()
