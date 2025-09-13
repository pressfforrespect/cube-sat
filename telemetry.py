# telemetry.py

import datetime
import math

class TelemetrySystem:
    """
    Manages the logging and display of real-time satellite telemetry data.
    """
    def __init__(self):
        self._telemetry_log = []

    def log_status(self, timestamp, current_location, target_location, correction_vector, is_on_course):
        """
        Records a new telemetry entry.
        """
        entry = {
            "timestamp": timestamp,
            "current_location": current_location,
            "target_location": target_location,
            "error_magnitude": math.sqrt(sum((target_location[i] - current_location[i])**2 for i in range(3))),
            "correction_vector": correction_vector,
            "is_on_course": is_on_course
        }
        self._telemetry_log.append(entry)