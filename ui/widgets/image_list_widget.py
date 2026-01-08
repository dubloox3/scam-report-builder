import os
from typing import List, Tuple, Optional
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QFileDialog, QLabel, QScrollArea, QFrame, QMessageBox,
                             QListWidget, QListWidgetItem, QAbstractItemView, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QSize, QStandardPaths
from PySide6.QtGui import QFont
from .image_crop_dialog import ImageCropDialog


class ImageListWidget(QWidget):
    """Widget for managing a list of images with cropping capability."""
    
    images_changed = Signal()
    image_added = Signal(str, bytes)
    
    def __init__(self, label: str, button_text: str = "+ Add", parent=None):
        super().__init__(parent)
        self.label = label
        self.images: List[Tuple[str, bytes]] = []
        self.init_ui(label, button_text)
        
    def init_ui(self, label: str, button_text: str):
        """Initialize the user interface."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(8)
        
        # Header
        header = QHBoxLayout()
        header_label = QLabel(label)
        header_label.setStyleSheet("font-weight: bold; color: #333;")
        header.addWidget(header_label)
        header.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton(button_text)
        self.add_button.clicked.connect(self.add_image)
        self.add_button.setMinimumHeight(35)
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        self.remove_all_button = QPushButton("Remove All")
        self.remove_all_button.clicked.connect(self.remove_all_images)
        self.remove_all_button.setMinimumHeight(35)
        self.remove_all_button.setEnabled(False)
        self.remove_all_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_all_button)
        button_layout.addStretch()
        
        # List widget for file names - wrapped in scroll area for proper scrolling
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setMinimumHeight(150)
        
        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(1)
        
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QListWidget::item {
                border-bottom: 1px solid #f0f0f0;
                background-color: white;
            }
            QListWidget::item:alternate {
                background-color: #f9f9f9;
            }
        """)
        self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.list_layout.addWidget(self.list_widget)
        self.scroll_area.setWidget(self.list_container)
        
        # Status
        self.status_label = QLabel("No images added")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #666; font-style: italic; padding: 4px;")
        
        main_layout.addLayout(header)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.scroll_area)
        main_layout.addWidget(self.status_label)
        
        self.setLayout(main_layout)
    
    def add_image(self):
        """Open file dialog to select and add an image."""
        image_formats = " ".join(["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.gif", "*.tiff", "*.webp"])
        file_filter = f"Images ({image_formats})"
        
        # Get initial directory - use QStandardPaths for Pictures or Home location
        pictures_location = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.PicturesLocation)
        home_location = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.HomeLocation)
        
        # Prefer Pictures location, fall back to Home if Pictures doesn't exist
        initial_dir = pictures_location if pictures_location and os.path.exists(pictures_location) else home_location
        
        # Alternative: Use ConfigManager if available and preferred
        # try:
        #     from core.config_manager import ConfigManager
        #     config = ConfigManager()
        #     initial_dir = config.get_initial_folder_for_images() or initial_dir
        # except ImportError:
        #     pass
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            initial_dir,  # Use the determined initial directory
            file_filter
        )
        
        if file_path:
            # DO NOT call any update_report_folder_from_dialog() method here
            # Image selection is temporary and should not affect report save location
            
            crop_dialog = ImageCropDialog(file_path, self)
            if crop_dialog.exec():
                cropped_image_bytes = crop_dialog.get_cropped_image_data()
                if cropped_image_bytes:
                    filename = os.path.basename(file_path)
                    self.images.append((filename, cropped_image_bytes))
                    self.update_list()
                    self.images_changed.emit()
                    self.image_added.emit(self.label, cropped_image_bytes)
    
    def remove_image(self, index: int):
        """Remove an image at the specified index."""
        if 0 <= index < len(self.images):
            reply = QMessageBox.question(
                self,
                "Remove Image",
                f"Remove image '{self.images[index][0]}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.images.pop(index)
                self.update_list()
                self.images_changed.emit()
    
    def remove_all_images(self):
        """Remove all images."""
        if not self.images:
            return
            
        reply = QMessageBox.question(
            self,
            "Remove All Images",
            f"Remove all {len(self.images)} images?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.images.clear()
            self.update_list()
            self.images_changed.emit()
    
    def update_list(self):
        """Update the file list display."""
        self.list_widget.clear()
        
        for idx, (filename, _) in enumerate(self.images):
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, idx)
            
            # Create a custom widget for the item
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(12, 6, 12, 6)
            item_layout.setSpacing(12)
            
            # File name label
            file_label = QLabel(filename)
            file_label.setStyleSheet("""
                QLabel {
                    color: #333333;
                    font-size: 13px;
                    background: transparent;
                }
            """)
            file_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            file_label.setWordWrap(True)
            item_layout.addWidget(file_label)
            
            # Remove button - small red "X" matching text height
            remove_btn = QPushButton("✕")
            remove_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ff4444;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    font-size: 12px;
                    font-weight: bold;
                    min-width: 24px;
                    max-width: 24px;
                    min-height: 24px;
                    max-height: 24px;
                }
                QPushButton:hover {
                    background-color: #ff0000;
                }
            """)
            remove_btn.setFixedSize(24, 24)  # Fixed small size matching text height
            remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            remove_btn.clicked.connect(lambda checked, idx=idx: self.remove_image(idx))
            
            item_layout.addWidget(remove_btn, 0, Qt.AlignmentFlag.AlignRight)
            
            # Calculate appropriate item height based on content
            font_metrics = file_label.fontMetrics()
            text_height = font_metrics.height() + 12  # Add padding
            item_height = max(text_height, 32)  # Minimum height of 32px
            
            item.setSizeHint(QSize(0, item_height))
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, item_widget)
        
        # Update status and button state
        count = len(self.images)
        if count == 0:
            self.status_label.setText("No images added")
            self.remove_all_button.setEnabled(False)
        elif count == 1:
            self.status_label.setText("1 image added")
            self.remove_all_button.setEnabled(True)
        else:
            self.status_label.setText(f"{count} images added")
            self.remove_all_button.setEnabled(True)
            
        # Ensure scroll area shows all items
        self.list_widget.updateGeometry()
    
    def get_images(self) -> List[Tuple[str, bytes]]:
        """Get the list of images."""
        return self.images.copy()
    
    def clear_images(self):
        """Clear all images."""
        self.images.clear()
        self.update_list()
        self.images_changed.emit()
    
    def set_images(self, images: List[Tuple[str, bytes]]):
        """Set the images list."""
        self.images = images.copy()
        self.update_list()
        self.images_changed.emit()