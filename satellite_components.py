# satellite_components.py
import random

class Satellite:
    """
    Represents an autonomous satellite with a target and current location.
    The satellite's location is a tuple of (x, y, z) coordinates.
    """
    def __init__(self, target_location):
        """
        Initializes the Satellite object.

        Args:
            target_location (tuple): The desired coordinates of the satellite.
        """
        self._target_location = list(target_location)
        self._current_location = list(target_location)
        print(f"Satellite initialized. Target Location: {self._target_location}")

    def get_location(self):
        """
        Returns the satellite's current location.

        Returns:
            list: The current coordinates of the satellite.
        """
        return self._current_location

    def set_location(self, new_coordinates):
        """
        Updates the satellite's current location.

        Args:
            new_coordinates (list): The new coordinates for the satellite.
        """
        self._current_location = new_coordinates

    def simulate_drift(self):
        """
        Simulates gradual orbital drift by applying a non-uniform random vector.
        This represents real-world perturbations like atmospheric drag or
        gravitational anomalies.
        """
        drift_vector = [random.uniform(-0.05, 0.05) for _ in range(3)]
        self._current_location = [
            self._current_location[i] + drift_vector[i] for i in range(3)
        ]

class Thruster:
    """
    Represents the satellite's propulsion system used for station-keeping.
    """
    def __init__(self):
        """
        Initializes the Thruster object.
        """
        print("Thruster system is online.")

    def apply_thrust(self, satellite, correction_vector):
        """
        Applies a correction vector to the satellite's location.

        Args:
            satellite (Satellite): The Satellite object to be moved.
            correction_vector (list): The vector representing the thrust needed.

        Returns:
            list: The satellite's new location after correction.
        """
        new_location = [
            satellite.get_location()[i] + correction_vector[i] for i in range(3)
        ]
        satellite.set_location(new_location)
        return new_location

class Sensor:
    """
    Simulates a sensor (like a GPS receiver) that provides the satellite's
    current location data. In a real system, this would be based on sensor readings.
    """
    def __init__(self, satellite):
        """
        Initializes the Sensor object.
        
        Args:
            satellite (Satellite): The satellite object to monitor.
        """
        self._satellite = satellite
        print("Sensor system is active.")

    def get_current_position(self):
        """
        Retrieves the satellite's current location from the simulated sensor.
        
        Returns:
            list: The current coordinates of the satellite.
        """
        # A real sensor might have some noise, so we can add a tiny bit
        # to simulate measurement error.
        current_location = self._satellite.get_location()
        noise = [random.uniform(-1e-4, 1e-4) for _ in range(3)]
        return [current_location[i] + noise[i] for i in range(3)]
