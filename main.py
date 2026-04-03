import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from downloader_engine import DownloaderEngine

# Global appearance settings
ctk.set_appearance_mode("System")  # Follow system light/dark mode
ctk.set_default_color_theme("blue")

class MediaDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Media Downloader")
        self.geometry("600x400")
        self.resizable(False, False)
        
        # Set default download path to user's 'Downloads' folder
        self.download_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        
        self.setup_ui()
        
        # Initialize the downloading backend
        self.engine = DownloaderEngine(
            progress_callback=self.update_progress,
            completion_callback=self.on_download_complete,
            error_callback=self.on_download_error
        )
        
    def setup_ui(self):
        # App Title
        self.title_label = ctk.CTkLabel(self, text="Media Downloader", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=(20, 10))
        
        # URL Input Area
        self.url_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.url_frame.pack(fill="x", padx=40, pady=10)
        
        self.url_label = ctk.CTkLabel(self.url_frame, text="URL:")
        self.url_label.pack(side="left", padx=(0, 10))
        
        self.url_entry = ctk.CTkEntry(self.url_frame, placeholder_text="Paste YouTube, Vimeo, etc. link here...", width=400)
        self.url_entry.pack(side="left", fill="x", expand=True)

        # Format Selection Area
        self.format_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.format_frame.pack(fill="x", padx=40, pady=10)
        
        self.format_label = ctk.CTkLabel(self.format_frame, text="Format:")
        self.format_label.pack(side="left", padx=(0, 10))
        
        self.format_var = tk.StringVar(value="Video")
        
        def on_type_change():
            if self.format_var.get() == "Video":
                self.ext_menu.configure(values=["Best (Auto)", "mp4", "webm", "mkv"])
                self.ext_var.set("Best (Auto)")
            else:
                self.ext_menu.configure(values=["Best (Auto)", "mp3", "m4a", "wav", "flac"])
                self.ext_var.set("Best (Auto)")

        self.radio_video = ctk.CTkRadioButton(self.format_frame, text="Video", variable=self.format_var, value="Video", command=on_type_change)
        self.radio_video.pack(side="left", padx=10)
        
        self.radio_audio = ctk.CTkRadioButton(self.format_frame, text="Audio Only", variable=self.format_var, value="Audio", command=on_type_change)
        self.radio_audio.pack(side="left", padx=10)

        self.ext_label = ctk.CTkLabel(self.format_frame, text="File Type:")
        self.ext_label.pack(side="left", padx=(20, 10))
        
        self.ext_var = tk.StringVar(value="Best (Auto)")
        self.ext_menu = ctk.CTkOptionMenu(self.format_frame, variable=self.ext_var, values=["Best (Auto)", "mp4", "webm", "mkv"], width=100)
        self.ext_menu.pack(side="left")

        # Save Location Area
        self.path_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.path_frame.pack(fill="x", padx=40, pady=10)
        
        self.path_label = ctk.CTkLabel(self.path_frame, text="Save To:")
        self.path_label.pack(side="left", padx=(0, 10))
        
        self.path_display = ctk.CTkEntry(self.path_frame, width=300, state="disabled")
        self.path_display.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.update_path_display()
        
        self.browse_btn = ctk.CTkButton(self.path_frame, text="Browse", width=80, command=self.browse_folder)
        self.browse_btn.pack(side="left")
        
        # Spacer
        ctk.CTkFrame(self, fg_color="transparent", height=20).pack()

        # Progress Bar and Status
        self.progress_bar = ctk.CTkProgressBar(self, width=520)
        self.progress_bar.pack(pady=(10, 5))
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(self, text="Ready", text_color="gray")
        self.status_label.pack()

        # Action Button
        self.download_btn = ctk.CTkButton(self, text="DOWNLOAD", height=40, font=ctk.CTkFont(size=16, weight="bold"), command=self.start_download)
        self.download_btn.pack(pady=20)

    def update_path_display(self):
        """Updates the read-only entry box to show the save path."""
        self.path_display.configure(state="normal")
        self.path_display.delete(0, 'end')
        self.path_display.insert(0, self.download_path)
        self.path_display.configure(state="disabled")

    def browse_folder(self):
        """Opens a folder picker dialog."""
        folder = filedialog.askdirectory(initialdir=self.download_path)
        if folder:
            self.download_path = folder
            self.update_path_display()

    def start_download(self):
        """Triggered when the DOWNLOAD button is clicked."""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Input Error", "Please enter a valid URL.")
            return
            
        # Update UI to reflect downloading state
        self.download_btn.configure(state="disabled", text="Downloading...")
        self.progress_bar.set(0)
        self.status_label.configure(text="Initializing download...")
        
        fmt = self.format_var.get()
        ext = self.ext_var.get()
        self.engine.download_in_thread(url, fmt, ext, self.download_path)

    def update_progress(self, percent):
        """Callback to update progress smoothly."""
        val = percent / 100.0
        # Use .after() to safely update the GUI from the background thread
        self.after(0, self._set_progress, val, percent)
        
    def _set_progress(self, val, percent):
        self.progress_bar.set(val)
        self.status_label.configure(text=f"Downloading... {percent:.1f}%")

    def on_download_complete(self):
        """Callback for successful download."""
        self.after(0, self._download_finished)

    def _download_finished(self):
        self.progress_bar.set(1.0)
        self.status_label.configure(text="Download Complete!")
        messagebox.showinfo("Success", "Download finished successfully!")
        self.download_btn.configure(state="normal", text="DOWNLOAD")
        self.url_entry.delete(0, 'end')

    def on_download_error(self, error_msg):
        """Callback for errors."""
        self.after(0, self._show_error, error_msg)
        
    def _show_error(self, error_msg):
        self.status_label.configure(text="Error occurred.")
        messagebox.showerror("Download Error", f"An error occurred:\n\n{error_msg}")
        self.download_btn.configure(state="normal", text="DOWNLOAD")
        self.progress_bar.set(0)

if __name__ == "__main__":
    app = MediaDownloaderApp()
    app.mainloop()
