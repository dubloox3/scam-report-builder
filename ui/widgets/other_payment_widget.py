"""
Other Payment Widget for Scam Report Builder
Widget for managing other payment methods
"""

from typing import List, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTextEdit, QGroupBox
)
from PySide6.QtGui import QFont


class OtherPaymentWidget(QWidget):
    """Widget for managing other payment methods"""
    
    PAYMENT_TYPES = [
        "MoneyGram / RIA / Western Union",
        "Crypto (Bitcoin, Ethereum, etc.)",
        "PayPal",
        "CashApp",
        "Foreign Bank Account",
        "Other"
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.payments = []
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("Other Payment Methods")
        header_font = QFont()
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        
        self.add_button = QPushButton("+ Add Payment Method")
        self.add_button.clicked.connect(self._add_payment)
        header_layout.addWidget(self.add_button)
        
        layout.addLayout(header_layout)
        layout.addSpacing(10)
        
        # Payments container
        self.payments_container = QWidget()
        self.payments_layout = QVBoxLayout(self.payments_container)
        self.payments_layout.setSpacing(10)
        self.payments_layout.setContentsMargins(5, 0, 5, 0)
        layout.addWidget(self.payments_container)
        layout.addStretch()
    
    def _add_payment(self):
        """Add a new payment method widget"""
        payment_widget = self._create_payment_widget()
        self.payments_layout.addWidget(payment_widget)
    
    def _create_payment_widget(self):
        """Create a payment method widget"""
        payment_widget = QGroupBox(f"Payment Method {len(self.payments) + 1}")
        payment_widget.setStyleSheet(self._get_groupbox_style())
        
        payment_layout = QVBoxLayout(payment_widget)
        
        # Payment type selection
        type_combo = QComboBox()
        type_combo.addItems(self.PAYMENT_TYPES)
        type_layout = self._create_type_layout(type_combo)
        payment_layout.addLayout(type_layout)
        
        # Payment details - Updated label
        payment_layout.addWidget(QLabel("Fee/Amount:"))
        details_text = self._create_details_text()
        payment_layout.addWidget(details_text)
        
        # Remove button
        remove_btn = self._create_remove_button(payment_widget, type_combo, details_text)
        payment_layout.addWidget(remove_btn)
        
        # Store reference
        self.payments.append((type_combo, details_text))
        
        return payment_widget
    
    def _create_type_layout(self, combo):
        """Create layout for payment type selection"""
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Type:"))
        layout.addWidget(combo, 1)
        layout.addStretch()
        return layout
    
    def _create_details_text(self):
        """Create payment details text edit - Updated placeholder"""
        details = QTextEdit()
        details.setMaximumHeight(100)
        details.setPlaceholderText(
            "Enter fee/amount details here...\n"
            "For Crypto: include wallet addresses, transaction IDs, amount\n"
            "For Money Transfer: include control numbers, sender/receiver info, fees\n"
            "For PayPal: include email addresses, transaction IDs, amount paid"
        )
        details.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        return details
    
    def _create_remove_button(self, widget, type_combo, details_text):
        """Create remove button for payment widget"""
        btn = QPushButton("Remove")
        btn.setStyleSheet("""
            QPushButton {
                background-color: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #f5c6cb;
            }
        """)
        btn.clicked.connect(lambda: self._remove_payment(widget, type_combo, details_text))
        return btn
    
    @staticmethod
    def _get_groupbox_style():
        """Get CSS style for group boxes"""
        return """
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """
    
    def _remove_payment(self, widget, type_combo, details_text):
        """Remove a payment method widget"""
        # Remove from list
        for i, (t, d) in enumerate(self.payments):
            if t is type_combo and d is details_text:
                self.payments.pop(i)
                break
        
        # Remove widget
        widget.deleteLater()
        self._update_widget_titles()
    
    def _update_widget_titles(self):
        """Update titles of all payment widgets"""
        widgets = self._get_payment_widgets()
        for i, widget in enumerate(widgets):
            widget.setTitle(f"Payment Method {i + 1}")
    
    def _get_payment_widgets(self):
        """Get all payment group box widgets"""
        widgets = []
        for i in range(self.payments_layout.count()):
            item = self.payments_layout.itemAt(i)
            if item and item.widget():
                widgets.append(item.widget())
        return widgets
    
    def get_data(self) -> List[Dict[str, Any]]:
        """Get all payment data as list of dictionaries"""
        data = []
        for type_combo, details_text in self.payments:
            details = details_text.toPlainText().strip()
            if details:  # Only include if there are details
                data.append({
                    "type": type_combo.currentText(),
                    "details": details
                })
        return data
    
    def clear(self):
        """Clear all payment methods"""
        # Remove all widgets
        while self.payments_layout.count():
            item = self.payments_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
        
        # Clear payments list
        self.payments.clear()
    
    def set_data(self, payments_data: List[Dict[str, Any]]):
        """Set payment data from list of dictionaries"""
        self.clear()
        
        for payment in payments_data:
            self._add_payment()
            
            if self.payments:
                type_combo, details_text = self.payments[-1]
                index = type_combo.findText(payment.get("type", ""))
                if index >= 0:
                    type_combo.setCurrentIndex(index)
                details_text.setPlainText(payment.get("details", ""))