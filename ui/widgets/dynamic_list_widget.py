"""
Dynamic List Widget for Scam Report Builder
Widget for managing lists of items (aliases, emails, etc.)
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PySide6.QtCore import Qt


class DynamicListWidget(QWidget):
    """Widget for dynamically adding/removing list items"""
    
    def __init__(self, label: str = "", field_type: str = "list", parent=None, default_values=None, button_text: str = "+ Add", required: bool = False):
        super().__init__(parent)
        self.required = required
        self.field_type = field_type
        self.widgets = []
        self.default_values = default_values if default_values is not None else []
        self.setup_ui(label, button_text)
    
    def setup_ui(self, label: str, button_text: str):
        """Setup the widget UI"""
        layout = QVBoxLayout(self)
        
        # Header with label and add button
        header = QHBoxLayout()
        header.addWidget(QLabel(label))
        
        if self.required:
            req_label = QLabel("(required)")
            req_label.setStyleSheet("color: red; font-weight: bold;")
            header.addWidget(req_label)
        
        header.addStretch()
        
        self.add_button = QPushButton(button_text)
        self.add_button.clicked.connect(self._add_entry)
        header.addWidget(self.add_button)
        
        layout.addLayout(header)
        
        # Add initial entries from default_values
        if self.default_values:
            for value in self.default_values:
                self._add_entry_with_value(value)
        # Add initial empty entry if required but no default values
        elif self.required:
            self._add_entry()
    
    def _add_entry(self, value: str = ""):
        """Add a new entry widget"""
        entry_layout = QHBoxLayout()
        
        # Text input
        entry_widget = QLineEdit()
        entry_widget.setPlaceholderText("Enter value...")
        
        # Set value if provided
        if value:
            entry_widget.setText(value)
        
        # Remove button
        remove_btn = QPushButton("✕")
        remove_btn.setFixedWidth(30)
        remove_btn.clicked.connect(lambda: self._remove_entry(entry_widget, entry_layout))
        
        # Add to layout
        entry_layout.addWidget(entry_widget)
        entry_layout.addWidget(remove_btn)
        
        self.widgets.append(entry_widget)
        self.layout().addLayout(entry_layout)
    
    def _add_entry_with_value(self, value: str):
        """Helper method to add entry with a specific value"""
        self._add_entry(value)
    
    def _remove_entry(self, widget, layout):
        """Remove an entry widget"""
        if len(self.widgets) == 1 and self.required:
            QMessageBox.warning(self, "Cannot Remove", "At least one entry is required.")
            return
        
        # Remove widgets from layout
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Remove from list
        self.widgets.remove(widget)
        self.layout().removeItem(layout)
    
    def get_values(self) -> list:
        """Get all entered values"""
        values = [w.text().strip() for w in self.widgets]
        return [v for v in values if v]  # Filter out empty values
    
    def is_valid(self) -> bool:
        """Check if widget has valid data"""
        if not self.required:
            return True
        return any(w.text().strip() for w in self.widgets)
    
    def clear_all(self):
        """Clear all entries"""
        # Remove all entries except the first one if required
        while len(self.widgets) > (1 if self.required else 0):
            # Find the last widget and its layout
            for i in reversed(range(self.layout().count())):
                item = self.layout().itemAt(i)
                if item and hasattr(item, 'count') and item.count() > 0:
                    # This is a layout containing widgets
                    widget_item = item.itemAt(0)
                    if widget_item and widget_item.widget() in self.widgets:
                        self._remove_entry(widget_item.widget(), item)
                        break
        
        # Clear the remaining entry if it exists
        if self.widgets:
            self.widgets[0].clear()