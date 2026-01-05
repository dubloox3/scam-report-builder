# ui/widgets/image_crop_dialog.py
import io
from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QSlider, QComboBox, QSizePolicy, QDialogButtonBox,
    QWidget, QMessageBox, QTextEdit
)
from PySide6.QtCore import Qt, QRect, QPoint, QTimer, QSize, Signal
from PySide6.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QFont
from PIL import Image, ImageOps


class CropOverlay(QLabel):
    """Interactive crop rectangle overlay with resize handles"""
    
    crop_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.crop_rect = QRect()
        self.start_pos = QPoint()
        self.dragging = False
        self.creating = False
        self.resizing = False
        self.resize_edge = None
        self.handle_size = 10
        self.min_crop_size = 20
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        
    def reset(self):
        """Reset crop selection"""
        self.crop_rect = QRect()
        self.update()
        self.crop_changed.emit()
    
    def get_handle_at_position(self, pos: QPoint) -> Optional[str]:
        """Get resize handle at mouse position"""
        if not self.crop_rect.isValid():
            return None
        
        rect = self.crop_rect
        margin = 5
        
        # Check edges
        if abs(pos.x() - rect.left()) < margin and rect.top() <= pos.y() <= rect.bottom():
            return 'left'
        elif abs(pos.x() - rect.right()) < margin and rect.top() <= pos.y() <= rect.bottom():
            return 'right'
        elif abs(pos.y() - rect.top()) < margin and rect.left() <= pos.x() <= rect.right():
            return 'top'
        elif abs(pos.y() - rect.bottom()) < margin and rect.left() <= pos.x() <= rect.right():
            return 'bottom'
        
        # Check corners
        if abs(pos.x() - rect.left()) < margin and abs(pos.y() - rect.top()) < margin:
            return 'top-left'
        elif abs(pos.x() - rect.right()) < margin and abs(pos.y() - rect.top()) < margin:
            return 'top-right'
        elif abs(pos.x() - rect.left()) < margin and abs(pos.y() - rect.bottom()) < margin:
            return 'bottom-left'
        elif abs(pos.x() - rect.right()) < margin and abs(pos.y() - rect.bottom()) < margin:
            return 'bottom-right'
        
        return None
    
    def get_cursor_for_edge(self, edge: Optional[str]) -> Qt.CursorShape:
        """Get cursor shape for resize edge"""
        if not edge:
            return Qt.ArrowCursor
        
        cursors = {
            'top-left': Qt.SizeFDiagCursor, 'bottom-right': Qt.SizeFDiagCursor,
            'top-right': Qt.SizeBDiagCursor, 'bottom-left': Qt.SizeBDiagCursor,
            'top': Qt.SizeVerCursor, 'bottom': Qt.SizeVerCursor,
            'left': Qt.SizeHorCursor, 'right': Qt.SizeHorCursor
        }
        return cursors.get(edge, Qt.ArrowCursor)
    
    def mousePressEvent(self, event):
        """Handle mouse press for crop interaction"""
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            self.start_pos = pos
            
            edge = self.get_handle_at_position(pos)
            if edge:
                self.resizing = True
                self.resize_edge = edge
            elif self.crop_rect.isValid() and self.crop_rect.contains(pos):
                self.dragging = True
                self.drag_offset = pos - self.crop_rect.topLeft()
            else:
                self.creating = True
                self.crop_rect = QRect(pos, pos)
            
            self.update()
            self.crop_changed.emit()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for crop interaction"""
        pos = event.pos()
        
        # Update cursor
        if not (self.dragging or self.resizing or self.creating):
            edge = self.get_handle_at_position(pos)
            self.setCursor(self.get_cursor_for_edge(edge))
        
        # Update crop rectangle
        if self.creating:
            self.crop_rect = QRect(self.start_pos, pos).normalized()
        elif self.dragging:
            new_top_left = pos - self.drag_offset
            bounds = self.rect()
            new_top_left.setX(max(0, min(new_top_left.x(), bounds.width() - self.crop_rect.width())))
            new_top_left.setY(max(0, min(new_top_left.y(), bounds.height() - self.crop_rect.height())))
            self.crop_rect.moveTopLeft(new_top_left)
        elif self.resizing and self.resize_edge:
            self._resize_crop_rect(pos)
        
        if self.dragging or self.resizing or self.creating:
            self.update()
            self.crop_changed.emit()
    
    def _resize_crop_rect(self, pos: QPoint):
        """Resize crop rectangle based on dragged edge"""
        if not self.resize_edge:
            return
        
        rect = self.crop_rect
        bounds = self.rect()
        
        # Update rectangle based on edge
        edge_actions = {
            'top-left': lambda: rect.setTopLeft(pos),
            'top-right': lambda: rect.setTopRight(pos),
            'bottom-left': lambda: rect.setBottomLeft(pos),
            'bottom-right': lambda: rect.setBottomRight(pos),
            'top': lambda: rect.setTop(pos.y()),
            'bottom': lambda: rect.setBottom(pos.y()),
            'left': lambda: rect.setLeft(pos.x()),
            'right': lambda: rect.setRight(pos.x())
        }
        
        if action := edge_actions.get(self.resize_edge):
            action()
        
        rect = rect.normalized()
        
        # Enforce minimum size
        if rect.width() < self.min_crop_size:
            if 'left' in self.resize_edge:
                rect.setLeft(rect.right() - self.min_crop_size)
            elif 'right' in self.resize_edge:
                rect.setRight(rect.left() + self.min_crop_size)
        
        if rect.height() < self.min_crop_size:
            if 'top' in self.resize_edge:
                rect.setTop(rect.bottom() - self.min_crop_size)
            elif 'bottom' in self.resize_edge:
                rect.setBottom(rect.top() + self.min_crop_size)
        
        self.crop_rect = rect.intersected(bounds)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.LeftButton:
            if self.creating:
                self.creating = False
                self.crop_rect = self.crop_rect.normalized()
                if self.crop_rect.width() < self.min_crop_size or self.crop_rect.height() < self.min_crop_size:
                    self.crop_rect = QRect()
            
            self.dragging = False
            self.resizing = False
            self.resize_edge = None
            self.update()
            self.crop_changed.emit()
    
    def paintEvent(self, event):
        """Draw crop overlay"""
        super().paintEvent(event)
        
        if not self.crop_rect.isValid():
            return
            
        painter = QPainter(self)
        bounds = self.rect()
        
        # Draw overlay outside crop area
        painter.setBrush(QColor(0, 0, 0, 100))
        painter.setPen(Qt.NoPen)
        
        top = self.crop_rect.top()
        bottom = self.crop_rect.bottom()
        left = self.crop_rect.left()
        right = self.crop_rect.right()
        height = self.crop_rect.height()
        
        painter.drawRect(0, 0, bounds.width(), top)  # Top
        painter.drawRect(0, bottom, bounds.width(), bounds.height() - bottom)  # Bottom
        painter.drawRect(0, top, left, height)  # Left
        painter.drawRect(right, top, bounds.width() - right, height)  # Right
        
        # Draw crop rectangle with red border
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(255, 0, 0), 2))
        painter.drawRect(self.crop_rect)
        
        # Draw resize handles
        painter.setBrush(QColor(255, 255, 255, 220))
        painter.setPen(QPen(QColor(0, 0, 0, 200), 1))
        
        rect = self.crop_rect
        half = self.handle_size // 2
        
        handles = [
            QRect(rect.left() - half, rect.top() - half, self.handle_size, self.handle_size),
            QRect(rect.right() - half, rect.top() - half, self.handle_size, self.handle_size),
            QRect(rect.left() - half, rect.bottom() - half, self.handle_size, self.handle_size),
            QRect(rect.right() - half, rect.bottom() - half, self.handle_size, self.handle_size),
        ]
        
        for handle in handles:
            painter.drawRect(handle)


class ImageCropDialog(QDialog):
    """Dialog for cropping images before insertion into documents"""
    
    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.cropped_image: Optional[bytes] = None
        self.original_image = None
        self.current_image = None
        self.overlay = None
        
        self.setup_ui()
        self.load_image()
    
    def setup_ui(self):
        """Setup dialog UI"""
        self.setWindowTitle("Crop Image")
        self.setMinimumSize(1100, 700)
        
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QTextEdit()
        instructions.setMaximumHeight(60)
        instructions.setReadOnly(True)
        instructions.setText(
            "Click and drag to create crop area. Drag from center to move. "
            "Drag edges/corners to resize. Use rotation buttons if needed."
        )
        instructions.setStyleSheet("""
            QTextEdit {
                background-color: #f0f8ff;
                border: 1px solid #ccc;
                font-size: 10pt;
                padding: 5px;
                color: #333;
            }
        """)
        layout.addWidget(instructions)
        
        # Main content
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        
        # Left: Image area
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addLayout(self._create_toolbar())
        left_layout.addWidget(self._create_image_display())
        main_layout.addWidget(left_widget, 65)
        
        # Right: Preview and settings
        main_layout.addWidget(self._create_sidebar(), 35)
        layout.addWidget(main_widget, 1)
        
        # Dialog buttons
        layout.addWidget(self._create_button_box())
        
        # Connect signals
        self.quality_slider.valueChanged.connect(self._update_quality_label)
        self.quality_slider.valueChanged.connect(self.update_preview)
        self.size_combo.currentTextChanged.connect(self.update_preview)
    
    def _create_toolbar(self):
        """Create toolbar with crop controls"""
        toolbar = QHBoxLayout()
        
        # Rotation
        rotation_widget = QWidget()
        rotation_layout = QHBoxLayout(rotation_widget)
        rotation_layout.setContentsMargins(0, 0, 0, 0)
        
        rotation_label = QLabel("Rotate:")
        rotation_label.setStyleSheet("font-weight: bold;")
        rotation_layout.addWidget(rotation_label)
        
        self.rotate_left_btn = QPushButton("↺ 90° Left")
        self.rotate_left_btn.clicked.connect(lambda: self._rotate_image(90))
        rotation_layout.addWidget(self.rotate_left_btn)
        
        self.rotate_right_btn = QPushButton("↻ 90° Right")
        self.rotate_right_btn.clicked.connect(lambda: self._rotate_image(-90))
        rotation_layout.addWidget(self.rotate_right_btn)
        
        toolbar.addWidget(rotation_widget)
        toolbar.addStretch()
        
        # Crop actions
        action_widget = QWidget()
        action_layout = QHBoxLayout(action_widget)
        action_layout.setContentsMargins(0, 0, 0, 0)
        
        self.reset_btn = QPushButton("Reset Crop")
        self.reset_btn.clicked.connect(self.reset_selection)
        action_layout.addWidget(self.reset_btn)
        
        self.full_image_btn = QPushButton("Full Image")
        self.full_image_btn.clicked.connect(self.select_full_image)
        action_layout.addWidget(self.full_image_btn)
        
        toolbar.addWidget(action_widget)
        
        return toolbar
    
    def _create_image_display(self):
        """Create image display area"""
        container = QWidget()
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_label.setStyleSheet("background-color: white; border: 2px solid #888;")
        
        layout.addWidget(self.image_label)
        return container
    
    def _create_sidebar(self):
        """Create sidebar with preview and settings"""
        sidebar = QWidget()
        layout = QVBoxLayout(sidebar)
        
        # Preview
        preview_group = QGroupBox("Preview")
        preview_group.setMinimumWidth(300)
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(280, 200)
        self.preview_label.setStyleSheet("border: 2px solid #aaa; background-color: #f8f8f8;")
        preview_layout.addWidget(self.preview_label)
        
        self.preview_info = QLabel("Preview will appear here")
        self.preview_info.setAlignment(Qt.AlignCenter)
        self.preview_info.setStyleSheet("font-weight: bold; color: #333; padding: 5px;")
        preview_layout.addWidget(self.preview_info)
        
        layout.addWidget(preview_group)
        
        # Settings
        layout.addWidget(self._create_settings_group())
        
        return sidebar
    
    def _create_settings_group(self):
        """Create export settings group"""
        group = QGroupBox("Export Settings")
        layout = QVBoxLayout(group)
        
        # Quality
        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setRange(30, 100)
        self.quality_slider.setValue(80)
        self.quality_slider.setTickInterval(10)
        
        self.quality_label = QLabel("80%")
        self.quality_label.setAlignment(Qt.AlignCenter)
        self.quality_label.setStyleSheet("font-weight: bold;")
        
        quality_layout = QVBoxLayout()
        quality_layout.addWidget(QLabel("JPEG Quality:"))
        quality_layout.addWidget(self.quality_slider)
        
        quality_value = QHBoxLayout()
        quality_value.addWidget(QLabel("Low"))
        quality_value.addWidget(self.quality_label)
        quality_value.addWidget(QLabel("High"))
        quality_layout.addLayout(quality_value)
        
        layout.addLayout(quality_layout)
        
        # Size
        self.size_combo = QComboBox()
        self.size_combo.addItems(["600px", "800px", "1000px", "1200px", "Original"])
        self.size_combo.setCurrentIndex(1)
        
        size_layout = QVBoxLayout()
        size_layout.addWidget(QLabel("Maximum Size:"))
        size_layout.addWidget(self.size_combo)
        layout.addLayout(size_layout)
        
        # Image info
        self.image_info = QLabel("Loading...")
        self.image_info.setStyleSheet("color: #444; font-size: 9pt; margin-top: 10px;")
        layout.addWidget(self.image_info)
        
        layout.addStretch()
        
        return group
    
    def _create_button_box(self):
        """Create dialog button box"""
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._apply_crop)
        button_box.rejected.connect(self.reject)
        
        ok_button = button_box.button(QDialogButtonBox.Ok)
        ok_button.setText("Save Cropped Image")
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        return button_box
    
    def load_image(self):
        """Load and prepare image"""
        try:
            self.original_image = Image.open(self.image_path)
            self.original_image = ImageOps.exif_transpose(self.original_image)
            self.current_image = self.original_image.copy()
            self._display_image()
            self.select_full_image()
            self._update_image_info()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")
            self.reject()
    
    def _update_image_info(self):
        """Update image info display"""
        if self.current_image:
            self.image_info.setText(
                f"Size: {self.current_image.width} × {self.current_image.height}\n"
                f"Mode: {self.current_image.mode}"
            )
    
    def select_full_image(self):
        """Select entire image as crop area"""
        if self.overlay:
            self.overlay.crop_rect = QRect(0, 0, self.overlay.width(), self.overlay.height())
            self.overlay.update()
            self.update_preview()
    
    def _rotate_image(self, degrees):
        """Rotate image by specified degrees"""
        self.current_image = self.current_image.rotate(degrees, expand=True)
        self._display_image()
        self.select_full_image()
        self._update_image_info()
    
    def _display_image(self):
        """Display image in label"""
        if not self.current_image:
            return
            
        try:
            # Convert PIL to QPixmap
            buffer = io.BytesIO()
            self.current_image.save(buffer, format='PNG')
            buffer.seek(0)
            
            qimage = QImage()
            if not qimage.loadFromData(buffer.getvalue()):
                return
                
            pixmap = QPixmap.fromImage(qimage)
            if pixmap.isNull():
                return
            
            # Scale to fit label
            label_size = self.image_label.size()
            if label_size.width() <= 0 or label_size.height() <= 0:
                label_size = QSize(500, 500)
            
            scaled = pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled)
            
            # Create/update overlay
            if not self.overlay:
                self.overlay = CropOverlay(self.image_label)
                self.overlay.crop_changed.connect(self.update_preview)
                self.overlay.setStyleSheet("background-color: transparent;")
            
            # Position overlay over scaled image
            pixmap_size = scaled.size()
            label_rect = self.image_label.rect()
            x_offset = (label_rect.width() - pixmap_size.width()) // 2
            y_offset = (label_rect.height() - pixmap_size.height()) // 2
            
            self.overlay.setGeometry(x_offset, y_offset, pixmap_size.width(), pixmap_size.height())
            self.overlay.raise_()
            
        except Exception:
            pass  # Silently handle display errors
    
    def resizeEvent(self, event):
        """Handle window resize"""
        super().resizeEvent(event)
        QTimer.singleShot(50, self._display_image)
        QTimer.singleShot(100, self.update_preview)
    
    def showEvent(self, event):
        """Handle dialog show"""
        super().showEvent(event)
        QTimer.singleShot(100, self._display_image)
        QTimer.singleShot(150, self.update_preview)
    
    def reset_selection(self):
        """Reset crop selection"""
        if self.overlay:
            self.overlay.reset()
    
    def _update_quality_label(self, value):
        """Update quality slider label"""
        self.quality_label.setText(f"{value}%")
    
    def _get_cropped_image(self) -> Optional[Image.Image]:
        """Get cropped PIL image based on current selection"""
        if not self.overlay or not self.overlay.crop_rect.isValid():
            return self.current_image
        
        try:
            crop_rect = self.overlay.crop_rect
            pixmap = self.image_label.pixmap()
            
            if not pixmap or pixmap.isNull():
                return self.current_image
            
            # Calculate scale from display to actual image
            scale_x = self.current_image.width / pixmap.width()
            scale_y = self.current_image.height / pixmap.height()
            
            # Convert display coordinates to image coordinates
            x = int(crop_rect.x() * scale_x)
            y = int(crop_rect.y() * scale_y)
            width = int(crop_rect.width() * scale_x)
            height = int(crop_rect.height() * scale_y)
            
            # Clamp to image bounds
            x = max(0, min(x, self.current_image.width - 1))
            y = max(0, min(y, self.current_image.height - 1))
            width = min(width, self.current_image.width - x)
            height = min(height, self.current_image.height - y)
            
            if width > 0 and height > 0:
                right = min(x + width, self.current_image.width)
                bottom = min(y + height, self.current_image.height)
                return self.current_image.crop((x, y, right, bottom))
            
        except Exception:
            pass  # Return full image on error
        
        return self.current_image
    
    def update_preview(self):
        """Update preview display"""
        try:
            cropped = self._get_cropped_image()
            if not cropped:
                return
            
            # Create preview as JPEG
            buffer = io.BytesIO()
            quality = self.quality_slider.value()
            
            if cropped.mode == 'RGBA':
                rgb_image = Image.new('RGB', cropped.size, (255, 255, 255))
                rgb_image.paste(cropped, mask=cropped.split()[3] if len(cropped.split()) > 3 else None)
                rgb_image.save(buffer, format='JPEG', quality=quality)
            else:
                cropped.save(buffer, format='JPEG', quality=quality)
            
            buffer.seek(0)
            
            # Load and display preview
            qimage = QImage()
            if qimage.loadFromData(buffer.getvalue()):
                preview = QPixmap.fromImage(qimage)
                if not preview.isNull():
                    scaled = preview.scaled(
                        self.preview_label.size(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    self.preview_label.setPixmap(scaled)
            
            # Update info
            self.preview_info.setText(f"{cropped.width} × {cropped.height}")
            
        except Exception:
            pass  # Silently handle preview errors
    
    def _apply_crop(self):
        """Finalize crop and prepare for export"""
        try:
            cropped = self._get_cropped_image()
            if not cropped:
                raise Exception("No image to crop")
            
            # Apply resize if needed
            max_size = self.size_combo.currentText()
            if max_size != "Original":
                max_dim = int(max_size.replace("px", ""))
                if cropped.width > max_dim or cropped.height > max_dim:
                    ratio = min(max_dim / cropped.width, max_dim / cropped.height)
                    new_size = (int(cropped.width * ratio), int(cropped.height * ratio))
                    cropped = cropped.resize(new_size, Image.Resampling.LANCZOS)
            
            # Convert to JPEG bytes
            buffer = io.BytesIO()
            quality = self.quality_slider.value()
            
            if cropped.mode == 'RGBA':
                rgb_image = Image.new('RGB', cropped.size, (255, 255, 255))
                rgb_image.paste(cropped, mask=cropped.split()[3] if len(cropped.split()) > 3 else None)
                rgb_image.save(buffer, format='JPEG', quality=quality, optimize=True)
            else:
                cropped.save(buffer, format='JPEG', quality=quality, optimize=True)
            
            self.cropped_image = buffer.getvalue()
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process image: {str(e)}")
            self.reject()
    
    def get_cropped_image_data(self) -> Optional[bytes]:
        """Get cropped image as JPEG bytes for document insertion"""
        return self.cropped_image