"""
Main Window for Scam Report Builder
Primary application interface with tab-based form.
"""

import re
import os
import json
import base64
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QDateEdit, QScrollArea, QGroupBox,
    QMessageBox, QFileDialog, QTabWidget, QDialog
)
from ui.dialogs.template_editor_dialog import TemplateEditorDialog
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont

from core.config_manager import ConfigManager
from core.template_manager import TemplateManager
from ui.widgets.dynamic_list_widget import DynamicListWidget
from ui.widgets.image_list_widget import ImageListWidget
from ui.widgets.other_payment_widget import OtherPaymentWidget
from ui.dialogs.report_number_dialog import ReportNumberDialog


class ScamReportBuilder(QMainWindow):
    """Main application window for building scam reports"""
    
    def __init__(self, template_key: str):
        super().__init__()
        self.template_key = template_key
        self.template = TemplateManager.get_template(template_key)
        self.report_number = None
        self.report_format = None
        self.last_saved_json_path = None  # Store path to last saved JSON for modification
        self.original_odt_path = None  # Store original ODT path when modifying
        
        if not self.template:
            raise ValueError(f"Template '{template_key}' not found")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the main window UI"""
        # Update window title with corrected template name
        display_name = self.template['name']
        if display_name == "Advance-Fee Scam (419)":
            display_name = "Advance-Fee Scam"
        
        self.setWindowTitle(f"Scam Report Builder - {display_name}")
        self.setMinimumSize(1000, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        self.tab_widget = QTabWidget()
        
        self.main_info_tab = QWidget()
        self.payment_tab = QWidget()
        self.evidence_tab = QWidget()
        self.remarks_tab = QWidget()
        
        self._build_main_info_tab()
        self._build_payment_tab()
        self._build_evidence_tab()
        self._build_remarks_tab()
        
        self.tab_widget.addTab(self.main_info_tab, "Main Info")
        self.tab_widget.addTab(self.payment_tab, "Payment Information")
        self.tab_widget.addTab(self.evidence_tab, "Evidence")
        self.tab_widget.addTab(self.remarks_tab, "Remarks")
        
        main_layout.addWidget(self.tab_widget)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Save as Template button
        self.save_template_btn = QPushButton("Save as Template")
        self.save_template_btn.clicked.connect(self._save_as_template)
        self.save_template_btn.setFixedHeight(40)
        self.save_template_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        button_layout.addWidget(self.save_template_btn)
        
        # Create Report button
        self.export_btn = QPushButton("Create Scam Report")
        self.export_btn.clicked.connect(self._export_report)
        self.export_btn.setFixedHeight(40)
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        button_layout.addWidget(self.export_btn)
        
        main_layout.addLayout(button_layout)
    
    def _build_tab(self, tab_widget: QWidget, fields_to_include: List[str]):
        """Build a tab with specified fields"""
        layout = QVBoxLayout(tab_widget)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setAlignment(Qt.AlignTop)
        
        fields = self.template['fields']
        for key in fields_to_include:
            if key in fields:
                self._create_field_widget(key, fields[key], content_layout)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
    
    def _create_field_widget(self, key: str, field_def: Dict[str, Any], layout: QVBoxLayout):
        """Create widget for a field based on its type"""
        field_type = field_def['type']
        
        if field_type == 'text':
            # Handle custom labels for specific fields
            if key == 'scammer_names':
                label = "Scammers real name:"
            else:
                label = field_def['label']
            
            field_layout = QHBoxLayout()
            field_layout.addWidget(QLabel(label))
            
            widget = QLineEdit()
            
            # Handle custom placeholder for other_payments
            if key == 'other_payments':
                widget.setPlaceholderText("Enter other payment details here...")
            else:
                widget.setText(field_def.get('default', ''))
            
            setattr(self, f"{key}_field", widget)
            
            field_layout.addWidget(widget)
            
            if field_def.get('required'):
                req_label = QLabel("(required)")
                req_label.setStyleSheet("color: red; font-weight: bold;")
                field_layout.addWidget(req_label)
            
            field_layout.addStretch()
            layout.addLayout(field_layout)
            
        elif field_type == 'date':
            field_layout = QHBoxLayout()
            field_layout.addWidget(QLabel(f"{field_def['label']}:"))
            
            widget = QDateEdit()
            widget.setCalendarPopup(True)
            widget.setDate(QDate.currentDate())
            widget.setDisplayFormat("MM/dd/yy")
            setattr(self, f"{key}_field", widget)
            
            field_layout.addWidget(widget)
            field_layout.addStretch()
            layout.addLayout(field_layout)
            
        elif field_type == 'multiline':
            layout.addWidget(QLabel(f"{field_def['label']}:"))
            
            widget = QTextEdit()
            widget.setPlaceholderText(field_def.get('placeholder', ''))
            widget.setMaximumHeight(150)
            setattr(self, f"{key}_field", widget)
            
            layout.addWidget(widget)
            
        elif field_type == 'list':
            # Get default values from template if they exist
            default_values = field_def.get('default', [])
            
            # Apply specific label, button text, and placeholder changes for 'alias' field
            if key == 'alias':
                label = "Scammers main alias (This name will be used for the report filename)"
                button_text = "+Add other scammer aliases"
                # Update placeholder for first entry
                if default_values:
                    default_values[0] = default_values[0] if default_values[0] != "Enter value..." else "Enter scammers main alias..."
            else:
                label = field_def['label']
                button_text = field_def.get('button', '+ Add')
            
            widget = DynamicListWidget(
                label=label,
                button_text=button_text,
                required=field_def.get('required', False),
                default_values=default_values
            )
            
            setattr(self, f"{key}_widget", widget)
            layout.addWidget(widget)
            
        elif field_type == 'image_list' or field_type == 'images':
            # Handle both 'image_list' (old) and 'images' (new) types
            widget = ImageListWidget(
                label=field_def['label'],
                button_text=field_def.get('button', '+ Add')
            )
            setattr(self, f"{key}_widget", widget)
            layout.addWidget(widget)
            
        elif field_type == 'other_payments':
            widget = OtherPaymentWidget()
            setattr(self, f"{key}_widget", widget)
            layout.addWidget(widget)
    
    def _build_main_info_tab(self):
        """Build the Main Info tab"""
        # Get fields from template sections
        sections = self.template.get('sections', {})
        fields = sections.get('Main Info:', [])
        if not fields:
            # Fallback for templates without sections (backward compatibility)
            fields = ['type', 'summary', 'alias', 'emails', 'websites', 'ips', 'locations', 'started']
        self._build_tab(self.main_info_tab, fields)
        
        # For custom templates, populate type and summary fields with template name/description
        if self.template_key.startswith('custom-'):
            template_name = self.template.get('name', '')
            template_description = self.template.get('description', '')
            
            # Set type field
            if hasattr(self, 'type_field'):
                self.type_field.setText(template_name)
            
            # Set summary field
            if hasattr(self, 'summary_field'):
                self.summary_field.setText(template_description)
    
    def _build_payment_tab(self):
        """Build the Payment Information tab"""
        # Get fields from template sections
        sections = self.template.get('sections', {})
        fields = sections.get('Payment Information:', [])
        if not fields:
            # Fallback for templates without sections (backward compatibility)
            fields = ['amount', 'bank_info', 'other_payments']
        
        layout = QVBoxLayout(self.payment_tab)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setAlignment(Qt.AlignTop)
        
        fields_def = self.template['fields']
        
        for key in fields:
            if key in fields_def:
                if key == 'bank_info':
                    field_def = fields_def[key]
                    self._create_bank_info_widget(field_def, content_layout)
                else:
                    self._create_field_widget(key, fields_def[key], content_layout)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
    
    def _create_bank_info_widget(self, field_def: Dict[str, Any], layout: QVBoxLayout):
        """Create widget for multiple bank accounts"""
        label = field_def.get('label', 'Bank Information')
        
        group_box = QGroupBox(label)
        group_layout = QVBoxLayout(group_box)
        
        bank_accounts_widget = QWidget()
        self.bank_accounts_layout = QVBoxLayout(bank_accounts_widget)
        self.bank_accounts_layout.setSpacing(10)
        
        self.bank_account_fields = []
        
        self._add_bank_account_field(self.bank_accounts_layout)
        
        group_layout.addWidget(bank_accounts_widget)
        
        add_button = QPushButton("+ Add Bank Account")
        add_button.setMaximumWidth(200)
        add_button.clicked.connect(lambda: self._add_bank_account_field(self.bank_accounts_layout))
        group_layout.addWidget(add_button, alignment=Qt.AlignLeft)
        
        layout.addWidget(group_box)
    
    def _add_bank_account_field(self, layout: QVBoxLayout):
        """Add a new bank account field to the layout with remove button"""
        account_container = QWidget()
        account_layout = QVBoxLayout(account_container)
        account_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create horizontal layout for label and remove button
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 5)
        
        account_num = len(self.bank_account_fields) + 1
        account_label = QLabel(f"Bank Account #{account_num}:")
        account_label.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(account_label)
        
        header_layout.addStretch()
        
        # Add remove button (only show if there's more than one account)
        remove_button = QPushButton("✕")
        remove_button.setMaximumWidth(30)
        remove_button.setMaximumHeight(25)
        remove_button.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                font-weight: bold;
                border-radius: 3px;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
        """)
        remove_button.clicked.connect(lambda: self._remove_bank_account_field(account_container))
        header_layout.addWidget(remove_button)
        
        account_layout.addLayout(header_layout)
        
        # Create multiline text edit for bank info (5 lines high)
        bank_info_edit = QTextEdit()
        bank_info_edit.setPlaceholderText("Enter bank account details (bank name, account number, SWIFT/BIC, etc.)")
        bank_info_edit.setMaximumHeight(100)  # Approximately 5 lines
        bank_info_edit.setAcceptRichText(False)
        
        account_layout.addWidget(bank_info_edit)
        
        # Store reference to the field
        self.bank_account_fields.append((account_container, bank_info_edit))
        
        # Add to the parent layout
        layout.addWidget(account_container)
        
        # Update remove button visibility
        self._update_remove_button_visibility()
    
    def _remove_bank_account_field(self, account_container):
        """Remove a bank account field from the layout"""
        # Find and remove the account container from our list
        for i, (container, edit) in enumerate(self.bank_account_fields):
            if container == account_container:
                # Remove from layout
                self.bank_accounts_layout.removeWidget(container)
                # Remove from our list
                self.bank_account_fields.pop(i)
                # Delete the widget
                container.deleteLater()
                break
        
        # Renumber remaining accounts
        self._renumber_bank_accounts()
        # Update remove button visibility
        self._update_remove_button_visibility()
    
    def _renumber_bank_accounts(self):
        """Update the labels for all bank accounts"""
        for i, (container, edit) in enumerate(self.bank_account_fields):
            # Find the label in the container
            header_layout = container.layout().itemAt(0).layout()
            if header_layout:
                label_widget = header_layout.itemAt(0).widget()
                if isinstance(label_widget, QLabel):
                    label_widget.setText(f"Bank Account #{i + 1}:")
    
    def _update_remove_button_visibility(self):
        """Show/hide remove buttons based on number of accounts"""
        # Show remove button only if there's more than one account
        for container, edit in self.bank_account_fields:
            header_layout = container.layout().itemAt(0).layout()
            if header_layout:
                remove_button = header_layout.itemAt(2).widget()
                if isinstance(remove_button, QPushButton):
                    remove_button.setVisible(len(self.bank_account_fields) > 1)
    
    def _get_bank_accounts_data(self):
        """Get all bank account data as a list of strings"""
        accounts = []
        for container, field in self.bank_account_fields:
            text = field.toPlainText().strip()
            if text:
                accounts.append(text)
        return accounts
    
    def _build_evidence_tab(self):
        """Build the Evidence tab"""
        template_fields = self.template['fields']
        
        # Use a prioritized list of fields we want to include
        desired_field_order = [
            'scammer_names',
            'passport_ids', 
            'scammer_photos',
            'victim_ids',
            'others'
        ]
        
        # Build final list in desired order, only including fields that exist
        fields = []
        for field in desired_field_order:
            if field in template_fields:
                fields.append(field)
        
        # If 'others' is not in the standard list, look for any field with 'other' in the name
        if 'others' not in fields:
            for field_name, field_def in template_fields.items():
                field_lower = field_name.lower()
                field_type = field_def.get('type', 'unknown')
                if ('other' in field_lower and 
                    field_name not in fields and
                    field_type in ['images', 'image_list']):
                    fields.append(field_name)
                    break
        
        self._build_tab(self.evidence_tab, fields)
    
    def _build_remarks_tab(self):
        """Build the Remarks tab"""
        # Get fields from template sections
        sections = self.template.get('sections', {})
        fields = sections.get('Remarks:', [])
        if not fields:
            # Fallback for templates without sections (backward compatibility)
            fields = ['remarks']
        self._build_tab(self.remarks_tab, fields)
    
    def _get_report_number(self) -> bool:
        """Get report number from user"""
        config_manager = ConfigManager()
        # Reload config to ensure we have the latest report number
        config_manager.reload_config()
        default_number, default_format = config_manager.get_next_report_number()
        dialog = ReportNumberDialog(default_number)
        
        if dialog.exec() == QDialog.Accepted:
            self.report_number, self.report_format = dialog.get_values()
            return True
        return False
    
    def _validate_form(self) -> bool:
        """Validate form data"""
        errors = []
        fields = self.template['fields']
        
        for key, field_def in fields.items():
            if field_def.get('required', False):
                if field_def['type'] == 'text':
                    widget = getattr(self, f"{key}_field", None)
                    if widget and not widget.text().strip():
                        errors.append(f"{field_def['label']} is required")
                        
                elif field_def['type'] == 'list':
                    widget = getattr(self, f"{key}_widget", None)
                    if widget and not widget.is_valid():
                        errors.append(f"{field_def['label']} requires at least one entry")
        
        if errors:
            QMessageBox.warning(self, "Validation Error", "\n".join(errors))
            return False
        return True
    
    def _collect_data(self) -> Tuple[Dict[str, Any], Dict[str, List[Tuple[str, bytes]]]]:
        """Collect all form data and images"""
        data = {}
        images = {}
        fields = self.template['fields']
        
        for key, field_def in fields.items():
            field_type = field_def['type']
            
            if field_type == 'text':
                widget = getattr(self, f"{key}_field", None)
                if widget:
                    value = widget.text().strip()
                    if value:
                        data[key] = value
                    elif field_def.get('default'):
                        data[key] = field_def['default']
                        
            elif field_type == 'date':
                widget = getattr(self, f"{key}_field", None)
                if widget:
                    data[key] = widget.date().toString("MM/dd/yy")
                    
            elif field_type == 'multiline':
                widget = getattr(self, f"{key}_field", None)
                if widget:
                    value = widget.toPlainText().strip()
                    if value:
                        data[key] = value
                    
            elif field_type == 'list':
                widget = getattr(self, f"{key}_widget", None)
                if widget:
                    values = widget.get_values()
                    if values:
                        data[key] = values
                        
            elif field_type == 'other_payments':
                widget = getattr(self, f"{key}_widget", None)
                if widget:
                    payment_data = widget.get_data()
                    if payment_data:
                        data[key] = payment_data
                        
            elif field_type == 'image_list' or field_type == 'images':
                widget = getattr(self, f"{key}_widget", None)
                if widget:
                    image_list = widget.get_images()
                    if image_list:
                        images[key] = image_list
        
        if hasattr(self, 'bank_account_fields'):
            bank_accounts = self._get_bank_accounts_data()
            if bank_accounts:
                data['bank_info'] = bank_accounts
        
        return data, images
    
    def _save_as_template(self):
        """Save current template as a custom template"""
        from core.template_manager import TemplateManager
        
        # Get current template data
        current_template = self.template
        
        # Pre-fill template editor with current template
        editor = TemplateEditorDialog(self, template_data=current_template)
        
        def on_template_saved(template_key):
            QMessageBox.information(
                self,
                "Template Saved",
                "Custom template saved successfully!\n"
                "You can select it from the template list next time."
            )
        
        editor.template_saved.connect(on_template_saved)
        editor.exec()
    
    def _export_report(self):
        """Export report to ODT file"""
        if not self._validate_form():
            return
        
        # Check if this is a modification by checking if we have a saved JSON path
        # This is the most reliable indicator that we're modifying an existing report
        last_json = getattr(self, 'last_saved_json_path', None)
        is_modification = (
            last_json is not None 
            and Path(last_json).exists()
            and self.report_number is not None
            and self.report_format is not None
        )
        
        # Only show report number dialog for new reports
        if not is_modification:
            if not self._get_report_number():
                return
        
        report_data, images = self._collect_data()
        
        # Generate formatted report number for the data
        if self.report_number and self.report_format:
            try:
                formatted_number = self.report_format.format(number=self.report_number)
            except:
                formatted_number = str(self.report_number)
            report_data['report_number'] = formatted_number
        
        config_manager = ConfigManager()
        
        # If modifying and we have the original ODT path, use it as the default
        # Otherwise, generate a new filename
        original_path = getattr(self, 'original_odt_path', None)
        if is_modification and original_path:
            # Use the original filename when modifying - this preserves the report number
            # Don't check if file exists - user might have moved/deleted it, but we want to preserve the number
            initial_path = original_path
            initial_folder = str(Path(original_path).parent) if Path(original_path).parent.exists() else None
        else:
            # Generate new filename for new reports
            scammer_name = ""
            
            # Check if this is a custom template without alias field
            is_custom_template = self.template_key.startswith('custom-')
            has_alias_field = 'alias' in self.template.get('fields', {})
            
            if is_custom_template and not has_alias_field:
                # Use filename_name field for custom templates without alias
                scammer_name = report_data.get('filename_name', '')
            elif report_data.get('alias'):
                # Use alias field for built-in templates or custom templates with alias
                scammer_name = report_data['alias'][0] if isinstance(report_data['alias'], list) else str(report_data['alias'])
            
            # Generate filename using the new config_manager method
            filename = config_manager.generate_report_filename_from_full_name(
                report_number=self.report_number,
                full_name=scammer_name,
                file_extension="odt"
            )
            
            # Check if filename generation succeeded
            if not filename:
                # Fallback to old filename format
                clean_alias = re.sub(r'[^\w\s-]', '', scammer_name)
                clean_alias = re.sub(r'[-\s]+', '_', clean_alias)
                clean_alias = clean_alias[:50] or "unknown"
                filename = f"{self.report_number}_Scammer_report_{clean_alias}.odt"
            
            # Get the report folder that was set at startup
            initial_folder = config_manager.get_report_folder()
            
            # If no report folder is set, fall back to get_initial_folder_for_dialog
            if not initial_folder or not Path(initial_folder).exists():
                initial_folder = config_manager.get_initial_folder_for_dialog()
            
            # Ensure initial_folder is actually a directory, not a file
            if initial_folder:
                initial_folder_path = Path(initial_folder)
                # Check if it's a file (has extension or doesn't exist as directory)
                if initial_folder_path.suffix or not initial_folder_path.is_dir():
                    # It's likely a file path, get the parent directory
                    initial_folder = str(initial_folder_path.parent)
            
            # Prepare the initial path for the dialog
            initial_path = str(Path(initial_folder) / filename) if initial_folder else filename
        
        # IMPORTANT: Save and restore the current working directory
        # This prevents image selection dialogs from interfering with report save location
        current_dir = os.getcwd()
        
        try:
            # When modifying, use the full original path directly (Qt will handle the path)
            # For new reports, change to the folder first
            if not (is_modification and original_path):
                if initial_folder and Path(initial_folder).exists() and Path(initial_folder).is_dir():
                    os.chdir(str(initial_folder))
                    # Use just the filename when we've changed directory
                    if not is_modification:
                        initial_path = filename
            
            # Use native Windows file dialog for saving reports
            # This will show "Save" dialog (not "Open") and use Windows Explorer UI
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Save Report",
                initial_path,
                "ODT Files (*.odt)"
            )
            
        finally:
            # Always restore the original directory
            os.chdir(current_dir)
        
        if file_path:
            try:
                # Update the last used folder in config using the directory portion
                config_manager.update_report_folder_from_dialog(str(Path(file_path).parent))
                
                # Update report number in config (only if this is a new report, not a modification)
                # Check if this is a modification by seeing if we have a saved JSON path
                is_modification = getattr(self, 'last_saved_json_path', None) is not None
                if not is_modification:
                    config_manager.update_report_number(self.report_number, self.report_format)
                    # Save template_key for "New Report" feature
                    config_manager.set_last_template_key(self.template_key)
                
                # Generate the ODT file
                from core.odt_generator import ODTGenerator
                
                success = ODTGenerator.create_odt(
                    content=report_data,
                    output_path=file_path,
                    images=images,
                    template_key=self.template_key
                )
                
                if success:
                    # Save report data to JSON file for modification capability
                    # JSON files are stored in the JSON data folder, not next to ODT files
                    # If modifying, use the same JSON path; otherwise create new one
                    last_json = getattr(self, 'last_saved_json_path', None)
                    if last_json and Path(last_json).exists():
                        json_path = last_json
                    else:
                        # Get JSON path from config manager (uses dedicated JSON data folder)
                        json_path = config_manager.get_json_path_for_odt(file_path)
                    
                    self._save_report_data_to_json(report_data, images, json_path, file_path)
                    
                    # Show success dialog with options
                    self._show_success_dialog(file_path, json_path)
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        "Failed to generate ODT file. Please check the console for details."
                    )
                    
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to save report:\n{str(e)}"
                )
    
    def _save_report_data_to_json(self, report_data: Dict[str, Any], images: Dict[str, List[Tuple[str, bytes]]], json_path: str, odt_path: str = None):
        """Save report data to JSON file for modification capability"""
        try:
            # Convert images to base64 for JSON storage
            images_data = {}
            for category, img_list in images.items():
                images_data[category] = []
                for img_name, img_bytes in img_list:
                    if img_bytes:
                        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                        images_data[category].append({
                            'name': img_name,
                            'data': img_base64
                        })
            
            # If this is a modification and we have the original path, preserve it
            # Otherwise, use the current ODT path
            original_odt = odt_path if odt_path else None
            
            # Combine data and images
            save_data = {
                'report_data': report_data,
                'images': images_data,
                'template_key': self.template_key,
                'report_number': self.report_number,
                'report_format': self.report_format,
                'original_odt_path': original_odt
            }
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            self.last_saved_json_path = json_path
        except Exception:
            pass  # Silent failure - JSON save is non-critical for report generation
    
    def _show_success_dialog(self, odt_path: str, json_path: str):
        """Show success dialog with options for New Report and Modify Report"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Report Created Successfully")
        msg.setText(f"Report #{self.report_number} saved to:\n{odt_path}")
        msg.setIcon(QMessageBox.Information)
        
        # Add custom buttons
        new_report_btn = msg.addButton("New Report", QMessageBox.ActionRole)
        modify_btn = msg.addButton("Modify Report", QMessageBox.ActionRole)
        close_btn = msg.addButton("Close", QMessageBox.AcceptRole)
        
        # Style buttons
        new_report_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        modify_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        
        msg.exec()
        clicked_button = msg.clickedButton()
        
        if clicked_button == new_report_btn:
            self._clear_form()
        elif clicked_button == modify_btn:
            self._load_report_from_json(json_path)
    
    def _clear_form(self):
        """Clear all form fields for a new report"""
        fields = self.template['fields']
        
        for key, field_def in fields.items():
            field_type = field_def['type']
            
            if field_type == 'text':
                widget = getattr(self, f"{key}_field", None)
                if widget:
                    widget.clear()
                    # Restore default if exists
                    if field_def.get('default'):
                        widget.setText(field_def['default'])
                        
            elif field_type == 'date':
                widget = getattr(self, f"{key}_field", None)
                if widget:
                    widget.setDate(QDate.currentDate())
                    
            elif field_type == 'multiline':
                widget = getattr(self, f"{key}_field", None)
                if widget:
                    widget.clear()
                    
            elif field_type == 'list':
                widget = getattr(self, f"{key}_widget", None)
                if widget:
                    widget.clear_all()
                    # Restore default if exists
                    default_values = field_def.get('default', [])
                    if default_values:
                        # Clear again to remove the empty entry that clear_all might leave
                        widget.clear_all()
                        for value in default_values:
                            widget._add_entry_with_value(value)
                    elif not widget.required:
                        # If not required and no defaults, ensure at least one empty entry exists
                        if len(widget.widgets) == 0:
                            widget._add_entry()
                            
            elif field_type == 'other_payments':
                widget = getattr(self, f"{key}_widget", None)
                if widget:
                    widget.clear()
                    
            elif field_type == 'image_list' or field_type == 'images':
                widget = getattr(self, f"{key}_widget", None)
                if widget:
                    widget.clear_images()
        
        # Clear bank accounts - keep one empty field
        if hasattr(self, 'bank_account_fields'):
            # Remove all but the first one
            while len(self.bank_account_fields) > 1:
                container, _ = self.bank_account_fields[-1]
                self._remove_bank_account_field(container)
            # Clear the remaining bank account field
            if self.bank_account_fields:
                _, field = self.bank_account_fields[0]
                field.clear()
        
        # Reset report number and JSON path for new report
        self.report_number = None
        self.report_format = None
        self.last_saved_json_path = None
        self.original_odt_path = None
        
        # For custom templates, re-populate type and summary fields with template name/description
        if self.template_key.startswith('custom-'):
            template_name = self.template.get('name', '')
            template_description = self.template.get('description', '')
            
            # Set type field
            if hasattr(self, 'type_field'):
                self.type_field.setText(template_name)
            
            # Set summary field
            if hasattr(self, 'summary_field'):
                self.summary_field.setText(template_description)
        
        # Switch to first tab
        self.tab_widget.setCurrentIndex(0)
    
    def _load_report_from_json(self, json_path: str):
        """Load report data from JSON file back into the form"""
        try:
            if not Path(json_path).exists():
                QMessageBox.warning(
                    self,
                    "File Not Found",
                    f"Report data file not found:\n{json_path}\n\nCannot modify report."
                )
                return
            
            with open(json_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            report_data = save_data.get('report_data', {})
            images_data = save_data.get('images', {})
            # Preserve report number and format BEFORE clearing form
            saved_report_number = save_data.get('report_number')
            saved_report_format = save_data.get('report_format', '{number}')
            # Load the original ODT path if it exists
            original_odt = save_data.get('original_odt_path')
            
            # If no original path is saved, try to find ODT file in report folder
            if not original_odt:
                from core.config_manager import ConfigManager
                config_manager = ConfigManager()
                report_folder = config_manager.get_report_folder()
                if report_folder:
                    json_path_obj = Path(json_path)
                    odt_filename = json_path_obj.stem + '.odt'  # Same name but .odt extension
                    potential_odt = Path(report_folder) / odt_filename
                    if potential_odt.exists():
                        original_odt = str(potential_odt)
                    else:
                        # Default to report folder with the filename (even if file doesn't exist yet)
                        original_odt = str(potential_odt)
            
            # Clear form first (this will reset report_number, but we'll restore it)
            self._clear_form()
            
            # Restore report number and format after clearing
            self.report_number = saved_report_number
            self.report_format = saved_report_format
            self.original_odt_path = original_odt
            self.last_saved_json_path = json_path
            
            # Load data into form
            fields = self.template['fields']
            
            for key, field_def in fields.items():
                field_type = field_def['type']
                
                if field_type == 'text':
                    widget = getattr(self, f"{key}_field", None)
                    if widget and key in report_data:
                        widget.setText(str(report_data[key]))
                        
                elif field_type == 'date':
                    widget = getattr(self, f"{key}_field", None)
                    if widget and key in report_data:
                        date_str = report_data[key]
                        try:
                            # Parse MM/dd/yy format
                            date_obj = datetime.strptime(date_str, "%m/%d/%y")
                            widget.setDate(QDate(date_obj.year, date_obj.month, date_obj.day))
                        except:
                            pass
                            
                elif field_type == 'multiline':
                    widget = getattr(self, f"{key}_field", None)
                    if widget and key in report_data:
                        widget.setPlainText(str(report_data[key]))
                        
                elif field_type == 'list':
                    widget = getattr(self, f"{key}_widget", None)
                    if widget and key in report_data:
                        values = report_data[key]
                        if isinstance(values, list):
                            widget.clear_all()
                            for value in values:
                                widget._add_entry_with_value(str(value))
                            
                elif field_type == 'other_payments':
                    widget = getattr(self, f"{key}_widget", None)
                    if widget and key in report_data:
                        payment_data = report_data[key]
                        if isinstance(payment_data, list):
                            widget.set_data(payment_data)
                            
                elif field_type == 'image_list' or field_type == 'images':
                    widget = getattr(self, f"{key}_widget", None)
                    if widget and key in images_data:
                        # Convert base64 back to bytes
                        image_list = []
                        for img_dict in images_data[key]:
                            img_name = img_dict.get('name', 'image.jpg')
                            img_base64 = img_dict.get('data', '')
                            if img_base64:
                                try:
                                    img_bytes = base64.b64decode(img_base64)
                                    image_list.append((img_name, img_bytes))
                                except:
                                    pass
                        if image_list:
                            widget.set_images(image_list)
            
            # Load bank accounts
            if 'bank_info' in report_data and hasattr(self, 'bank_account_fields'):
                bank_accounts = report_data['bank_info']
                if isinstance(bank_accounts, list):
                    # Clear existing
                    while len(self.bank_account_fields) > 0:
                        container, _ = self.bank_account_fields[-1]
                        self._remove_bank_account_field(container)
                    
                    # Add bank accounts
                    for account_data in bank_accounts:
                        self._add_bank_account_field(self.bank_accounts_layout)
                        if self.bank_account_fields:
                            _, field = self.bank_account_fields[-1]
                            field.setPlainText(str(account_data))
            
            # Report number, format, JSON path, and ODT path are already set above
            # No need to set them again here
            
            QMessageBox.information(
                self,
                "Report Loaded",
                f"Report data has been loaded (Report #{self.report_number}). You can now modify and save it again."
            )
            
            # Switch to first tab
            self.tab_widget.setCurrentIndex(0)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Loading Report",
                f"Failed to load report data:\n{str(e)}"
            )