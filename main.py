import customtkinter as ctk
import time
import datetime
import threading
from tkinter import END, scrolledtext, Canvas
import math
import sys
import random
import cv2
from PIL import Image, ImageTk

# Import custom modules
from satellite_components import Satellite, Thruster, Sensor
from control_algorithm import PIDController
from telemetry import TelemetrySystem
from history import HistoryRecorder
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Set the appearance mode and default color theme for the GUI
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class SatelliteGUI(ctk.CTk):
    """
    Main application window for the satellite control system GUI.
    This version implements a new three-column layout with
    telemetry/video on the left, charts in the middle, and a narrower
    history panel on the right.
    """
    def __init__(self, target_location):
        super().__init__()

        # System initialization
        self.my_satellite = Satellite(target_location)
        self.my_thruster = Thruster()
        self.my_sensor = Sensor(self.my_satellite)
        self.my_telemetry = TelemetrySystem()
        self.my_history = HistoryRecorder()
        self.my_controller = PIDController(Kp=0.5, Ki=0.01, Kd=0.1)

        # Simulation state
        self.loop_is_running = False
        self.recording_history = False
        self.loop_lock = threading.Lock()
        self.paused = True
        self.status_text = "Paused"
        
        # Video playback properties
        self.is_video_playing = False
        # The 'r' before the string creates a "raw string" which prevents Python
        # from interpreting backslashes as escape characters.
        video_path = r"C:\Users\KZE\Desktop\final\assets\CubeSat_Animation.mp4" 
        self.cap = cv2.VideoCapture(video_path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) if self.cap.isOpened() else 30
        self.frame_delay = int(1000 / self.fps) # Delay in milliseconds

        # Data for plots
        self.drift_data = []
        self.correction_counts = []

        # GUI setup
        self.title("CubeSat Autonomous Station-Keeping System")
        self.geometry("1800x950") # Adjusted size for new layout
        # Changed column weights to adjust frame sizes
        self.columnconfigure(0, weight=2) # Left Frame (expanded)
        self.columnconfigure(1, weight=4) # Middle Frame (widest)
        self.columnconfigure(2, weight=1) # Right Frame (narrowed)
        self.rowconfigure(0, weight=1)

        # Left Frame: Telemetry, Video Placeholder, and Buttons
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.left_frame.columnconfigure(0, weight=1)
        # Configure rows to make the telemetry and video placeholders equally expandable
        self.left_frame.rowconfigure(1, weight=1) 
        self.left_frame.rowconfigure(3, weight=1)
        self.left_frame.rowconfigure(4, weight=0) 

        # Telemetry display widgets
        self.telemetry_label = ctk.CTkLabel(self.left_frame, text="Real Time Telemetry", font=ctk.CTkFont(size=20, weight="bold"))
        self.telemetry_label.grid(row=0, column=0, pady=(20, 10), sticky="ew")

        # Increased font size to 16 for better visibility
        self.telemetry_text = ctk.CTkTextbox(self.left_frame, wrap="word", font=("Helvetica", 16))
        self.telemetry_text.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Satellite Visualization placeholder
        self.viz_label = ctk.CTkLabel(self.left_frame, text="Satellite Visualization", font=ctk.CTkFont(size=16))
        self.viz_label.grid(row=2, column=0, pady=(20, 10), sticky="ew")
        
        # This is the new widget for video playback
        self.video_label = ctk.CTkLabel(self.left_frame, text="Video loading...")
        self.video_label.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

        # Control buttons
        self.button_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.button_frame.grid(row=4, column=0, pady=(10, 0), sticky="ew")
        self.button_frame.columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        self.start_button = ctk.CTkButton(self.button_frame, text="Start Simulation", command=self.start_loop)
        self.start_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.stop_button = ctk.CTkButton(self.button_frame, text="Pause Simulation", command=self.stop_loop)
        self.stop_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.record_button = ctk.CTkButton(self.button_frame, text="Start Recording", command=self.toggle_recording)
        self.record_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        self.clear_history_button = ctk.CTkButton(self.button_frame, text="Clear History", command=self.clear_history, fg_color="#E74C3C", hover_color="#C0392B")
        self.clear_history_button.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        self.quit_button = ctk.CTkButton(self.button_frame, text="Quit", command=self.on_closing, fg_color="#E74C3C", hover_color="#C0392B")
        self.quit_button.grid(row=0, column=4, padx=5, pady=5, sticky="ew")

        # Middle Frame: Charts
        self.middle_frame = ctk.CTkFrame(self)
        self.middle_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.middle_frame.columnconfigure(0, weight=1)
        self.middle_frame.rowconfigure(0, weight=1)
        self.middle_frame.rowconfigure(1, weight=1)

        # Figure for Correction Count
        self.fig_corr, self.ax_corr = plt.subplots(figsize=(8, 4))
        self.fig_corr.set_facecolor("#2b2b2b")
        self.ax_corr.set_facecolor("#2b2b2b")
        self.ax_corr.tick_params(colors='white')
        self.ax_corr.xaxis.label.set_color('white')
        self.ax_corr.yaxis.label.set_color('white')
        self.ax_corr.spines['bottom'].set_color('white')
        self.ax_corr.spines['left'].set_color('white')
        self.ax_corr.spines['top'].set_visible(False)
        self.ax_corr.spines['right'].set_visible(False)
        self.canvas_corr = FigureCanvasTkAgg(self.fig_corr, master=self.middle_frame)
        self.canvas_corr_widget = self.canvas_corr.get_tk_widget()
        self.canvas_corr_widget.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.ax_corr.set_title("Correction Count Over Time", color='white')
        self.ax_corr.set_xlabel("Time (s)", color='white')
        self.ax_corr.set_ylabel("Correction Count", color='white')

        # Figure for Orbital Drift
        self.fig_drift, self.ax_drift = plt.subplots(figsize=(8, 4))
        self.fig_drift.set_facecolor("#2b2b2b")
        self.ax_drift.set_facecolor("#2b2b2b")
        self.ax_drift.tick_params(colors='white')
        self.ax_drift.xaxis.label.set_color('white')
        self.ax_drift.yaxis.label.set_color('white')
        self.ax_drift.spines['bottom'].set_color('white')
        self.ax_drift.spines['left'].set_color('white')
        self.ax_drift.spines['top'].set_visible(False)
        self.ax_drift.spines['right'].set_visible(False)
        self.canvas_drift = FigureCanvasTkAgg(self.fig_drift, master=self.middle_frame)
        self.canvas_drift_widget = self.canvas_drift.get_tk_widget()
        self.canvas_drift_widget.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.ax_drift.set_title("Orbital Drift Over Time", color='white')
        self.ax_drift.set_xlabel("Time (s)", color='white')
        self.ax_drift.set_ylabel("Drift Magnitude", color='white')
        
        # Right Frame: History
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=2, padx=20, pady=20, sticky="nsew")
        self.right_frame.columnconfigure(0, weight=1)
        self.right_frame.rowconfigure(1, weight=1)
        
        self.history_label = ctk.CTkLabel(self.right_frame, text="History", font=ctk.CTkFont(size=20, weight="bold"))
        self.history_label.grid(row=0, column=0, pady=(20, 10), sticky="ew")

        # Updated history text box with a dark gray background to match the theme
        self.history_text = scrolledtext.ScrolledText(self.right_frame, wrap="word", font=("Helvetica", 10), height=30, bg="#2b2b2b", fg="white", insertbackground="white")
        self.history_text.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")


        # Start the simulation loop in a separate thread
        self.simulation_thread = threading.Thread(target=self.main_loop, daemon=True)
        self.simulation_thread.start()

    def update_video_frame(self):
        """
        Reads a single frame from the video and updates the video label.
        This function schedules itself to run at the video's FPS.
        """
        if self.is_video_playing and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                # Loop video from the beginning if it ends
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
            
            if ret:
                # Convert frame to a format suitable for CTkLabel
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                
                # Resize the image to fit the label, maintaining aspect ratio
                label_width = self.video_label.winfo_width()
                label_height = self.video_label.winfo_height()
                if label_width > 0 and label_height > 0:
                    img.thumbnail((label_width, label_height), Image.Resampling.LANCZOS)
                    img_tk = ctk.CTkImage(light_image=img, size=img.size)
                    self.video_label.configure(image=img_tk, text="")
                
                # Schedule the next frame update
                self.after(self.frame_delay, self.update_video_frame)
            else:
                self.video_label.configure(text="Video playback error.")

    def update_telemetry_display(self):
        """Updates the telemetry text box with the latest status."""
        self.telemetry_text.delete(1.0, END) # Clear old text
        log_str = f"Status: {self.status_text}\n\n"
        
        latest_entry = self.my_telemetry._telemetry_log[-1] if self.my_telemetry._telemetry_log else None
        
        if latest_entry:
            timestamp_str = latest_entry["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            curr_loc = latest_entry["current_location"]
            target_loc = latest_entry["target_location"]
            error_mag = latest_entry["error_magnitude"]
            corr_vec = latest_entry["correction_vector"]
            is_on_course = latest_entry["is_on_course"]
            
            log_str += f"Location: X:{curr_loc[0]:.3f}, Y:{curr_loc[1]:.3f}, Z:{curr_loc[2]:.3f}\n"
            log_str += f"Target:   X:{target_loc[0]:.3f}, Y:{target_loc[1]:.3f}, Z:{target_loc[2]:.3f}\n"
            log_str += f"Error:    {error_mag:.4f} units\n"
            log_str += f"Correction: X:{corr_vec[0]:.3f}, Y:{corr_vec[1]:.3f}, Z:{corr_vec[2]:.3f}\n"
            
        self.telemetry_text.insert(END, log_str)

    def update_history_display(self):
        """Updates the history text box with the latest recorded drift event."""
        drift_history = self.my_history.get_drift_history()
        
        # Clear the history text box and re-populate it with the full log
        self.history_text.delete(1.0, END)
        for event in drift_history:
            timestamp_str = event["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            location = event["location"]
            error = event["error_magnitude"]
            correction = event["correction_vector"]
            
            history_str = f"Event at {timestamp_str}:\n"
            history_str += f"  - Location: X:{location[0]:.3f}, Y:{location[1]:.3f}, Z:{location[2]:.3f}\n"
            history_str += f"  - Error Magnitude: {error:.4f}\n"
            history_str += f"  - Correction Applied: X:{correction[0]:.3f}, Y:{correction[1]:.3f}, Z:{correction[2]:.3f}\n"
            history_str += "-" * 20 + "\n"
            self.history_text.insert(END, history_str)

        self.history_text.see(END)

    def update_plots(self):
        """Updates the matplotlib plots with new data."""
        self.ax_corr.clear()
        self.ax_corr.set_title("Correction Count Over Time", color='white')
        self.ax_corr.set_xlabel("Time (s)", color='white')
        self.ax_corr.set_ylabel("Correction Count", color='white')
        self.ax_corr.plot(range(len(self.correction_counts)), self.correction_counts, marker='o', color='cyan')
        self.canvas_corr.draw()

        self.ax_drift.clear()
        self.ax_drift.set_title("Orbital Drift Over Time", color='white')
        self.ax_drift.set_xlabel("Time (s)", color='white')
        self.ax_drift.set_ylabel("Drift Magnitude", color='white')
        self.ax_drift.plot(range(len(self.drift_data)), self.drift_data, marker='o', color='yellow')
        self.canvas_drift.draw()

    def start_loop(self):
        """Starts the simulation loop and video playback."""
        with self.loop_lock:
            self.loop_is_running = True
            self.paused = False
            self.status_text = "Running"
            self.update_telemetry_display()
            self.is_video_playing = True
            self.update_video_frame() # Start the video playback loop

    def stop_loop(self):
        """Pauses the simulation loop and video playback."""
        with self.loop_lock:
            self.loop_is_running = False
            self.paused = True
            self.status_text = "Paused"
            self.update_telemetry_display()
            self.is_video_playing = False
    
    def toggle_recording(self):
        """Toggles history recording on and off."""
        with self.loop_lock:
            self.recording_history = not self.recording_history
            if self.recording_history:
                self.record_button.configure(text="Stop Recording")
            else:
                self.record_button.configure(text="Start Recording")
                
    def clear_history(self):
        """Clears the history display and the recorded history data."""
        self.my_history.clear_history()
        self.history_text.delete(1.0, END)
        self.drift_data.clear()
        self.correction_counts.clear()
        self.update_plots()

    def main_loop(self):
        """
        Main autonomous control loop for the simulated CubeSat.
        """
        correction_count = 0
        while True:
            with self.loop_lock:
                if self.paused:
                    time.sleep(1) # Sleep while paused
                    continue

            # 1. Simulate drift
            self.my_satellite.simulate_drift()

            # 2. Get current position from the sensor
            current_location = self.my_sensor.get_current_position()
            target_location = self.my_satellite._target_location

            # 3. Calculate distance from target
            distance_from_target = math.sqrt(sum((target_location[i] - current_location[i])**2 for i in range(3)))
            is_on_course = distance_from_target < 0.1 # Threshold for correction

            correction_vector = [0.0, 0.0, 0.0]
            if not is_on_course:
                # 4. Use the PID controller to calculate the correction vector
                correction_vector = self.my_controller.compute_correction(target_location, current_location)

                # 5. Apply the correction using the thruster
                self.my_thruster.apply_thrust(self.my_satellite, correction_vector)
                
                correction_count += 1
                
                # 6. If history recording is enabled, save the drift event.
                if self.recording_history:
                    self.my_history.record_drift(datetime.datetime.now(), self.my_satellite.get_location(), distance_from_target, correction_vector)
                    # Update history display from the main thread
                    self.after(0, self.update_history_display)
            
            # 7. Update plot data
            self.drift_data.append(distance_from_target)
            self.correction_counts.append(correction_count)

            # 8. Log the status using the telemetry system
            self.my_telemetry.log_status(datetime.datetime.now(), current_location, target_location, correction_vector, is_on_course)
            self.after(0, self.update_telemetry_display)
            self.after(0, self.update_plots)

            # 9. Pause to simulate the passage of time
            time.sleep(1)

    def on_closing(self):
        """Handles a graceful exit of the application."""
        self.cap.release()
        self.destroy()
        sys.exit()
        
if __name__ == "__main__":
    from login import LoginPage
    def launch_main_app():
        target_location = (1000, 500, 200)
        app = SatelliteGUI(target_location=target_location)
        app.mainloop()

    login_app = LoginPage(launch_main_app)
    login_app.mainloop()
    #target_location = (100.0, 200.0, 300.0)
    #app = SatelliteGUI(target_location)
    #app.mainloop()
