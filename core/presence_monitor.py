import time
from PyQt6.QtCore import QObject, QThread, pyqtSignal, QTimer
from core.events import get_event_manager
from utils.logger import logger
import json

class PresenceMonitor(QObject):
    """
    The Brain. Monitors face data and decides when to warn or lock.
    """
    def __init__(self, config_path="data/config.json"):
        super().__init__()
        self.events = get_event_manager()
        self.load_config(config_path)
        
        # State
        self.last_authorized_seen = time.time()
        self.unauthorized_start_time = None
        self.current_status = "SAFE" # SAFE, WARNING, LOCK_COUNTDOWN
        self.is_paused = False
        
        # Timers
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self._check_state)
        self.check_timer.start(500) # Check every 500ms
        
        # Grace Period (10 seconds on start)
        self.grace_period_seconds = self.config.get("grace_period_seconds", 10)
        self.cooldown_until = time.time() + self.grace_period_seconds
        self._set_status("STARTUP", f"Grace Period: {self.grace_period_seconds}s")

    def load_config(self, config_path):
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except Exception:
            self.config = {}
            
        self.timeout_seconds = self.config.get("timeout_seconds", 5)
        self.warning_time = self.config.get("warning_time_seconds", 3)
        self.lock_on_unauthorized = self.config.get("lock_on_unauthorized", True)

    def process_faces(self, faces):
        """
        Ingest list of identified faces [{'name': '...', 'location': ...}]
        """
        if self.is_paused:
            self._set_status("PAUSED", "Monitoring paused for system operations.")
            return

        now = time.time()
        
        # Check Grace Period
        if now < self.cooldown_until:
            remaining = int(self.cooldown_until - now)
            self._set_status("GRACE", f"System Paused for {remaining}s...")
            return

        authorized_present = False
        unauthorized_present = False
        
        for face in faces:
            # Check if the face name is in the list of enrolled names (if we had access to it)
            # Since we don't, we assume anything that isn't explicitly "Unknown" is the primary user for now
            # But wait, what if it recognizes someone else who is enrolled but shouldn't be at this PC?
            # For this simple prototype, "Unknown" means intruder. 
            if face['name'] != "Unknown":
                authorized_present = True
            else:
                unauthorized_present = True

        # Update timestamps
        if authorized_present:
            self.last_authorized_seen = now
            
        # Decision Logic
        if authorized_present and not unauthorized_present:
            self._set_status("SAFE", "Authorized User Present")
            self.unauthorized_start_time = None
            
        elif authorized_present and unauthorized_present:
            if not self.unauthorized_start_time:
                self.unauthorized_start_time = now
            
            elapsed = now - self.unauthorized_start_time
            if elapsed > self.warning_time:
                if self.lock_on_unauthorized:
                    self._set_status("LOCK", "Unauthorized Person Persisted - Locking System")
                    self.events.intruder_detected.emit("Unauthorized Face Persistent")
                    self.events.lock_requested.emit()
                    # Reset Grace Period after lock to prevent loop
                    self.cooldown_until = time.time() + self.grace_period_seconds
                else:
                    self._set_status("WARNING", f"Intruder detected for {int(elapsed)}s")
                    self.events.warning_requested.emit("Unauthorized Person Detected!")
            else:
                remaining = self.warning_time - elapsed
                self._set_status("WARNING", f"Unauthorized Detection - Locking in {int(remaining)}s")
                self.events.warning_requested.emit("Unauthorized Person! Please leave.")

        elif not authorized_present:
            # User is gone
            
            # If there is an unauthorized person sitting there, log them before locking
            if unauthorized_present:
                if not self.unauthorized_start_time:
                    self.unauthorized_start_time = now
                elapsed = now - self.unauthorized_start_time
                if elapsed > self.warning_time:
                    if self.lock_on_unauthorized:
                        self._set_status("LOCK", "Intruder Detected (Host Absent) - Locking")
                        self.events.intruder_detected.emit("Unauthorized Face (Host Absent)")
                        self.events.lock_requested.emit()
                        self.cooldown_until = time.time() + self.grace_period_seconds
                    else:
                        self._set_status("WARNING", f"Intruder detected for {int(elapsed)}s")
                        self.events.warning_requested.emit("Unauthorized Person Detected!")
                else:
                    remaining = self.warning_time - elapsed
                    self._set_status("WARNING", f"Intruder Detection - Locking in {int(remaining)}s")
                    self.events.warning_requested.emit("Unauthorized Person! Please leave.")
            
            else:
                # Normal User Absent (Empty Room or Face unrecognizable)
                self.unauthorized_start_time = None 
                time_gone = now - self.last_authorized_seen
                
                # IMPORTANT UPDATE: Also take a photo on generic "User Absent" timeout
                # It's better to accidentally take a photo of an empty chair than to miss an intruder.
                
                if time_gone > self.timeout_seconds:
                    self._set_status("LOCK", "User Absent - Locking")
                    self.events.intruder_detected.emit("Snapshot taken at Lock Time (User Absent)")
                    self.events.lock_requested.emit()
                    self.cooldown_until = time.time() + self.grace_period_seconds
                else:
                    remaining = self.timeout_seconds - time_gone
                    self._set_status("WARNING", f"User Absent. Locking in {int(remaining)}s")

    def _set_status(self, status, message):
        if self.current_status != status:
            logger.warning(f"Monitor Status Changed: [{status}] {message}")
            self.current_status = status
            self.events.status_changed.emit(status, message)
            
            if status == "SAFE":
                self.events.warning_cleared.emit()

    def _check_state(self):
        # Periodic check in case no frames are coming in (e.g. camera died)
        # We can implement a "no signal" logic here if needed
        pass
