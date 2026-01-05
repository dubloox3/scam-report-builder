"""
Configuration Manager for Scam Report Builder
Handles saving/loading application settings.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
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
                    return config
            except Exception as e:
                print(f"Error loading config: {e}")
        
        # Default configuration
        return {
            "last_report_number": 0,
            "numbering_format": "{number}",
            "output_directory": "",
            "report_folder": ""
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
    
    def get_next_report_number(self) -> tuple[int, str]:
        """Get next report number and format"""
        return self.config.get("last_report_number", 0) + 1, self.config.get("numbering_format", "{number}")
    
    def update_report_number(self, number: int, format_str: str):
        """Update report number in config"""
        self.config["last_report_number"] = number
        self.config["numbering_format"] = format_str
        self.save_config()
    
    def get_output_directory(self) -> Path:
        """
        Get output directory for reports.
        If not set, prompts user to choose or creates default 'Reports' folder.
        """
        output_dir = self.config.get("output_directory", "")
        
        # If directory is already configured and exists, use it
        if output_dir and Path(output_dir).exists():
            return Path(output_dir)
        
        # Prompt user to choose folder
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        response = messagebox.askyesno(
            "Reports Folder",
            "No reports folder configured.\n\n"
            "Would you like to choose a folder for saving reports?\n\n"
            "Click 'No' to create a 'Reports' folder in the script directory."
        )
        
        if response:  # User clicked Yes - choose folder
            chosen_dir = filedialog.askdirectory(
                title="Select Reports Folder",
                initialdir=Path.cwd()
            )
            
            if chosen_dir:
                output_dir = chosen_dir
            else:
                # User cancelled, create default folder
                output_dir = Path.cwd() / "Reports"
                output_dir.mkdir(exist_ok=True)
                messagebox.showinfo(
                    "Reports Folder Created",
                    f"Created default 'Reports' folder at:\n{output_dir}"
                )
        else:  # User clicked No - create default folder
            output_dir = Path.cwd() / "Reports"
            output_dir.mkdir(exist_ok=True)
            messagebox.showinfo(
                "Reports Folder Created",
                f"Created default 'Reports' folder at:\n{output_dir}"
            )
        
        # Save the chosen directory to config
        self.config["output_directory"] = str(output_dir)
        self.save_config()
        
        return Path(output_dir)
    
    def update_output_directory(self, new_directory: str):
        """Update output directory in config"""
        self.config["output_directory"] = new_directory
        self.save_config()
    
    def reset_output_directory(self):
        """Reset output directory (e.g., for testing or user wants to change)"""
        self.config["output_directory"] = ""
        self.save_config()
    
    def get_report_folder(self) -> str:
        """Returns saved report folder path from config, or empty string if not set"""
        return self.config.get("report_folder", "")
    
    def set_report_folder(self, folder_path: str):
        """Saves report folder path to config"""
        self.config["report_folder"] = folder_path
        self.save_config()