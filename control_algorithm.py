# control_algorithm.py

class PIDController:
    """
    A Proportional-Integral-Derivative (PID) controller for autonomous
    station-keeping.
    
    Kp (Proportional): Corrects based on the current error.
    Ki (Integral): Corrects for long-term steady-state errors.
    Kd (Derivative): Corrects for the rate of change of the error.
    """
    def __init__(self, Kp, Ki, Kd):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        
        # Internal state for integral and derivative components
        self._integral = [0.0, 0.0, 0.0]
        self._previous_error = [0.0, 0.0, 0.0]
        
    def compute_correction(self, target_location, current_location):
        """
        Calculates the correction vector based on PID logic.
        
        Args:
            target_location (list): The desired coordinates.
            current_location (list): The current measured coordinates.
            
        Returns:
            list: The calculated correction vector to apply.
        """
        error = [target_location[i] - current_location[i] for i in range(3)]
        
        self._integral = [self._integral[i] + error[i] for i in range(3)]
        
        derivative = [error[i] - self._previous_error[i] for i in range(3)]
        self._previous_error = error
        
        proportional_term = [self.Kp * e for e in error]
        integral_term = [self.Ki * i for i in self._integral]
        derivative_term = [self.Kd * d for d in derivative]
        
        correction = [
            proportional_term[i] + integral_term[i] + derivative_term[i] for i in range(3)
        ]
        
        return correction