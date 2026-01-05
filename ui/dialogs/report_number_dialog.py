"""
Report Number Dialog for Scam Report Builder
Dialog for setting report number and format.
"""

from datetime import datetime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
    QGroupBox, QCheckBox, QLineEdit, QDialogButtonBox,
    QWidget, QGridLayout
)
from PySide6.QtCore import Qt


class ReportNumberDialog(QDialog):
    """Dialog for setting report number and format"""
    
    def __init__(self, default_number: int, existing_alias_number: int = None, parent=None):
        super().__init__(parent)
        self.number = default_number
        self.format_str = "{number}"
        self.setup_ui(default_number, existing_alias_number)
    
    def setup_ui(self, default_number: int, existing_alias_number: int = None):
        """Setup the dialog UI"""
        self.setWindowTitle("Set Report Number")
        self.setFixedSize(450, 350)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Instructions
        instruction = QLabel("Set the report number for this scam report:")
        layout.addWidget(instruction)
        
        # Show existing alias info if provided
        if existing_alias_number:
            existing_label = QLabel(f"Existing reports for this scammer: up to #{existing_alias_number}")
            existing_label.setStyleSheet("color: #0066cc; font-weight: bold;")
            layout.addWidget(existing_label)
        
        # Number input
        number_layout = QHBoxLayout()
        number_layout.addWidget(QLabel("Report Number:"))
        
        self.number_spin = QSpinBox()
        self.number_spin.setRange(1, 9999)
        self.number_spin.setValue(default_number)
        self.number_spin.setMinimumWidth(100)
        
        number_layout.addWidget(self.number_spin)
        number_layout.addStretch()
        layout.addLayout(number_layout)
        
        # Format options
        format_group = QGroupBox("Numbering Format")
        format_layout = QVBoxLayout(format_group)
        
        # Simple format
        self.simple_radio = QCheckBox("Simple: 1, 2, 3...")
        self.simple_radio.setChecked(True)
        format_layout.addWidget(self.simple_radio)
        
        # Year format
        current_year = datetime.now().year
        self.year_radio = QCheckBox(f"With year: {current_year}-001, {current_year}-002...")
        format_layout.addWidget(self.year_radio)
        
        # Custom format
        self.custom_radio = QCheckBox("Custom format:")
        format_layout.addWidget(self.custom_radio)
        
        custom_widget = QWidget()
        custom_layout = QHBoxLayout(custom_widget)
        custom_layout.setContentsMargins(30, 0, 0, 0)
        
        self.custom_edit = QLineEdit()
        self.custom_edit.setPlaceholderText("e.g., SR-{number:03d}")
        self.custom_edit.setEnabled(False)
        custom_layout.addWidget(self.custom_edit)
        
        format_layout.addWidget(custom_widget)
        
        # Format examples
        examples_label = QLabel("Examples:\n"
                              "• Simple: {number} → 1, 2, 3\n"
                              "• Padded: {number:03d} → 001, 002, 003\n"
                              "• With prefix: SR-{number:04d} → SR-0001, SR-0002")
        examples_label.setStyleSheet("color: #666; font-size: 10pt; margin-top: 10px;")
        format_layout.addWidget(examples_label)
        
        layout.addWidget(format_group)
        layout.addStretch()
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._accept_dialog)
        button_box.rejected.connect(self.reject)
        
        # Style buttons
        ok_button = button_box.button(QDialogButtonBox.Ok)
        ok_button.setText("Use This Number")
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        
        cancel_button = button_box.button(QDialogButtonBox.Cancel)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        
        layout.addWidget(button_box)
        
        # Connect signals
        self.simple_radio.toggled.connect(self._update_format_enabled)
        self.year_radio.toggled.connect(self._update_format_enabled)
        self.custom_radio.toggled.connect(self._update_format_enabled)
        
        # Initial update
        self._update_format_enabled()
    
    def _update_format_enabled(self):
        """Update enabled state of format controls"""
        self.custom_edit.setEnabled(self.custom_radio.isChecked())
    
    def _accept_dialog(self):
        """Handle dialog acceptance"""
        self.number = self.number_spin.value()
        
        if self.simple_radio.isChecked():
            self.format_str = "{number}"
        elif self.year_radio.isChecked():
            year = datetime.now().year
            self.format_str = f"{year}-" + "{number:03d}"
        elif self.custom_radio.isChecked():
            self.format_str = self.custom_edit.text() or "{number}"
        
        self.accept()
    
    def get_values(self):
        """Get the selected values"""
        return self.number, self.format_str