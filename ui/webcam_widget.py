from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QImage, QPainter, QColor, QPen, QFont
from PyQt6.QtCore import Qt, QRect

class WebcamWidget(QWidget):
    """
    Displays the video feed using high-performance Zero-Copy rendering.
    Draws metadata (faces) using QPainter overlays rather than pixel modification.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = None
        self._current_frame_data = None # Keep reference to data to prevent segfault
        self.faces = [] # [{'name': str, 'location': (top, right, bottom, left)}]
        self.setMinimumSize(640, 480)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background-color: #000000; border: 2px solid #333;")

    def update_frame(self, frame):
        """
        Updates the internal image from a raw BGR OpenCV frame.
        No color conversion is performed here (Zero-Copy-ish).
        """
        if frame is None:
            return

        h, w, ch = frame.shape
        bytes_per_line = ch * w
        
        # Performance Optimization: Zero-Copy
        # Store the numpy array reference so it doesn't get garbage collected
        # while QImage is using it.
        self._current_frame_data = frame 
        
        # Create QImage pointing directly to the numpy array memory
        self.image = QImage(
            self._current_frame_data.data, 
            w, 
            h, 
            bytes_per_line, 
            QImage.Format.Format_BGR888
        )
        # Note: We do NOT call .copy() here anymore.
        
        self.update()

    def update_faces(self, faces):
        """
        Updates the list of faces to draw.
        """
        self.faces = faces
        # No need to call update() here usually, as update_frame comes right after. 
        # But if frame stops and faces change, we might want to.
        # For now, rely on update_frame to trigger repaint.

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False) # Keep video crisp
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
        
        # 1. Background
        painter.fillRect(self.rect(), QColor(0, 0, 0))
        
        widget_width = self.width()
        widget_height = self.height()
        
        scale_x = 1.0
        scale_y = 1.0
        offset_x = 0
        offset_y = 0
        
        # 2. Draw Video Frame
        if self.image and not self.image.isNull():
            img_width = self.image.width()
            img_height = self.image.height()
            
            # Aspect Ratio Calculation
            img_ratio = img_width / img_height
            widget_ratio = widget_width / widget_height
            
            if widget_ratio > img_ratio:
                # Widget is wider (fit height)
                draw_height = widget_height
                draw_width = int(draw_height * img_ratio)
                offset_x = (widget_width - draw_width) // 2
            else:
                # Widget is taller (fit width)
                draw_width = widget_width
                draw_height = int(draw_width / img_ratio)
                offset_y = (widget_height - draw_height) // 2
            
            target_rect = QRect(offset_x, offset_y, draw_width, draw_height)
            painter.drawImage(target_rect, self.image)
            
            # Calculate scaling factors for overlays
            scale_x = draw_width / img_width
            scale_y = draw_height / img_height
        else:
            painter.setPen(QColor(100, 100, 100))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Waiting for Camera Feed...")
            return

        # 3. Draw Face Overlays (Vector Graphics)
        # Enable Antialiasing for UI elements
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        font = painter.font()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        
        for face in self.faces:
            top, right, bottom, left = face['location']
            name = face['name']
            
            # Map coordinates to widget space
            x = int(left * scale_x) + offset_x
            y = int(top * scale_y) + offset_y
            w_box = int((right - left) * scale_x)
            h_box = int((bottom - top) * scale_y)
            
            # Color Scheme
            if name == "Unknown":
                color = QColor(255, 85, 85) # Red #ff5555
            else:
                color = QColor(0, 255, 153) # Green #00ff99
                
            pen = QPen(color)
            pen.setWidth(2)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            
            # Draw Box
            painter.drawRect(x, y, w_box, h_box)
            
            # Draw Name Label
            label_text = f" {name} "
            fm = painter.fontMetrics()
            text_w = fm.horizontalAdvance(label_text)
            text_h = fm.height()
            
            # Label Background
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(x, y + h_box, text_w, text_h + 4)
            
            # Label Text
            painter.setPen(QColor(30, 30, 46)) # Dark text
            painter.drawText(x, y + h_box + text_h, label_text)
