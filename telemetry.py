# telemetry_and_history.py
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
        
        Args:
            timestamp (datetime.datetime): The time of the log.
            current_location (list): The satellite's current location.
            target_location (list): The target location.
            correction_vector (list): The correction vector applied.
            is_on_course (bool): True if the satellite is on course.
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

    def display_latest_status(self):
        """
        Prints the latest telemetry entry in a formatted way.
        """
        if not self._telemetry_log:
            print("No telemetry data yet.")
            return

        latest_entry = self._telemetry_log[-1]
        timestamp_str = latest_entry["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        curr_loc = latest_entry["current_location"]
        target_loc = latest_entry["target_location"]
        error_mag = latest_entry["error_magnitude"]
        corr_vec = latest_entry["correction_vector"]
        is_on_course = latest_entry["is_on_course"]

        print("="*40)
        print(f"📡 Telemetry Report ({timestamp_str})")
        print("="*40)
        print(f"Current Location: X: {curr_loc[0]:.3f}, Y: {curr_loc[1]:.3f}, Z: {curr_loc[2]:.3f}")
        print(f"Target Location:  X: {target_loc[0]:.3f}, Y: {target_loc[1]:.3f}, Z: {target_loc[2]:.3f}")
        print(f"Distance from Target: {error_mag:.4f} units")
        
        if is_on_course:
            print("Status: ✔ ON COURSE")
        else:
            print("Status: ❌ OFF COURSE - CORRECTING")
            print(f"Applied Correction Vector: X:{corr_vec[0]:.3f}, Y:{corr_vec[1]:.3f}, Z:{corr_vec[2]:.3f}")
        
        print("\n")

class HistoryRecorder:
    """
    A class to record and manage the history of satellite drift events.
    """
    def __init__(self):
        self._drift_history = []
        
    def record_drift(self, timestamp, location, error_magnitude, correction_vector):
        """
        Records an event where the satellite drifted off course.
        
        Args:
            timestamp (datetime.datetime): The time of the drift event.
            location (list): The satellite's location at the time of the drift.
            error_magnitude (float): The magnitude of the error.
            correction_vector (list): The correction applied to fix the drift.
        """
        drift_event = {
            "timestamp": timestamp,
            "location": location,
            "error_magnitude": error_magnitude,
            "correction_vector": correction_vector
        }
        self._drift_history.append(drift_event)
        
    def display_history(self):
        """
        Prints the entire history of recorded drift events.
        """
        if not self._drift_history:
            print("No drift history recorded yet.")
            return
            
        print("="*40)
        print("📋 Satellite Drift History")
        print("="*40)
        for i, event in enumerate(self._drift_history):
            timestamp_str = event["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            location = event["location"]
            error = event["error_magnitude"]
            correction = event["correction_vector"]
            print(f"Event #{i+1} at {timestamp_str}:")
            print(f"  - Location: X:{location[0]:.3f}, Y:{location[1]:.3f}, Z:{location[2]:.3f}")
            print(f"  - Error Magnitude: {error:.4f}")
            print(f"  - Correction Applied: X:{correction[0]:.3f}, Y:{correction[1]:.3f}, Z:{correction[2]:.3f}")
            print("-" * 20)
