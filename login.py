import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import sys

class LoginPage(ctk.CTk):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.title("CubeSat Login")
        self.geometry("1000x600")

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Load the background image
        self.bg_image_path = "C:\\Users\\KZE\\Desktop\\final\\assets\\login.png"
        try:
            self.bg_image_pil = Image.open(self.bg_image_path)
            self.bg_image = ImageTk.PhotoImage(self.bg_image_pil)
        except FileNotFoundError:
            print(f"Error: Background image not found at {self.bg_image_path}")
            sys.exit()

        # Create a CTkLabel to display the background image
        self.bg_label = ctk.CTkLabel(self, text="", image=self.bg_image)
        # Fix: Use place() to fill the window completely without padding
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Create a frame for the login widgets
        self.login_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#1a1a1a")
        
        # Place the login frame on the window
        self.login_frame.place(relx=0.2, rely=0.5, anchor=ctk.CENTER)
        
        # Add widgets to the login frame using grid()
        self.login_frame.grid_columnconfigure(0, weight=1)
        
        self.label = ctk.CTkLabel(self.login_frame, text="SatNav.", font=ctk.CTkFont(size=30, weight="bold"))
        self.label.grid(row=0, column=0, padx=30, pady=(40, 10))

        self.subtitle_label = ctk.CTkLabel(self.login_frame, text="A Simple CubeSat Simulation", font=ctk.CTkFont(size=18))
        self.subtitle_label.grid(row=1, column=0, padx=30, pady=(0, 20))

        self.username_entry = ctk.CTkEntry(self.login_frame, placeholder_text="User ID", width=200, height=40, corner_radius=10)
        self.username_entry.grid(row=2, column=0, padx=30, pady=10)

        self.password_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Password", show="*", width=200, height=40, corner_radius=10)
        self.password_entry.grid(row=3, column=0, padx=30, pady=10)

        self.login_button = ctk.CTkButton(self.login_frame, text="Login", command=self.attempt_login, width=200, height=40, corner_radius=10, fg_color="#1F6AA5")
        self.login_button.grid(row=4, column=0, padx=30, pady=20)

        # Bind the configure event to handle window resizing
        self.bind("<Configure>", self.on_resize)
    
    def on_resize(self, event):
        # Resize the background image
        if self.bg_image_pil:
            new_width = self.winfo_width()
            new_height = self.winfo_height()
            resized_image = self.bg_image_pil.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(resized_image)
            self.bg_label.configure(image=self.bg_image)

    def attempt_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username == "admin" and password == "root":
            self.on_login_success()
            self.destroy()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

if __name__ == "__main__":
    from main import SatelliteGUI

    def launch_main_app():
        target_location = (1000, 500, 200)
        app = SatelliteGUI(target_location=target_location)
        app.mainloop()

    login_app = LoginPage(launch_main_app)
    login_app.mainloop()