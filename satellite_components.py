# satellite_components.py

import random

class Satellite:
    """
    Represents an autonomous satellite with a target and current location.
    """
    def __init__(self, target_location):
        self._target_location = list(target_location)
        self._current_location = list(target_location)

    def get_location(self):
        return self._current_location

    def set_location(self, new_coordinates):
        self._current_location = new_coordinates

    def simulate_drift(self):
        """
        Simulates gradual orbital drift by applying a random vector.
        """
        drift_vector = [random.uniform(-0.05, 0.05) for _ in range(3)]
        self._current_location = [
            self._current_location[i] + drift_vector[i] for i in range(3)
        ]

class Thruster:
    """
    Represents the satellite's propulsion system for station-keeping.
    """
    def apply_thrust(self, satellite, correction_vector):
        new_location = [
            satellite.get_location()[i] + correction_vector[i] for i in range(3)
        ]
        satellite.set_location(new_location)
        return new_location

class Sensor:
    """
    Simulates a sensor that provides the satellite's current location data.
    """
    def __init__(self, satellite):
        self._satellite = satellite

    def get_current_position(self):
        current_location = self._satellite.get_location()
        noise = [random.uniform(-1e-4, 1e-4) for _ in range(3)]
        return [current_location[i] + noise[i] for i in range(3)]