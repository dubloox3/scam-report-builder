"""
Main entry point for Scam Report Builder
"""
import sys
import os
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox, QFileDialog
from PySide6.QtCore import Qt  # ADD THIS IMPORT

from ui.dialogs.template_selection_dialog import TemplateSelectionDialog
from ui.main_window import ScamReportBuilder
from core.config_manager import ConfigManager


def prompt_report_folder() -> Path:
    """Prompt user for report folder location on first run"""
    config = ConfigManager()
    
    # Check if folder already configured
    saved_folder = config.get_report_folder()
    if saved_folder and Path(saved_folder).exists():
        return Path(saved_folder)
    
    # Determine script directory - handle EXE mode
    if getattr(sys, 'frozen', False):
        # Running as EXE/pyinstaller bundle
        # sys._MEIPASS contains the bundle directory
        if hasattr(sys, '_MEIPASS'):
            script_dir = Path(sys._MEIPASS)
        else:
            script_dir = Path(sys.executable).parent
    else:
        # Running as normal Python script
        script_dir = Path(__file__).parent
    
    # Ask user for folder choice
    msg = QMessageBox()
    msg.setWindowTitle("Report Folder Setup")
    msg.setText("Choose where to save scam reports:")
    msg.setInformativeText(
        "You can select an existing folder or create a new 'Reports' folder "
        "in the application directory."
    )
    
    # Create buttons and get references
    existing_btn = msg.addButton("Use Existing Folder", QMessageBox.ActionRole)
    create_btn = msg.addButton("Create Reports Folder", QMessageBox.AcceptRole)
    msg.setDefaultButton(create_btn)  # Set the actual button as default
    
    ret = msg.exec()
    clicked_button = msg.clickedButton()
    
    if clicked_button == create_btn:  # Create Reports folder
        reports_dir = script_dir / "Reports"
        reports_dir.mkdir(exist_ok=True)
        folder_path = reports_dir
    else:  # Use existing folder
        folder = QFileDialog.getExistingDirectory(
            None,
            "Select Reports Folder",
            str(script_dir)
        )
        if not folder:  # User cancelled
            folder_path = script_dir / "Reports"
            folder_path.mkdir(exist_ok=True)
        else:
            folder_path = Path(folder)
    
    # Save to config
    config.set_report_folder(str(folder_path))
    config.save_config()
    
    return folder_path


def main():
    """Main application entry point"""
    # Set up high DPI scaling for better display on high-res screens
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application metadata
    app.setApplicationName("Scam Report Builder")
    app.setOrganizationName("ScamBaitingTools")
    
    # Setup report folder on first run
    try:
        reports_folder = prompt_report_folder()
        if not reports_folder.exists():
            reports_folder.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        QMessageBox.critical(
            None,
            "Folder Error",
            f"Could not setup reports folder: {str(e)}\n"
            "Application will exit."
        )
        sys.exit(1)
    
    # Show template selection dialog
    template_dialog = TemplateSelectionDialog()
    template_dialog.show()
    app.exec()
    
    if not template_dialog.selected_template:
        sys.exit(0)
    
    # Launch main application window with selected template
    window = ScamReportBuilder(template_dialog.selected_template)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
