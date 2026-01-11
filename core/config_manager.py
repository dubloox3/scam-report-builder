"""
Configuration Manager for Scam Report Builder
Handles saving/loading application settings.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, Any, Optional
from PySide6.QtWidgets import QFileDialog, QMessageBox


class ConfigManager:
    """Manages application configuration"""
    
    CONFIG_FILE = "scam_report_config.json"
    JSON_DATA_FOLDER = ".report_data"  # Folder name for JSON data files
    
    def __init__(self):
        """Initialize the ConfigManager with loaded configuration"""
        self.config = self.load_config()
    
    def _get_app_root(self) -> Path:
        """Get application root directory (works for both script and EXE)"""
        import sys
        if getattr(sys, 'frozen', False):
            # Running as EXE - use executable's directory
            return Path(sys.executable).parent
        else:
            # Running as script - use script directory
            return Path(__file__).parent.parent
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file - loads immediately from disk"""
        app_root = self._get_app_root()
        config_path = app_root / self.CONFIG_FILE
        
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
                    if "last_template_key" not in config:
                        config["last_template_key"] = ""
                    return config
            except Exception:
                pass  # Return default config on error
        
        # Default configuration
        return {
            "last_report_number": 0,
            "numbering_format": "{number}",
            "output_directory": "",
            "report_folder": "",
            "last_used_folder": "",
            "last_template_key": ""
        }
    
    def save_config(self, config: Optional[Dict[str, Any]] = None):
        """Save configuration to file - saves immediately to disk"""
        try:
            # If config parameter is provided, update self.config
            if config is not None:
                self.config = config
            
            # Write to disk immediately
            app_root = self._get_app_root()
            config_path = app_root / self.CONFIG_FILE
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            # Force flush to ensure data is written
            f.flush()
            os.fsync(f.fileno())
            
        except Exception:
            pass  # Silent failure - config save errors are non-critical
    
    def reload_config(self):
        """Force reload config from disk"""
        # Reload using the same path logic
        app_root = self._get_app_root()
        config_path = app_root / self.CONFIG_FILE
        
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
                    if "last_template_key" not in config:
                        config["last_template_key"] = ""
                    self.config = config
            except Exception:
                pass  # Keep existing config on reload error
    
    # ===== REPORT FOLDER METHODS (IMMEDIATE SYNC) =====
    
    def get_report_folder(self) -> str:
        """
        Returns the explicitly set report folder path from config.
        This returns the 'report_folder' config value.
        For immediate sync verification after set_report_folder().
        """
        # Return the report_folder value directly
        return self.config.get("report_folder", "")
    
    def set_report_folder(self, folder_path: str) -> bool:
        """
        Saves report folder path to config IMMEDIATELY.
        Also updates last_used_folder for pre-selection.
        Returns True if successful, False otherwise.
        """
        try:
            # Convert to string and normalize
            folder_str = str(folder_path).strip()
            if not folder_str:
                return False
            
            # Store the absolute path for consistency
            folder_path_obj = Path(folder_str)
            folder_str = str(folder_path_obj.resolve())
            
            # Update BOTH config values for different purposes:
            # - report_folder: The explicitly set folder (what get_report_folder() returns)
            # - last_used_folder: For file dialog pre-selection
            self.config["report_folder"] = folder_str
            self.config["last_used_folder"] = folder_str
            
            # Save to disk immediately
            self.save_config()
            
            # Verify it was saved by reloading
            self.reload_config()
            
            # Verify the value matches
            saved_value = self.config.get("report_folder", "")
            if saved_value == folder_str:
                return True
            else:
                return False
                
        except Exception as e:
            return False
    
    def get_last_used_folder(self) -> str:
        """
        Get the last used report folder path from config.
        Used for file dialog pre-selection.
        """
        return self.config.get("last_used_folder", "")
    
    def set_last_used_folder(self, folder_path: str) -> bool:
        """
        Set and save the last used report folder path to config IMMEDIATELY.
        This updates where file dialogs will open.
        """
        try:
            # Convert to string and normalize path
            folder_str = str(folder_path).strip()
            if folder_str:
                # Store the absolute path for consistency
                folder_path_obj = Path(folder_str)
                folder_str = str(folder_path_obj.resolve())
            
            self.config["last_used_folder"] = folder_str
            self.save_config()
            return True
        except Exception:
            return False
    
    def save_last_used_folder(self, folder_path: str) -> bool:
        """Alias for set_last_used_folder() for clearer naming"""
        return self.set_last_used_folder(folder_path)
    
    # ===== FOLDER PRE-SELECTION AND MANAGEMENT =====
    
    def get_output_directory(self) -> Path:
        """
        Get output directory for reports.
        If not set, prompts user to choose or creates default 'Reports' folder.
        Returns the chosen directory path.
        """
        # First check report_folder (explicitly set folder)
        report_folder = self.get_report_folder()
        if report_folder and Path(report_folder).exists():
            return Path(report_folder)
        
        # Then check last_used_folder (for pre-selection)
        last_used_folder = self.get_last_used_folder()
        if last_used_folder and Path(last_used_folder).exists():
            # Also update report_folder for consistency
            self.config["report_folder"] = last_used_folder
            return Path(last_used_folder)
        
        # Fall back to output_directory for backward compatibility
        output_dir = self.config.get("output_directory", "")
        if output_dir and Path(output_dir).exists():
            # Update both for consistency
            self.config["report_folder"] = output_dir
            self.config["last_used_folder"] = output_dir
            self.save_config()
            return Path(output_dir)
        
        # If no valid saved folder, prompt user
        return self.prompt_for_folder()
    
    def prompt_for_folder(self) -> Path:
        """
        Prompt user to choose a folder for reports.
        Saves the selection to config for future use.
        Uses last_used_folder as starting point for pre-selection.
        """
        initial_dir = self.get_last_used_folder()
        if not initial_dir or not Path(initial_dir).exists():
            initial_dir = self.get_report_folder()
            if not initial_dir or not Path(initial_dir).exists():
                initial_dir = Path.cwd()
        
        response = QMessageBox.question(
            None,
            "Reports Folder",
            "Select folder for saving reports:\n\n"
            "• Click 'Yes' to choose a custom folder\n"
            "• Click 'No' to use the default 'Reports' folder",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if response == QMessageBox.Yes:
            chosen_dir = QFileDialog.getExistingDirectory(
                None,
                "Select Reports Folder",
                str(initial_dir)
            )
            
            if chosen_dir:
                output_dir = Path(chosen_dir)
                QMessageBox.information(
                    None,
                    "Folder Selected",
                    f"Reports will be saved to:\n{output_dir}"
                )
            else:
                output_dir = Path.cwd() / "Reports"
                output_dir.mkdir(exist_ok=True)
                QMessageBox.information(
                    None,
                    "Reports Folder Created",
                    f"Created default 'Reports' folder at:\n{output_dir}"
                )
        else:
            output_dir = Path.cwd() / "Reports"
            output_dir.mkdir(exist_ok=True)
            QMessageBox.information(
                None,
                "Reports Folder",
                f"Using default 'Reports' folder at:\n{output_dir}"
            )
        
        # Save the chosen directory to BOTH config values
        self.config["report_folder"] = str(output_dir)
        self.config["last_used_folder"] = str(output_dir)
        self.save_config()
        
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
        current_report_folder = self.get_report_folder()
        if str(target_folder) != current_report_folder:
            self.config["report_folder"] = str(target_folder)
            self.config["last_used_folder"] = str(target_folder)
            self.save_config()
        
        return target_folder
    
    def get_initial_folder_for_dialog(self) -> str:
        """
        Get the initial folder path for file dialogs in main_window.py.
        Returns the last_used_folder for pre-selection.
        
        WARNING: Only use this for REPORT FOLDER selection dialogs.
        For image selection dialogs, use get_initial_folder_for_images() instead.
        """
        last_folder = self.get_last_used_folder()
        if last_folder and Path(last_folder).exists():
            return last_folder
        
        # Fallback to report_folder
        report_folder = self.get_report_folder()
        if report_folder and Path(report_folder).exists():
            return report_folder
        
        return str(Path.cwd())
    
    def get_initial_folder_for_images(self) -> str:
        """
        Get the initial folder path for IMAGE SELECTION dialogs.
        Uses user's home Pictures folder or Desktop as default.
        Does NOT affect or use the report folder persistence.
        """
        # Common image locations to try
        potential_locations = [
            Path.home() / "Pictures",
            Path.home() / "Desktop",
            Path.home() / "Downloads",
            Path.home() / "Documents",
            Path.cwd()
        ]
        
        # Return first existing location
        for location in potential_locations:
            if location.exists():
                return str(location)
        
        # Fallback to home directory
        return str(Path.home())
    
    def update_report_folder_from_dialog(self, selected_folder: str):
        """
        Call this ONLY after a REPORT FOLDER selection dialog.
        Updates both last_used_folder and report_folder in config.
        
        DO NOT use this for image selection dialogs.
        """
        if selected_folder:  # Only update if user actually selected something
            self.config["last_used_folder"] = selected_folder
            self.config["report_folder"] = selected_folder
            self.save_config()
    
    def update_folder_from_dialog(self, selected_folder: str):
        """
        DEPRECATED: Use update_report_folder_from_dialog() instead.
        Kept for backward compatibility.
        """
        try:
            path = Path(selected_folder)
            folder_path = path.parent if path.suffix else path
            self.update_report_folder_from_dialog(str(folder_path))
        except Exception:
            self.update_report_folder_from_dialog(selected_folder)
    
    # ===== REPORT NUMBER METHODS =====
    
    def get_next_report_number(self) -> tuple[int, str]:
        """Get next report number and format"""
        return self.config.get("last_report_number", 0) + 1, self.config.get("numbering_format", "{number}")
    
    def update_report_number(self, number: int, format_str: str):
        """Update report number in config"""
        self.config["last_report_number"] = number
        self.config["numbering_format"] = format_str
        self.save_config()
    
    def set_last_template_key(self, template_key: str):
        """Save the last used template key"""
        self.config["last_template_key"] = template_key
        self.save_config()
    
    def get_last_template_key(self) -> str:
        """Get the last used template key"""
        return self.config.get("last_template_key", "")
    
    def update_output_directory(self, new_directory: str):
        """Update output directory in config (for backward compatibility)"""
        self.config["output_directory"] = new_directory
        self.save_config()
    
    def reset_output_directory(self):
        """Reset output directory (e.g., for testing or user wants to change)"""
        self.config["output_directory"] = ""
        self.config["report_folder"] = ""
        self.config["last_used_folder"] = ""
        self.save_config()
    
    # ===== FILENAME GENERATION METHODS =====
    
    def generate_report_filename(self, report_number: int, first_name: str, middle_name: str, last_name: str, 
                                file_extension: str = "odt") -> str:
        """
        Generate a report filename in the new format:
        [Number]_Scammer report firstname middlename lastname.extension
        """
        # Clean and prepare name parts
        name_parts = []
        
        # Add first name if not empty
        if first_name and first_name.strip():
            name_parts.append(first_name.strip())
        
        # Add middle name if not empty
        if middle_name and middle_name.strip():
            name_parts.append(middle_name.strip())
        
        # Add last name if not empty
        if last_name and last_name.strip():
            name_parts.append(last_name.strip())
        
        # Join name parts with spaces
        name_string = " ".join(name_parts)
        
        # Generate filename in new format
        # Format: [Number]_Scammer report [Name]
        filename = f"{report_number}_Scammer report {name_string}.{file_extension}"
        
        # Remove any extra spaces and ensure clean filename
        filename = re.sub(r'\s+', ' ', filename).strip()
        
        return filename
    
    def generate_report_filename_from_full_name(self, report_number: int, full_name: str, 
                                               file_extension: str = "odt") -> str:
        """
        Generate a report filename from a single full name string.
        Parses the name into first/middle/last components.
        """
        # Clean the full name
        full_name = full_name.strip() if full_name else ""
        if not full_name:
            # If no name provided, use generic
            name_parts = ["Unknown"]
        else:
            # Split by whitespace and filter out empty parts
            parts = [p.strip() for p in full_name.split() if p.strip()]
            
            if len(parts) == 0:
                name_parts = ["Unknown"]
            elif len(parts) == 1:
                # Only one name part
                name_parts = [parts[0]]
            elif len(parts) == 2:
                # Two name parts: first and last
                name_parts = [parts[0], parts[1]]
            else:
                # Three or more name parts
                # First part = first name
                # Second part = middle name
                # Remaining parts = last name (combined)
                first_name = parts[0]
                middle_name = parts[1]
                last_name = " ".join(parts[2:])
                name_parts = [first_name, middle_name, last_name]
        
        # Join all name parts with spaces (regardless of how many)
        name_string = " ".join(name_parts)
        
        # Generate filename in new format
        # Format: [Number]_Scammer report [Name]
        filename = f"{report_number}_Scammer report {name_string}.{file_extension}"
        
        # Remove any extra spaces and ensure clean filename
        filename = re.sub(r'\s+', ' ', filename).strip()
        
        return filename
    
    def generate_report_filename_legacy(self, report_number: int, first_name: str, middle_name: str, last_name: str,
                                       file_extension: str = "odt") -> str:
        """
        Legacy filename format for backward compatibility:
        [Number]_Scammer_report_firstname_middlename_lastname.extension
        """
        # Clean and prepare name parts
        name_parts = []
        
        if first_name and first_name.strip():
            name_parts.append(first_name.strip())
        if middle_name and middle_name.strip():
            name_parts.append(middle_name.strip())
        if last_name and last_name.strip():
            name_parts.append(last_name.strip())
        
        # Join name parts with underscores (legacy format)
        name_string = "_".join(name_parts)
        
        # Generate filename in legacy format
        filename = f"{report_number}_Scammer_report_{name_string}.{file_extension}"
        
        return filename
    
    # ===== JSON DATA FOLDER METHODS =====
    
    def get_json_data_folder(self) -> Path:
        """
        Get or create the JSON data folder for storing report modification data.
        Returns the path to .report_data folder in the application root directory.
        """
        # Determine application root directory (where main.py or executable is)
        import sys
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller bundle - use executable directory, not temp bundle
                app_root = Path(sys.executable).parent
            else:
                app_root = Path(sys.executable).parent
        else:
            # Running as script - use script directory
            app_root = Path(__file__).parent.parent  # Go up from core/ to project root
        
        json_folder = app_root / self.JSON_DATA_FOLDER
        json_folder.mkdir(exist_ok=True)
        return json_folder
    
    def get_json_path_for_odt(self, odt_path: str) -> str:
        """
        Get the JSON file path for a given ODT file path.
        The JSON file will be stored in the JSON data folder with the same base filename.
        
        Args:
            odt_path: Path to the ODT file
            
        Returns:
            Path to the corresponding JSON file in the JSON data folder
        """
        odt_path_obj = Path(odt_path)
        json_folder = self.get_json_data_folder()
        json_filename = odt_path_obj.stem + '.json'  # Same name but .json extension
        return str(json_folder / json_filename)