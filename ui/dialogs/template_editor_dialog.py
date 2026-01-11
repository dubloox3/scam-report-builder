"""
Template Editor Dialog for Scam Report Builder
Dialog for creating/editing custom templates
"""

from typing import Dict, Any, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QCheckBox, QScrollArea, QWidget, QMessageBox, QGroupBox,
    QComboBox, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from core.template_manager import TemplateManager


class TemplateEditorDialog(QDialog):
    """Dialog for creating/editing custom templates"""
    
    template_saved = Signal(str)  # Emits template key when saved
    
    def __init__(self, parent=None, template_data: Optional[Dict[str, Any]] = None):
        """
        Initialize template editor dialog
        
        Args:
            parent: Parent widget
            template_data: Optional existing template data to edit
        """
        super().__init__(parent)
        self.template_data = template_data
        self.edited_template_key = None
        self.setup_ui()
        
        if template_data:
            self._load_template_data(template_data)
    
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Custom Template Editor")
        self.setMinimumSize(700, 600)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Create Custom Template" if not self.template_data else "Edit Custom Template")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Template Name
        name_layout = QVBoxLayout()
        name_label = QLabel("Template Name: (Type of scam)")
        name_layout.addWidget(name_label)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., Romance Scam, Tech Support Scam")
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # Description
        desc_layout = QVBoxLayout()
        desc_label = QLabel("Description: (Short summary)")
        desc_layout.addWidget(desc_label)
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Brief description of this template...")
        self.description_edit.setMaximumHeight(80)
        desc_layout.addWidget(self.description_edit)
        layout.addLayout(desc_layout)
        
        # Available Fields Section
        fields_group = QGroupBox("Select Fields to Include")
        fields_layout = QVBoxLayout(fields_group)
        
        # Scroll area for field checkboxes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(300)
        
        fields_widget = QWidget()
        fields_scroll_layout = QVBoxLayout(fields_widget)
        
        self.field_checkboxes = {}
        self.required_checkboxes = {}
        
        available_fields = TemplateManager.get_available_fields()
        
        # Group fields by category
        categories = {
            "Main Info": [],
            "Payment Information": [],
            "Evidence": [],
            "Remarks": []
        }
        
        # Fields that are always included (not selectable)
        always_included_fields = {'type', 'summary', 'remarks'}
        
        for field_key, field_def in available_fields.items():
            # Skip always-included fields
            if field_key in always_included_fields:
                continue
            
            category = field_def.get('category', 'Main Info')
            if category in categories:
                categories[category].append((field_key, field_def))
        
        # Create checkboxes grouped by category
        for category, fields in categories.items():
            if not fields:
                continue
                
            # Category label
            cat_label = QLabel(f"<b>{category}</b>")
            fields_scroll_layout.addWidget(cat_label)
            
            # Fields in this category
            for field_key, field_def in fields:
                field_layout = QHBoxLayout()
                
                # Include checkbox
                include_cb = QCheckBox(field_def['label'])
                include_cb.setObjectName(f"include_{field_key}")
                self.field_checkboxes[field_key] = include_cb
                field_layout.addWidget(include_cb)
                
                # Required checkbox (only enabled if included)
                required_cb = QCheckBox("Required")
                required_cb.setObjectName(f"required_{field_key}")
                required_cb.setEnabled(False)
                self.required_checkboxes[field_key] = required_cb
                field_layout.addWidget(required_cb)
                
                # Connect include checkbox to enable/disable required
                include_cb.toggled.connect(required_cb.setEnabled)
                
                field_layout.addStretch()
                fields_scroll_layout.addLayout(field_layout)
            
            # Spacing between categories
            fields_scroll_layout.addWidget(QLabel(""))  # Spacer
        
        scroll.setWidget(fields_widget)
        fields_layout.addWidget(scroll)
        layout.addWidget(fields_group)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save Template")
        save_btn.clicked.connect(self._save_template)
        save_btn.setDefault(True)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #0069d9;
            }
        """)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def _load_template_data(self, template_data: Dict[str, Any]):
        """Load existing template data into the form"""
        # Set name and description
        self.name_edit.setText(template_data.get('name', ''))
        self.description_edit.setPlainText(template_data.get('description', ''))
        
        # Mark included fields (skip always-included fields: type, summary, filename_name, remarks)
        template_fields = template_data.get('fields', {})
        always_included = {'type', 'summary', 'filename_name', 'remarks'}
        
        for field_key, field_def in template_fields.items():
            # Skip always-included fields (they're not in checkboxes)
            if field_key in always_included:
                continue
            
            if field_key in self.field_checkboxes:
                include_cb = self.field_checkboxes[field_key]
                include_cb.setChecked(True)
                
                # Set required if specified
                if field_key in self.required_checkboxes:
                    required_cb = self.required_checkboxes[field_key]
                    required_cb.setChecked(field_def.get('required', False))
    
    def _save_template(self):
        """Save the custom template"""
        # Validate name
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Please enter a template name.")
            return
        
        # Validate description
        description = self.description_edit.toPlainText().strip()
        if not description:
            QMessageBox.warning(self, "Validation Error", "Please enter a template description.")
            return
        
        # Always include these fields in custom templates
        always_included = {
            'type': {
                'type': 'text',
                'label': 'Type of scam',
                'category': 'Main Info'
            },
            'summary': {
                'type': 'text',
                'label': 'Short summary',
                'category': 'Main Info'
            },
            'filename_name': {
                'type': 'text',
                'label': 'Name for filename generation (This name will be used for the report filename)',
                'category': 'Main Info'
            },
            'remarks': {
                'type': 'list',
                'label': 'Remarks',
                'button': '+ Add remark',
                'category': 'Remarks'
            }
        }
        
        # Collect selected fields (always include required fields)
        selected_fields = always_included.copy()
        available_fields = TemplateManager.get_available_fields()
        
        for field_key, include_cb in self.field_checkboxes.items():
            if include_cb.isChecked():
                field_def = available_fields[field_key].copy()
                
                # Add required flag if checked
                if field_key in self.required_checkboxes:
                    required_cb = self.required_checkboxes[field_key]
                    if required_cb.isChecked():
                        field_def['required'] = True
                
                selected_fields[field_key] = field_def
        
        # Save template
        try:
            filename = TemplateManager.save_custom_template(
                name=name,
                description=description,
                fields=selected_fields
            )
            
            template_key = f"custom-{filename}"
            self.edited_template_key = template_key
            
            QMessageBox.information(
                self,
                "Template Saved",
                f"Template '{name}' has been saved successfully!\n"
                "You can now select it from the template list."
            )
            
            self.template_saved.emit(template_key)
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save template:\n{str(e)}"
            )
