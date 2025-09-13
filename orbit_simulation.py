# orbit_simulation.py

import customtkinter as ctk
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D

class OrbitSimulationFrame(ctk.CTkFrame):
    """
    A GUI frame for simulating and visualizing a satellite's orbit,
    designed to be embedded in a larger application.
    """
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Matplotlib 3D Plot
        self.plot_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.plot_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.fig = Figure(figsize=(7, 7), dpi=100, facecolor="#2b2b2b")
        self.axes = self.fig.add_subplot(111, projection='3d')
        self.axes.set_facecolor("#2b2b2b")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

        # Orbital Parameters
        self.R_earth = 6371
        self.theta_index = 0
        self.num_points = 500
        self.theta = np.linspace(0, 2 * np.pi, self.num_points)
        self.is_animating = False  # Animation control flag

        # Controls Frame
        self.controls_frame = ctk.CTkFrame(self)
        self.controls_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        title_label = ctk.CTkLabel(self.controls_frame, text="Orbit Controls", font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(pady=20, padx=20)

        self.altitude_label = ctk.CTkLabel(self.controls_frame, text="Altitude (km): 500")
        self.altitude_label.pack(pady=(10, 0))
        self.altitude_slider = ctk.CTkSlider(self.controls_frame, from_=200, to=2000, command=self.update_plot)
        self.altitude_slider.set(500)
        self.altitude_slider.pack(pady=10, padx=20, fill="x")

        self.inclination_label = ctk.CTkLabel(self.controls_frame, text="Inclination (°): 45")
        self.inclination_label.pack(pady=(10, 0))
        self.inclination_slider = ctk.CTkSlider(self.controls_frame, from_=0, to=180, command=self.update_plot)
        self.inclination_slider.set(45)
        self.inclination_slider.pack(pady=10, padx=20, fill="x")

        self.ecc_label = ctk.CTkLabel(self.controls_frame, text="Eccentricity: 0.00")
        self.ecc_label.pack(pady=(10, 0))
        self.ecc_slider = ctk.CTkSlider(self.controls_frame, from_=0, to=90, command=self.update_plot)
        self.ecc_slider.set(0)
        self.ecc_slider.pack(pady=10, padx=20, fill="x")

        self.update_plot()
        self.animate_satellite() # Start the animation loop

    def compute_orbit(self):
        altitude = self.altitude_slider.get()
        inclination = self.inclination_slider.get()
        eccentricity = self.ecc_slider.get() / 100.0
        a = self.R_earth + altitude
        r = a * (1 - eccentricity**2) / (1 + eccentricity * np.cos(self.theta))
        x = r * np.cos(self.theta)
        y = r * np.sin(self.theta)
        z = np.zeros_like(x)
        inc_rad = np.radians(inclination)
        y_new = y * np.cos(inc_rad)
        z_new = y * np.sin(inc_rad)
        self.x, self.y, self.z = x, y_new, z_new

    def plot_orbit(self):
        self.axes.clear()
        u, v = np.mgrid[0:2*np.pi:40j, 0:np.pi:20j]
        xe, ye, ze = self.R_earth * np.cos(u) * np.sin(v), self.R_earth * np.sin(u) * np.sin(v), self.R_earth * np.cos(v)
        self.axes.plot_surface(xe, ye, ze, color="#3b82f6", alpha=0.4, rstride=2, cstride=2)
        self.axes.plot(self.x, self.y, self.z, "r-", label="Orbit Path")
        idx = self.theta_index % self.num_points
        self.axes.scatter(self.x[idx], self.y[idx], self.z[idx], color="white", s=60, depthshade=True, label="Satellite")
        self.axes.set_xlabel("X (km)", color='white')
        self.axes.set_ylabel("Y (km)", color='white')
        self.axes.set_zlabel("Z (km)", color='white')
        self.axes.tick_params(axis='x', colors='white')
        self.axes.tick_params(axis='y', colors='white')
        self.axes.tick_params(axis='z', colors='white')
        max_range = np.array([self.x.max()-self.x.min(), self.y.max()-self.y.min(), self.z.max()-self.z.min()]).max() / 2.0
        mid_x, mid_y, mid_z = (self.x.max()+self.x.min())*0.5, (self.y.max()+self.y.min())*0.5, (self.z.max()+self.z.min())*0.5
        self.axes.set_xlim(mid_x - max_range, mid_x + max_range)
        self.axes.set_ylim(mid_y - max_range, mid_y + max_range)
        self.axes.set_zlim(mid_z - max_range, mid_z + max_range)
        self.canvas.draw()

    def update_plot(self, event=None):
        alt_val = self.altitude_slider.get()
        inc_val = self.inclination_slider.get()
        ecc_val = self.ecc_slider.get() / 100.0
        self.altitude_label.configure(text=f"Altitude (km): {alt_val:.0f}")
        self.inclination_label.configure(text=f"Inclination (°): {inc_val:.0f}")
        self.ecc_label.configure(text=f"Eccentricity: {ecc_val:.2f}")
        self.compute_orbit()
        self.plot_orbit()

    def start_animation(self):
        """Starts the satellite animation."""
        self.is_animating = True

    def stop_animation(self):
        """Stops the satellite animation."""
        self.is_animating = False

    def animate_satellite(self):
        if self.is_animating:
            self.theta_index = (self.theta_index + 1)
            self.plot_orbit()
        self.after(50, self.animate_satellite)
