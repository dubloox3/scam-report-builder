"""
Configuration Manager for Scam Report Builder
Handles saving/loading application settings.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from tkinter import filedialog, messagebox
import tkinter as tk


class ConfigManager:
    """Manages application configuration"""
    
    CONFIG_FILE = "scam_report_config.json"
    
    def __init__(self):
        """Initialize the ConfigManager with loaded configuration"""
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        config_path = Path(self.CONFIG_FILE)
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    # Ensure all required fields exist
                    if "output_directory" not in config:
                        config["output_directory"] = ""
                    if "last_report_number" not in config:
                        config["last_report_number"] = 0
                    if "numbering_format" not in config:
                        config["numbering_format"] = "{number}"
                    if "report_folder" not in config:
                        config["report_folder"] = ""
                    if "last_used_folder" not in config:
                        config["last_used_folder"] = ""
                    return config
            except Exception as e:
                print(f"Error loading config: {e}")
        
        # Default configuration
        return {
            "last_report_number": 0,
            "numbering_format": "{number}",
            "output_directory": "",
            "report_folder": "",
            "last_used_folder": ""
        }
    
    def save_config(self, config: Optional[Dict[str, Any]] = None):
        """Save configuration to file"""
        try:
            # If config parameter is provided, update self.config
            if config is not None:
                self.config = config
            
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    # ===== FOLDER PERSISTENCE METHODS =====
    
    def get_last_used_folder(self) -> str:
        """Get the last used report folder path from config"""
        return self.config.get("last_used_folder", "")
    
    def set_last_used_folder(self, folder_path: str):
        """Set and save the last used report folder path to config"""
        # Convert to string and normalize path
        folder_str = str(folder_path).strip()
        if folder_str:
            # Store the absolute path for consistency
            folder_path_obj = Path(folder_str)
            if folder_path_obj.exists():
                folder_str = str(folder_path_obj.resolve())
        
        self.config["last_used_folder"] = folder_str
        self.save_config()
    
    # Alias for backward compatibility
    def save_last_used_folder(self, folder_path: str):
        """Alias for set_last_used_folder() for clearer naming"""
        self.set_last_used_folder(folder_path)
    
    def get_output_directory(self) -> Path:
        """
        Get output directory for reports.
        If not set, prompts user to choose or creates default 'Reports' folder.
        Returns the chosen directory path.
        """
        # First check if we have a saved last_used_folder that exists
        last_used_folder = self.get_last_used_folder()
        if last_used_folder and Path(last_used_folder).exists():
            return Path(last_used_folder)
        
        # Fall back to output_directory for backward compatibility
        output_dir = self.config.get("output_directory", "")
        if output_dir and Path(output_dir).exists():
            # Update last_used_folder for consistency
            self.set_last_used_folder(output_dir)
            return Path(output_dir)
        
        # If no valid saved folder, prompt user
        return self.prompt_for_folder()
    
    def prompt_for_folder(self) -> Path:
        """
        Prompt user to choose a folder for reports.
        Saves the selection to config for future use.
        """
        # Get the last used folder or current directory as starting point
        initial_dir = self.get_last_used_folder()
        if not initial_dir or not Path(initial_dir).exists():
            initial_dir = Path.cwd()
        
        # Prompt user to choose folder
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        response = messagebox.askyesno(
            "Reports Folder",
            "Select folder for saving reports:\n\n"
            "• Click 'Yes' to choose a custom folder\n"
            "• Click 'No' to use the default 'Reports' folder"
        )
        
        if response:  # User clicked Yes - choose custom folder
            chosen_dir = filedialog.askdirectory(
                title="Select Reports Folder",
                initialdir=str(initial_dir)
            )
            
            if chosen_dir:
                output_dir = chosen_dir
                messagebox.showinfo(
                    "Folder Selected",
                    f"Reports will be saved to:\n{output_dir}"
                )
            else:
                # User cancelled, create default folder
                output_dir = Path.cwd() / "Reports"
                output_dir.mkdir(exist_ok=True)
                messagebox.showinfo(
                    "Reports Folder Created",
                    f"Created default 'Reports' folder at:\n{output_dir}"
                )
        else:  # User clicked No - create/use default folder
            output_dir = Path.cwd() / "Reports"
            output_dir.mkdir(exist_ok=True)
            messagebox.showinfo(
                "Reports Folder",
                f"Using default 'Reports' folder at:\n{output_dir}"
            )
        
        # Save the chosen directory to config for future use
        self.set_last_used_folder(str(output_dir))
        
        return Path(output_dir)
    
    def ensure_report_folder_exists(self, folder_path: Optional[str] = None) -> Path:
        """
        Ensure the report folder exists.
        If folder_path is provided, use it; otherwise use saved folder.
        Creates folder if it doesn't exist.
        """
        if folder_path:
            target_folder = Path(folder_path)
        else:
            target_folder = self.get_output_directory()
        
        # Create folder if it doesn't exist
        target_folder.mkdir(parents=True, exist_ok=True)
        
        # Update config if this is a new folder
        current_folder = self.get_last_used_folder()
        if str(target_folder) != current_folder:
            self.set_last_used_folder(str(target_folder))
        
        return target_folder
    
    # ===== INTEGRATION WITH MAIN_WINDOW.PY =====
    
    def get_initial_folder_for_dialog(self) -> str:
        """
        Get the initial folder path for file dialogs in main_window.py.
        Returns the last used folder if it exists, otherwise current directory.
        """
        last_folder = self.get_last_used_folder()
        if last_folder and Path(last_folder).exists():
            return last_folder
        return str(Path.cwd())
    
    def update_folder_from_dialog(self, selected_folder: str):
        """
        Call this after a file dialog in main_window.py returns a folder.
        Updates the last used folder in config.
        """
        if selected_folder:  # Only update if user actually selected something
            self.set_last_used_folder(selected_folder)
    
    # ===== REST OF THE METHODS =====
    
    def get_next_report_number(self) -> tuple[int, str]:
        """Get next report number and format"""
        return self.config.get("last_report_number", 0) + 1, self.config.get("numbering_format", "{number}")
    
    def update_report_number(self, number: int, format_str: str):
        """Update report number in config"""
        self.config["last_report_number"] = number
        self.config["numbering_format"] = format_str
        self.save_config()
    
    def update_output_directory(self, new_directory: str):
        """Update output directory in config (for backward compatibility)"""
        self.config["output_directory"] = new_directory
        self.save_config()
    
    def reset_output_directory(self):
        """Reset output directory (e.g., for testing or user wants to change)"""
        self.config["output_directory"] = ""
        self.config["last_used_folder"] = ""
        self.save_config()
    
    def get_report_folder(self) -> str:
        """Returns saved report folder path from config, or empty string if not set"""
        # Prefer last_used_folder, fall back to report_folder for backward compatibility
        last_used = self.get_last_used_folder()
        if last_used:
            return last_used
        return self.config.get("report_folder", "")
    
    def set_report_folder(self, folder_path: str):
        """Saves report folder path to config"""
        self.config["report_folder"] = folder_path
        self.set_last_used_folder(folder_path)  # Also update last_used_folder
        self.save_config()
    
    def generate_report_filename(self, report_number: int, first_name: str, middle_name: str, last_name: str, 
                                file_extension: str = "odt") -> str:
        """Generate a report filename in the new format"""
        # ... (existing implementation) ...
    
    def generate_report_filename_from_full_name(self, report_number: int, full_name: str, 
                                               file_extension: str = "odt") -> str:
        """Generate a report filename from a single full name string"""
        # ... (existing implementation) ...
    
    def generate_report_filename_legacy(self, report_number: int, first_name: str, middle_name: str, last_name: str,
                                       file_extension: str = "odt") -> str:
        """Legacy filename format for backward compatibility"""
        # ... (existing implementation) ...