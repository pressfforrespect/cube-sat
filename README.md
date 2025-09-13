CubeSat Mission Control Software

!

A desktop application designed to simulate, visualize, and control the station-keeping maneuvers of a CubeSat. This software provides a graphical user interface for monitoring telemetry, visualizing the satellite's orbit in 3D, and observing the autonomous course correction system in action.

The core of the simulation is a PID (Proportional-Integral-Derivative) controller that automatically calculates and applies thrust to counteract orbital drift, ensuring the satellite remains at its target location.
✨ Features

    3D Orbit Visualization: A real-time, interactive 3D plot displays the satellite's orbit around a central body (Earth).

    Automated Station-Keeping: A PID controller simulates autonomous course corrections to maintain the satellite's target position.

    Live Telemetry Plotting: Real-time graphs for positional error and correction thrust magnitude.

    Event Logging: A detailed log records every time the satellite drifts off-course and a correction is applied.

    Modern GUI: The user interface is built with CustomTkinter for a clean and modern look.

    Secure Login: A simple login window to simulate a secure control environment.

    Centralized Configuration: All simulation parameters, PID gains, and theme settings are managed in a single config.py file for easy tuning.

    Performance Optimized: The application uses numpy for efficient vector calculations and collections.deque with a fixed size for logging to ensure stable memory usage over long sessions.

📸 Screenshots

(It is highly recommended to add screenshots of your application here. For example, the login screen and the main dashboard.)

Login Window
[Your Login Screen Screenshot Here]

Main Dashboard
[Your Main Dashboard Screenshot Here]
🛠️ Technology Stack

    Language: Python 3

    GUI: CustomTkinter

    Plotting & Visualization: Matplotlib

    Numerical Operations: NumPy

    Image Handling: Pillow (PIL)

📂 Project Structure

The project is organized into several modules, each with a specific responsibility:

.
├── assets/
│   └── login.png        # Background image for the login screen
├── main.py              # Main application entry point, integrates all modules
├── login.py             # Handles the user authentication window
├── config.py            # Centralized configuration for all settings
├── satellite_components.py # Defines Satellite, Thruster, and Sensor classes
├── control_algorithm.py # Implements the PID station-keeping logic
├── telemetry.py         # Manages logging of real-time telemetry data
├── history.py           # Records the history of drift and correction events
├── orbit_simulation.py  # GUI frame for the 3D orbit visualization
└── README.md            # This file

🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.
Prerequisites

    Python 3.7 or newer

Installation

    Clone the repository:

    git clone [https://github.com/your-username/cubesat-mission-control.git](https://github.com/your-username/cubesat-mission-control.git)
    cd cubesat-mission-control

    Create and activate a virtual environment (recommended):

        Windows:

        python -m venv venv
        .\venv\Scripts\activate

        macOS / Linux:

        python3 -m venv venv
        source venv/bin/activate

    Install the required libraries:
    Create a requirements.txt file with the following content:

    customtkinter
    matplotlib
    numpy
    Pillow

    Then, run the following command to install them:

    pip install -r requirements.txt

Usage

To run the application, execute the main.py script from the root directory:

python main.py

You can use any username and password on the login screen (e.g., admin/admin).
⚙️ Configuration

The config.py file allows you to easily modify key parameters without changing the core application logic. You can adjust:

    Simulation Speed: SIMULATION_TICK_RATE_HZ

    PID Controller Gains: PID_GAINS = {'Kp': ..., 'Ki': ..., 'Kd': ...}

    Course Tolerance: ON_COURSE_THRESHOLD

    GUI Theme and Colors: APP_THEME_MODE, APP_COLOR_THEME, etc.

🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

    Fork the Project

    Create your Feature Branch (git checkout -b feature/AmazingFeature)

    Commit your Changes (git commit -m 'Add some AmazingFeature')

    Push to the Branch (git push origin feature/AmazingFeature)

    Open a Pull Request

📄 License

This project is distributed under the MIT License. See the LICENSE file for more information.

