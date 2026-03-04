import ctypes
from utils.logger import logger
import json

class SystemLocker:
    """
    Handles OS-level locking actions.
    """
    def __init__(self, config_path="data/config.json"):
        self.config_path = config_path

    def _is_debug_mode(self):
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                return config.get("debug_mode", False)
        except Exception:
            return False

    def lock_workstation(self):
        """
        Locks the Windows workstation.
        If debug_mode is True, effectively logs the action without locking.
        """
        if self._is_debug_mode():
            logger.info("[DEBUG] System Lock Requested! (Skipped due to debug mode)")
            return

        try:
            logger.warning("Locking Workstation...")
            ctypes.windll.user32.LockWorkStation()
        except Exception as e:
            logger.error(f"Failed to lock workstation: {e}")
