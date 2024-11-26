import whisper
from pydub import AudioSegment
import json
from datetime import datetime
import ssl
import urllib.request
import os
import threading

from processor import AudioSplitter
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class AudioProcessorGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Audio Processor")
        self.window.geometry("800x600")
        
        # Initialize variables
        self.input_path = tk.StringVar()
        self.output_dir = tk.StringVar(value="split_segments")
        self.model_size = tk.StringVar(value="base")
        self.processing = False
        self.json_path = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Model selection
        model_frame = ttk.LabelFrame(main_frame, text="Model Settings", padding=10)
        model_frame.pack(fill="x", pady=5)
        
        ttk.Label(model_frame, text="Model Size:").pack(side="left", padx=5)
        model_choices = ["tiny", "base", "small", "medium", "large"]
        model_dropdown = ttk.Combobox(model_frame, textvariable=self.model_size, values=model_choices, state="readonly")
        model_dropdown.pack(side="left", padx=5)
        
        # Input file section
        input_frame = ttk.LabelFrame(main_frame, text="Input Audio File", padding=10)
        input_frame.pack(fill="x", pady=5)
        
        ttk.Entry(input_frame, textvariable=self.input_path, width=70).pack(side="left", padx=5)
        ttk.Button(input_frame, text="Browse", command=self.browse_input).pack(side="left")
        
        # Output directory section
        output_frame = ttk.LabelFrame(main_frame, text="Output Settings", padding=10)
        output_frame.pack(fill="x", pady=5)
        
        ttk.Label(output_frame, text="Output Directory:").pack(anchor="w")
        output_entry = ttk.Entry(output_frame, textvariable=self.output_dir, width=70)
        output_entry.pack(side="left", padx=5)
        ttk.Button(output_frame, text="Browse", command=self.browse_output).pack(side="left")
        
        # Status section
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding=10)
        status_frame.pack(fill="x", pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.pack(fill="x")
        
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(status_frame, variable=self.progress_var, maximum=100)
        self.progress.pack(fill="x", pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=10)
        
        self.process_btn = ttk.Button(button_frame, text="Process Audio", command=self.process_audio)
        self.process_btn.pack(side="left", padx=5)
        
        self.cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.cancel_processing, state="disabled")
        self.cancel_btn.pack(side="left", padx=5)
        
    def browse_input(self):
        filename = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[
                ("Audio Files", "*.mp3 *.wav *.m4a *.ogg"),
                ("All Files", "*.*")
            ]
        )
        if filename:
            self.input_path.set(filename)
            # Auto-set output directory based on input file
            default_output = os.path.join(os.path.dirname(filename), "split_segments")
            self.output_dir.set(default_output)
    
    def browse_output(self):
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir.set(directory)
    
    def update_progress(self, phase, progress=None, message=None):
        if message:
            self.status_label.config(text=message)
        if progress is not None:
            self.progress_var.set(progress)
        self.window.update_idletasks()
    
    def process_audio(self):
        if not self.input_path.get():
            messagebox.showerror("Error", "Please select an input audio file")
            return
            
        if not os.path.exists(self.input_path.get()):
            messagebox.showerror("Error", "Input file does not exist")
            return
        
        self.processing = True
        self.process_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        
        # Create and start processing thread
        self.process_thread = threading.Thread(target=self.process_audio_thread)
        self.process_thread.start()
        
        # Start monitoring the thread
        self.window.after(100, self.check_process_thread)
    
    def process_audio_thread(self):
        try:
            # Initialize splitter with selected model
            self.update_progress(phase="init", progress=0, message="Loading model...")
            splitter = AudioSplitter(model_size=self.model_size.get())
            
            # Process audio
            self.update_progress(phase="transcribe", progress=20, message="Transcribing audio...")
            sentences = splitter.process_audio(self.input_path.get())
            
            if not self.processing:  # Check if cancelled
                return
                
            # Save JSON
            self.update_progress(phase="json", progress=60, message="Saving transcription...")
            self.json_path = os.path.join(self.output_dir.get(), "output.json")
            os.makedirs(self.output_dir.get(), exist_ok=True)
            splitter.save_to_json(sentences, self.json_path)
            
            # Export JSON to user-selected location
            self.window.after(0, self.export_json)
            
            if not self.processing:  # Check if cancelled
                return
                
            # Split audio
            self.update_progress(phase="split", progress=80, message="Splitting audio segments...")
            splitter.split_audio_by_sentences(
                self.input_path.get(),
                sentences,
                self.output_dir.get()
            )
            
            self.update_progress(phase="complete", progress=100, message="Processing complete!")
            
        except Exception as e:
            self.window.after(0, lambda: self.show_error(str(e)))
    
    def export_json(self):
        if not self.json_path or not os.path.exists(self.json_path):
            messagebox.showerror("Error", "JSON file not found!")
            return
            
        # Open file dialog to choose where to save the JSON
        save_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialfile="output.json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save JSON File As"
        )
        
        if save_path:
            try:
                if save_path != self.json_path:  # Only copy if saving to a different location
                    import shutil
                    shutil.copy2(self.json_path, save_path)
                
                # Cross-platform way to open the containing folder
                folder_path = os.path.dirname(save_path)
                try:
                    if os.name == 'nt':  # Windows
                        os.startfile(folder_path)
                    elif os.name == 'posix':  # macOS and Linux
                        import subprocess
                        if sys.platform == 'darwin':  # macOS
                            subprocess.run(['open', folder_path])
                        else:  # Linux
                            subprocess.run(['xdg-open', folder_path])
                except Exception:
                    # If opening folder fails, just continue
                    pass
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export JSON: {str(e)}")
    
    def check_process_thread(self):
        if self.process_thread.is_alive():
            self.window.after(100, self.check_process_thread)
        else:
            self.process_complete()
    
    def cancel_processing(self):
        self.processing = False
        self.status_label.config(text="Cancelling...")
        self.cancel_btn.config(state="disabled")
    
    def process_complete(self):
        self.process_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")
        self.processing = False
        
        json_path = os.path.join(self.output_dir.get(), "output.json")
        message = f"Audio processing completed successfully!\nOutput saved to: {self.output_dir.get()}\nJSON file: {json_path}"
        messagebox.showinfo("Success", message)
    
    def show_error(self, error_message):
        self.status_label.config(text="Error occurred!")
        self.process_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")
        self.processing = False
        messagebox.showerror("Error", f"An error occurred: {error_message}")
    
    def run(self):
        self.window.mainloop()

def main():
    app = AudioProcessorGUI()
    app.run()

if __name__ == "__main__":
    main()