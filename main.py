# main.py

import sys
import time
import datetime
import threading
import math
from tkinter import END, scrolledtext
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Import custom modules
from satellite_components import Satellite, Thruster, Sensor
from control_algorithm import PIDController
from telemetry import TelemetrySystem
from history import HistoryRecorder
from orbit_simulation import OrbitSimulationFrame
from login import LoginPage # Import the LoginPage class

class SatelliteGUI(ctk.CTk):
    """
    Main application window for the satellite control system GUI.
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
        
        self.drift_data = []
        self.correction_counts = []

        self.setup_gui()

        # Start the simulation loop thread
        self.simulation_thread = threading.Thread(target=self.main_loop, daemon=True)
        self.simulation_thread.start()

    def setup_gui(self):
        """Configures and places all the GUI widgets."""
        self.title("CubeSat Autonomous Station-Keeping System")
        self.geometry("1800x950")
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=4)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)

        # Left Frame
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.left_frame.columnconfigure(0, weight=1)
        self.left_frame.rowconfigure(1, weight=1) 
        self.left_frame.rowconfigure(3, weight=2)
        self.left_frame.rowconfigure(4, weight=0) 

        self.telemetry_label = ctk.CTkLabel(self.left_frame, text="Real Time Telemetry", font=ctk.CTkFont(size=20, weight="bold"))
        self.telemetry_label.grid(row=0, column=0, pady=(20, 10), sticky="ew")
        self.telemetry_text = ctk.CTkTextbox(self.left_frame, wrap="word", font=("Helvetica", 16))
        self.telemetry_text.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.viz_label = ctk.CTkLabel(self.left_frame, text="Satellite Visualization", font=ctk.CTkFont(size=16))
        self.viz_label.grid(row=2, column=0, pady=(20, 10), sticky="ew")
        
        # Embed the OrbitSimulationFrame
        self.orbit_simulation_widget = OrbitSimulationFrame(master=self.left_frame)
        self.orbit_simulation_widget.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

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

        # Middle Frame
        self.middle_frame = ctk.CTkFrame(self)
        self.middle_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.middle_frame.columnconfigure(0, weight=1)
        self.middle_frame.rowconfigure(0, weight=1)
        self.middle_frame.rowconfigure(1, weight=1)

        self.fig_corr, self.ax_corr = plt.subplots(figsize=(8, 4))
        self.canvas_corr = self.create_plot(self.fig_corr, self.ax_corr, self.middle_frame, 0, "Correction Count Over Time")
        self.fig_drift, self.ax_drift = plt.subplots(figsize=(8, 4))
        self.canvas_drift = self.create_plot(self.fig_drift, self.ax_drift, self.middle_frame, 1, "Orbital Drift Over Time")
        
        # Right Frame
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=2, padx=20, pady=20, sticky="nsew")
        self.right_frame.columnconfigure(0, weight=1)
        self.right_frame.rowconfigure(1, weight=1)
        
        self.history_label = ctk.CTkLabel(self.right_frame, text="History", font=ctk.CTkFont(size=20, weight="bold"))
        self.history_label.grid(row=0, column=0, pady=(20, 10), sticky="ew")
        self.history_text = scrolledtext.ScrolledText(self.right_frame, wrap="word", font=("Helvetica", 10), bg="#2b2b2b", fg="white", insertbackground="white")
        self.history_text.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    def create_plot(self, fig, ax, master, row, title):
        """Helper method to create and configure a matplotlib plot."""
        fig.set_facecolor("#2b2b2b")
        ax.set_facecolor("#2b2b2b")
        ax.tick_params(colors='white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.set_title(title, color='white')
        canvas = FigureCanvasTkAgg(fig, master=master)
        canvas.get_tk_widget().grid(row=row, column=0, padx=5, pady=5, sticky="nsew")
        return canvas

    def update_telemetry_display(self):
        # ... (method code is unchanged)
        self.telemetry_text.delete(1.0, END)
        log_str = f"Status: {self.status_text}\n\n"
        latest_entry = self.my_telemetry._telemetry_log[-1] if self.my_telemetry._telemetry_log else None
        if latest_entry:
            curr_loc, target_loc = latest_entry["current_location"], latest_entry["target_location"]
            error_mag, corr_vec = latest_entry["error_magnitude"], latest_entry["correction_vector"]
            log_str += f"Location: X:{curr_loc[0]:.3f}, Y:{curr_loc[1]:.3f}, Z:{curr_loc[2]:.3f}\n"
            log_str += f"Target:   X:{target_loc[0]:.3f}, Y:{target_loc[1]:.3f}, Z:{target_loc[2]:.3f}\n"
            log_str += f"Error:    {error_mag:.4f} units\n"
            log_str += f"Correction: X:{corr_vec[0]:.3f}, Y:{corr_vec[1]:.3f}, Z:{corr_vec[2]:.3f}\n"
        self.telemetry_text.insert(END, log_str)

    def update_history_display(self):
        # ... (method code is unchanged)
        self.history_text.delete(1.0, END)
        for event in self.my_history.get_drift_history():
            ts_str = event["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            loc, err, cor = event["location"], event["error_magnitude"], event["correction_vector"]
            hist_str = f"Event at {ts_str}:\n"
            hist_str += f"  - Location: X:{loc[0]:.3f}, Y:{loc[1]:.3f}, Z:{loc[2]:.3f}\n"
            hist_str += f"  - Error Mag: {err:.4f}\n"
            hist_str += f"  - Correction: X:{cor[0]:.3f}, Y:{cor[1]:.3f}, Z:{cor[2]:.3f}\n"
            hist_str += "-" * 20 + "\n"
            self.history_text.insert(END, hist_str)
        self.history_text.see(END)

    def update_plots(self):
        # ... (method code is unchanged)
        self.ax_corr.clear()
        self.ax_corr.set_title("Correction Count Over Time", color='white')
        self.ax_corr.set_xlabel("Times", color='white')
        self.ax_corr.set_ylabel("Correction Count", color='white')
        self.ax_corr.plot(range(len(self.correction_counts)), self.correction_counts, marker='o', color='cyan')
        self.fig_corr.tight_layout()
        self.canvas_corr.draw()

        self.ax_drift.clear()
        self.ax_drift.set_title("Orbital Drift Over Time", color='white')
        self.ax_drift.set_xlabel("Times", color='white')
        self.ax_drift.set_ylabel("Drift Magnitude", color='white')
        self.ax_drift.plot(range(len(self.drift_data)), self.drift_data, marker='o', color='yellow')
        self.fig_drift.tight_layout()
        self.canvas_drift.draw()

    def start_loop(self):
        with self.loop_lock:
            self.loop_is_running = True
            self.paused = False
            self.status_text = "Running"
            self.update_telemetry_display()
        self.orbit_simulation_widget.start_animation()

    def stop_loop(self):
        with self.loop_lock:
            self.loop_is_running = False
            self.paused = True
            self.status_text = "Paused"
            self.update_telemetry_display()
        self.orbit_simulation_widget.stop_animation()
    
    def toggle_recording(self):
        # ... (method code is unchanged)
        with self.loop_lock:
            self.recording_history = not self.recording_history
            self.record_button.configure(text="Stop Recording" if self.recording_history else "Start Recording")
                
    def clear_history(self):
        # ... (method code is unchanged)
        self.my_history.clear_history()
        self.history_text.delete(1.0, END)
        self.drift_data.clear()
        self.correction_counts.clear()
        self.update_plots()

    def main_loop(self):
        # ... (method code is unchanged)
        correction_count = 0
        while True:
            with self.loop_lock:
                if self.paused:
                    time.sleep(1)
                    continue

            self.my_satellite.simulate_drift()
            current_location = self.my_sensor.get_current_position()
            target_location = self.my_satellite._target_location
            distance_from_target = math.sqrt(sum((target_location[i] - current_location[i])**2 for i in range(3)))
            is_on_course = distance_from_target < 0.1
            correction_vector = [0.0, 0.0, 0.0]

            if not is_on_course:
                correction_vector = self.my_controller.compute_correction(target_location, current_location)
                self.my_thruster.apply_thrust(self.my_satellite, correction_vector)
                correction_count += 1
                if self.recording_history:
                    self.my_history.record_drift(datetime.datetime.now(), self.my_satellite.get_location(), distance_from_target, correction_vector)
                    self.after(0, self.update_history_display)
            
            self.drift_data.append(distance_from_target)
            self.correction_counts.append(correction_count)
            self.my_telemetry.log_status(datetime.datetime.now(), current_location, target_location, correction_vector, is_on_course)
            self.after(0, self.update_telemetry_display)
            self.after(0, self.update_plots)
            time.sleep(1)

    def on_closing(self):
        self.destroy()
        sys.exit()

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    def launch_main_app():
        """Initializes and runs the main satellite control GUI."""
        target_location = (100.0, 200.0, 300.0)
        app = SatelliteGUI(target_location=target_location)
        app.mainloop()

    # Start the application by showing the login page first.
    login_app = LoginPage(on_login_success=launch_main_app)
    login_app.mainloop()

