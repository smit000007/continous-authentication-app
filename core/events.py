from PyQt6.QtCore import QObject, pyqtSignal

class EventManager(QObject):
    """
    Central event hub for the application.
    Inherits from QObject to use PyQt signals/slots.
    """
    # Core Status Events
    status_changed = pyqtSignal(str, str)  # status_code, message
    
    # Vision Events
    frame_processed = pyqtSignal(object)  # Processed frame (with annotations)
    new_face_detected = pyqtSignal(object) # raw frame
    
    # functional Events
    lock_requested = pyqtSignal()
    warning_requested = pyqtSignal(str) # reason
    warning_cleared = pyqtSignal()
    
    # Registration Events
    registration_success = pyqtSignal(str) # Name
    registration_failed = pyqtSignal(str) # Reason

_event_manager = None

def get_event_manager():
    global _event_manager
    if _event_manager is None:
        _event_manager = EventManager()
    return _event_manager
