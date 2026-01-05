"""
Template Selection Dialog for Scam Report Builder
Dialog for selecting the scam type template.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QDialog, QTextEdit
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPalette, QColor

from core.template_manager import TemplateManager


class TemplateSelectionDialog(QDialog):
    """Dialog for selecting a scam report template"""
    
    template_selected = Signal(str)  # Emits template key when selected
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_template = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Scam Report Builder - Select Template")
        self.setFixedSize(500, 400)
        
        # Set base palette for better text contrast
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255))
        palette.setColor(QPalette.WindowText, QColor(33, 37, 41))
        palette.setColor(QPalette.Text, QColor(33, 37, 41))
        self.setPalette(palette)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Scam Report Builder")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #212529;")
        layout.addWidget(title)
        
        # Template selection label
        select_label = QLabel("Select the type of scam report to create:")
        select_label.setStyleSheet("color: #212529;")
        layout.addWidget(select_label)
        
        # Template selection
        self.template_combo = QComboBox()
        templates = TemplateManager.get_all_templates()
        
        for key, template in templates.items():
            self.template_combo.addItem(template['name'], key)
        
        self.template_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 6px 12px;
                color: #212529;
                min-height: 34px;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 1px solid #dee2e6;
                color: #212529;
                selection-background-color: #007bff;
                selection-color: white;
            }
        """)
        layout.addWidget(self.template_combo)
        
        # Description area
        desc_label = QLabel("Description:")
        desc_label.setStyleSheet("color: #212529;")
        layout.addWidget(desc_label)
        
        self.description_text = QTextEdit()
        self.description_text.setReadOnly(True)
        self.description_text.setMaximumHeight(100)
        self.description_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                color: #212529;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
                line-height: 1.4;
            }
            QTextEdit:focus {
                border: 1px solid #007bff;
            }
        """)
        layout.addWidget(self.description_text)
        
        # Update description when selection changes
        self.template_combo.currentIndexChanged.connect(self._update_description)
        self._update_description()  # Initial update
        
        # Instructions - Updated text
        instructions = QLabel(
            "After selecting a template, you'll be able to fill in the details and generate a scam report."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("""
            QLabel {
                color: #495057;
                font-style: italic;
                padding: 8px;
                background-color: #f8f9fa;
                border-radius: 4px;
                border: 1px solid #e9ecef;
            }
        """)
        layout.addWidget(instructions)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                border-radius: 4px;
                background-color: #6c757d;
                color: white;
                border: none;
                font-weight: 500;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #545b62;
            }
        """)
        button_layout.addWidget(cancel_btn)
        
        select_btn = QPushButton("Select Template")
        select_btn.clicked.connect(self._select_template)
        select_btn.setDefault(True)
        select_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                border-radius: 4px;
                background-color: #007bff;
                color: white;
                font-weight: 600;
                border: none;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #0069d9;
            }
            QPushButton:pressed {
                background-color: #0062cc;
            }
        """)
        button_layout.addWidget(select_btn)
        
        layout.addLayout(button_layout)
    
    def _update_description(self):
        """Update the description based on selected template"""
        key = self.template_combo.currentData()
        if key:
            template = TemplateManager.get_template(key)
            if template:
                self.description_text.setText(template['description'])
                # Ensure text color is visible
                self.description_text.setStyleSheet("""
                    QTextEdit {
                        background-color: white;
                        color: #212529;
                        border: 1px solid #dee2e6;
                        border-radius: 4px;
                        padding: 8px;
                        font-size: 14px;
                        line-height: 1.4;
                    }
                """)
    
    def _select_template(self):
        """Handle template selection"""
        key = self.template_combo.currentData()
        if key:
            self.selected_template = key
            self.template_selected.emit(key)
            self.accept()