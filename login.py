# login.py

import customtkinter as ctk
from tkinter import messagebox
from PIL import Image

class LoginPage(ctk.CTk):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.title("CubeSat Login")
        self.geometry("1000x600")

        # Load and store the original image
        try:
            self.original_bg_image = Image.open(r"C:\Users\KZE\Desktop\New folder (4)\assets\login.png")
        except FileNotFoundError:
            self.original_bg_image = None
            print("Warning: login.png not found. Using a fallback background.")
            self.configure(fg_color="#1a1a1a")

        # Create a label for the background and place it
        self.bg_label = ctk.CTkLabel(self, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Bind the resize event to the _resize_image method
        self.bind("<Configure>", self._resize_image)

        # --- Login Frame and Widgets ---
        login_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#1a1a1a")
        login_frame.place(relx=0.2, rely=0.5, anchor=ctk.CENTER)
        
        label = ctk.CTkLabel(login_frame, text="SatNav.", font=ctk.CTkFont(size=30, weight="bold"))
        label.grid(row=0, column=0, padx=30, pady=(40, 10))

        subtitle = ctk.CTkLabel(login_frame, text="A Simple CubeSat Simulation", font=ctk.CTkFont(size=18))
        subtitle.grid(row=1, column=0, padx=30, pady=(0, 20))

        self.username_entry = ctk.CTkEntry(login_frame, placeholder_text="User ID", width=200, height=40)
        self.username_entry.grid(row=2, column=0, padx=30, pady=10)

        self.password_entry = ctk.CTkEntry(login_frame, placeholder_text="Password", show="*", width=200, height=40)
        self.password_entry.grid(row=3, column=0, padx=30, pady=10)

        login_button = ctk.CTkButton(login_frame, text="Login", command=self.attempt_login, width=200, height=40)
        login_button.grid(row=4, column=0, padx=30, pady=20)

    def _resize_image(self, event):
        """Resizes the background image to fit the new window size."""
        # Check if the image was loaded successfully
        if self.original_bg_image is None:
            return

        # Get the new window size from the event object
        new_width = event.width
        new_height = event.height
        
        # --- Resizing logic (same as before, but with dynamic dimensions) ---
        img_width, img_height = self.original_bg_image.size
        aspect_ratio_window = new_width / new_height
        aspect_ratio_img = img_width / img_height

        if aspect_ratio_img > aspect_ratio_window:
            # Image is wider, scale by height
            resize_height = new_height
            resize_width = int(resize_height * aspect_ratio_img)
        else:
            # Image is taller, scale by width
            resize_width = new_width
            resize_height = int(resize_width / aspect_ratio_img)

        # Resize the original image using a high-quality filter
        bg_image_resized = self.original_bg_image.resize((resize_width, resize_height), Image.LANCZOS)
        
        # Create a new CTkImage object with the resized image
        bg_image = ctk.CTkImage(light_image=bg_image_resized, size=(new_width, new_height))
        
        # Update the label with the new image
        self.bg_label.configure(image=bg_image)
        # Keep a reference to the image to prevent it from being garbage-collected
        self.bg_label.image = bg_image

    def attempt_login(self):
        if self.username_entry.get() == "admin" and self.password_entry.get() == "root":
            self.destroy()
            self.on_login_success()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")