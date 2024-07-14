import tkinter as tk
import json
import os
import re
import sys
import tempfile
import signal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Define the configuration classes based on JSON structure
class FontConfig:
    def __init__(self, name, size):
        self.name = name
        self.size = size

class WindowConfig:
    def __init__(self, width, height, x, y, font):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.font = FontConfig(**font)

class MatchConfig:
    def __init__(self, regex, bgcolor, fgcolor):
        self.regex = re.compile(regex)
        self.bgcolor = bgcolor
        self.fgcolor = fgcolor

class Config:
    def __init__(self, window, matches):
        self.window = WindowConfig(**window)
        self.matches = [MatchConfig(**match) for match in matches]

# Function to read the configuration file
def read_config(filepath):
    with open(filepath, 'r') as file:
        data = json.load(file)
        return Config(**data)

# Function to check if the state file exists 
def check_and_create_state_file(filepath):
    default_content = "NO FILE FOUND"
    if not os.path.exists(filepath):
        with open(filepath, 'w') as file:
            file.write(default_content)

# Function to read the state file
def read_state_file(filepath):
    with open(filepath, 'r') as file:
        return file.read().strip()

# Main application class
class AlwaysOnTopApp:
    def __init__(self, root, config, statefilepath):
        self.root = root
        self.config = config
        self.statefilepath = statefilepath

        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        if config.window.x < 0:
            x_position = screen_width + config.window.x - config.window.width
        else:
            x_position = config.window.x
        
        if config.window.y < 0:
            y_position = screen_height + config.window.y - config.window.height
        else:
            y_position = config.window.y

        self.root.geometry(f"{config.window.width}x{config.window.height}+{x_position}+{y_position}")

        # Create a frame to contain the content and the close button
        frame = tk.Frame(root)
        frame.pack(expand=True, fill=tk.BOTH)

        # Add a label to display the text
        self.label = tk.Label(frame, font=(config.window.font.name, config.window.font.size))
        self.label.pack(expand=True, fill=tk.BOTH)

        # Add a close button
        self.root.bind("<Escape>", self.on_escape)
        self.update_content()

        # Set up file monitoring
        event_handler = StateFileEventHandler(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, os.path.dirname(self.statefilepath), recursive=False)
        self.observer.start()

        # Handle Ctrl+C and Ctrl+Z if possible
        signal.signal(signal.SIGINT, self.signal_handler)
        if hasattr(signal, 'SIGTSTP'):
            signal.signal(signal.SIGTSTP, self.signal_handler)

    def update_content(self):
        try:
            state = read_state_file(self.statefilepath)
            matched = False
            for match in self.config.matches:
                if match.regex.search(state):
                    self.label.config(text=state, fg=match.fgcolor, bg=match.bgcolor)
                    matched = True
                    break
            if not matched:
                # Default colors if no match found
                self.label.config(text=state, fg="#FFFFFF", bg="#000000")
        except Exception as e:
            print(f"Error reading state file: {e}")

    def on_escape(self, event=None):
        self.on_close()

    def signal_handler(self, signum, frame):
        self.on_close()

    def on_close(self):
        self.observer.stop()
        self.observer.join()
        self.root.quit()
        self.root.destroy()
        sys.exit(0)

class StateFileEventHandler(FileSystemEventHandler):
    def __init__(self, app):
        self.app = app

    def on_modified(self, event):
        if event.src_path == self.app.statefilepath:
            self.app.update_content()

if __name__ == "__main__":
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Config file path
    config_filepath = os.path.join(script_dir, "statuswindow.config.json")

    # Read the configuration
    config = read_config(config_filepath)

    # Get the state file path from arguments or use default
    statefilepath = sys.argv[1] if len(sys.argv) > 1 else os.path.join(tempfile.gettempdir(), "state.txt")
    print("Using path '"+statefilepath+"'")
    
    # Check and create the state file if it does not exist
    check_and_create_state_file(statefilepath)

    # Initialize Tkinter root
    root = tk.Tk()
    app = AlwaysOnTopApp(root, config, statefilepath)
    root.mainloop()
