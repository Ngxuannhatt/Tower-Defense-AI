import os
import sys
import tkinter as tk

# Ensure the package directories are in the Python search path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from map_manager import MapManager
from pathfinder import Pathfinder
from gui import TowerDefenseGUI

def main():
    """
    Main application entry point.
    Initializes the core modules and runs the desktop simulation window.
    """
    # 1. Initialize MapManager with a 20x20 grid
    map_manager = MapManager(width=20, height=20)
    
    # 2. Initialize Pathfinder coordinator
    pathfinder = Pathfinder(map_manager)
    
    # 3. Setup Tkinter root window
    root = tk.Tk()
    
    # 4. Instantiate the GUI dashboard
    gui_app = TowerDefenseGUI(root, map_manager, pathfinder)
    
    # 5. Start main loop
    root.mainloop()

if __name__ == "__main__":
    main()
