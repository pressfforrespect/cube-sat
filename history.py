# history.py

import datetime

class HistoryRecorder:
    """
    A class to record and manage the history of satellite drift events.
    """
    def __init__(self):
        self._drift_history = []
        
    def record_drift(self, timestamp, location, error_magnitude, correction_vector):
        """
        Records an event where the satellite drifted off course.
        """
        drift_event = {
            "timestamp": timestamp,
            "location": location,
            "error_magnitude": error_magnitude,
            "correction_vector": correction_vector
        }
        self._drift_history.append(drift_event)

    def get_drift_history(self):
        """
        Returns the list of recorded drift events.
        """
        return self._drift_history
        
    def clear_history(self):
        """
        Clears the recorded drift history.
        """
        self._drift_history = []