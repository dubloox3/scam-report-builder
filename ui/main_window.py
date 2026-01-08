"""
Main Window for Scam Report Builder
Primary application interface with tab-based form.
"""

import re
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QDateEdit, QScrollArea, QGroupBox,
    QMessageBox, QFileDialog, QTabWidget, QDialog, QListWidget,
    QListWidgetItem, QDialogButtonBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont

from core.config_manager import ConfigManager
from core.template_manager import TemplateManager
from ui.widgets.dynamic_list_widget import DynamicListWidget
from ui.widgets.image_list_widget import ImageListWidget
from ui.widgets.other_payment_widget import OtherPaymentWidget
from ui.dialogs.report_number_dialog import ReportNumberDialog


class TemplateSelectionDialog(QDialog):
    """Dialog for selecting a report template"""
    
    def __init__(self):
        super().__init__()
        self.selected_template = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the template selection dialog UI"""
        self.setWindowTitle("Select Report Template")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        title = QLabel("Select a Report Template")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        instruction = QLabel("After selecting a template, you'll be able to fill in the details and generate a scam report.")
        instruction.setWordWrap(True)
        instruction.setAlignment(Qt.AlignCenter)
        instruction.setStyleSheet("color: #666666; margin: 10px 0;")
        layout.addWidget(instruction)
        
        self.template_list = QListWidget()
        self.template_list.itemClicked.connect(self._on_template_selected)
        layout.addWidget(self.template_list)
        
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("""
            QLabel {
                color: #333333;
                background-color: #f5f5f5;
                border: 1px solid #dddddd;
                border-radius: 4px;
                padding: 12px;
                margin: 10px 0;
            }
        """)
        layout.addWidget(self.description_label)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self.ok_button = button_box.button(QDialogButtonBox.Ok)
        self.ok_button.setEnabled(False)
        self.ok_button.setText("Create Scam Report")
        layout.addWidget(button_box)
        
        self._load_templates()
    
    def _load_templates(self):
        """Load available templates into the list"""
        templates = TemplateManager.get_all_templates()
        
        for template_key, template_data in templates.items():
            display_name = template_data['name']
            # Update display name for Advance-Fee Scam template
            if display_name == "Advance-Fee Scam (419)":
                display_name = "Advance-Fee Scam"
            
            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, template_key)
            self.template_list.addItem(item)
    
    def _on_template_selected(self, item):
        """Handle template selection"""
        template_key = item.data(Qt.UserRole)
        template = TemplateManager.get_template(template_key)
        
        if template:
            self.selected_template = template_key
            self.description_label.setText(template['description'])
            self.ok_button.setEnabled(True)
    
    def get_selected_template(self):
        """Get the selected template key"""
        return self.selected_template


class ScamReportBuilder(QMainWindow):
    """Main application window for building scam reports"""
    
    def __init__(self, template_key: str):
        super().__init__()
        self.template_key = template_key
        self.template = TemplateManager.get_template(template_key)
        self.report_number = None
        self.report_format = None
        
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
        main_layout.addWidget(self.export_btn)
    
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
                label = "Scammers main alias"
                button_text = "+Add other scammer aliases"
                # Add tooltip and update placeholder for first entry
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
            
            # Add tooltip to the alias widget
            if key == 'alias':
                widget.setToolTip("This name will be used for the report filename")
            
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
        fields = ['type', 'summary', 'alias', 'emails', 'websites', 'ips', 'locations', 'started']
        self._build_tab(self.main_info_tab, fields)
    
    def _build_payment_tab(self):
        """Build the Payment Information tab"""
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
        # First, let's see what fields the template actually has
        template_fields = self.template['fields']
        print("\n=== DEBUG: Checking template fields for Evidence tab ===")
        print(f"Total fields in template: {list(template_fields.keys())}")
        
        # Look for fields that might belong in Evidence tab
        evidence_keywords = ['scammer', 'passport', 'photo', 'victim', 'other', 'evidence']
        possible_evidence_fields = []
        
        for field_name, field_def in template_fields.items():
            field_lower = field_name.lower()
            field_type = field_def.get('type', 'unknown')
            
            # Check if field name contains any evidence-related keywords
            # OR if it's an image type field (images or image_list)
            if (any(keyword in field_lower for keyword in evidence_keywords) or
                field_type in ['images', 'image_list']):
                possible_evidence_fields.append(field_name)
                print(f"  Found evidence field: '{field_name}' (type: {field_type})")
        
        print(f"\nPossible evidence fields: {possible_evidence_fields}")
        
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
                field_type = template_fields[field].get('type', 'unknown')
                print(f"✓ Including '{field}' (type: {field_type})")
        
        # If 'others' is not in the standard list, look for any field with 'other' in the name
        if 'others' not in fields:
            for field_name, field_def in template_fields.items():
                field_lower = field_name.lower()
                field_type = field_def.get('type', 'unknown')
                if ('other' in field_lower and 
                    field_name not in fields and
                    field_type in ['images', 'image_list']):
                    fields.append(field_name)
                    print(f"✓ Including '{field_name}' as 'others' equivalent (type: {field_type})")
                    break
        
        print(f"\nFinal Evidence tab fields: {fields}")
        print("=== END DEBUG ===\n")
        
        self._build_tab(self.evidence_tab, fields)
    
    def _build_remarks_tab(self):
        """Build the Remarks tab"""
        fields = ['remarks']
        self._build_tab(self.remarks_tab, fields)
    
    def _get_report_number(self) -> bool:
        """Get report number from user"""
        config_manager = ConfigManager()
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
    
    def _export_report(self):
        """Export report to ODT file"""
        if not self._validate_form():
            return
        
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
        
        # Get scammer name for filename
        scammer_name = ""
        if report_data.get('alias'):
            scammer_name = report_data['alias'][0]
        
        # Generate filename using the new config_manager method
        config_manager = ConfigManager()
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
        
        # Get initial folder for file dialog using the new method
        initial_folder = config_manager.get_initial_folder_for_dialog()
        
        # IMPORTANT: Ensure initial_folder is actually a directory, not a file
        # If it contains a file extension, extract the directory part
        if initial_folder:
            initial_folder_path = Path(initial_folder)
            # Check if it's a file (has extension or doesn't exist as directory)
            if initial_folder_path.suffix or not initial_folder_path.is_dir():
                # It's likely a file path, get the parent directory
                initial_folder = str(initial_folder_path.parent)
        
        # IMPORTANT: Save and restore the current working directory
        # This prevents image selection dialogs from interfering with report save location
        current_dir = os.getcwd()
        
        try:
            # Change to the desired directory before showing dialog
            if initial_folder and Path(initial_folder).exists() and Path(initial_folder).is_dir():
                os.chdir(str(initial_folder))
            
            # Prepare the initial path for the dialog
            initial_path = str(Path(initial_folder) / filename) if initial_folder else filename
            
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
                # Update the last used folder in config using the new method
                config_manager.update_folder_from_dialog(file_path)
                
                # Update report number in config
                config_manager.update_report_number(self.report_number, self.report_format)
                
                # Generate the ODT file
                from core.odt_generator import ODTGenerator
                
                success = ODTGenerator.create_odt(
                    content=report_data,
                    output_path=file_path,
                    images=images
                )
                
                if success:
                    QMessageBox.information(
                        self, 
                        "Success", 
                        f"Report #{self.report_number} saved to:\n{file_path}"
                    )
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