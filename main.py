# main.py
import time
import datetime
import threading
import sys
import msvcrt # Only for Windows; use a different method for other OS

from satellite_components import Satellite, Thruster, Sensor
from control_algorithm import PIDController
from telemetry import TelemetrySystem, HistoryRecorder

# A global variable to control the loop's state.
# A lock is used for thread-safe access.
loop_is_running = False
loop_lock = threading.Lock()
# A flag to ensure the "paused" message is only printed once.
paused_message_shown = False
# A global variable to control if history recording is enabled.
recording_history = False
history_lock = threading.Lock()

def main_loop(my_satellite, my_thruster, my_sensor, my_controller, my_telemetry, my_history):
    """
    Main autonomous control loop for the simulated CubeSat.
    """
    global loop_is_running
    global paused_message_shown
    global recording_history
    print("🚀 CubeSat Autonomous Station-Keeping System Initiated.")
    print("The loop is currently paused. Press 'r' to resume it, 's' to stop it, 'c' to toggle history recording, 'h' to display history, or 'q' to quit.")

    while True:
        with loop_lock:
            if not loop_is_running:
                if not paused_message_shown:
                    print("Loop paused. Press 'r' to resume...")
                    paused_message_shown = True
                time.sleep(1) # Sleep while paused to avoid a tight loop
                continue
            else:
                paused_message_shown = False # Reset the flag when the loop is running

        # 1. Simulate drift
        my_satellite.simulate_drift()

        # 2. Get current position from the sensor
        current_location = my_sensor.get_current_position()
        target_location = my_satellite._target_location

        # 3. Calculate distance from target to check if correction is needed
        distance_from_target = sum((target_location[i] - current_location[i])**2 for i in range(3))**0.5
        is_on_course = distance_from_target < 0.1 # A simple threshold for correction

        correction_vector = [0.0, 0.0, 0.0]
        if not is_on_course:
            # 4. Use the PID controller to calculate the correction vector
            correction_vector = my_controller.compute_correction(target_location, current_location)

            # 5. Apply the correction using the thruster
            my_thruster.apply_thrust(my_satellite, correction_vector)
            
            # 6. If history recording is enabled, save the drift event.
            with history_lock:
                if recording_history:
                    my_history.record_drift(datetime.datetime.now(), my_satellite.get_location(), distance_from_target, correction_vector)

        # 7. Log the status using the telemetry system
        my_telemetry.log_status(datetime.datetime.now(), current_location, target_location, correction_vector, is_on_course)
        my_telemetry.display_latest_status()

        # 8. Pause to simulate the passage of time between cycles
        time.sleep(1)

def get_input_thread(my_history):
    """
    A separate thread to listen for a single character input without blocking the main loop.
    """
    global loop_is_running
    global recording_history
    while True:
        if sys.platform == 'win32':
            if msvcrt.kbhit():
                char = msvcrt.getch().decode('utf-8').lower()
                with loop_lock:
                    if char == 's':
                        if loop_is_running:
                            print("Stopping the loop...")
                        loop_is_running = False
                    elif char == 'r':
                        if not loop_is_running:
                            print("Resuming the loop...")
                        loop_is_running = True
                    elif char == 'q':
                        print("Quitting program.")
                        sys.exit()
                
                with history_lock:
                    if char == 'c':
                        recording_history = not recording_history
                        if recording_history:
                            print("History recording is now ON.")
                        else:
                            print("History recording is now OFF.")
                    elif char == 'h':
                        print("Displaying history log:")
                        my_history.display_history()

if __name__ == "__main__":
    target_location = (100.0, 200.0, 300.0)

    # Initialize all system components
    my_satellite = Satellite(target_location)
    my_thruster = Thruster()
    my_sensor = Sensor(my_satellite)
    my_telemetry = TelemetrySystem()
    my_history = HistoryRecorder()
    
    # Initialize the PID controller with tuning constants
    # These values would be carefully determined in a real-world scenario
    # Kp: Proportional gain
    # Ki: Integral gain
    # Kd: Derivative gain
    my_controller = PIDController(Kp=0.5, Ki=0.01, Kd=0.1)

    # Start the input listener thread
    input_thread = threading.Thread(target=get_input_thread, args=(my_history,))
    input_thread.daemon = True # This will exit the thread when the main program exits
    input_thread.start()

    try:
        main_loop(my_satellite, my_thruster, my_sensor, my_controller, my_telemetry, my_history)
    except SystemExit:
        print("Program terminated.")
