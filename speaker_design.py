import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGroupBox, QCheckBox, QColorDialog, QLineEdit, QComboBox)
from PyQt5.QtGui import QColor, QPainter, QBrush, QPen
from PyQt5.QtCore import Qt

try:
    from PyQt5.QtOpenGL import QGLWidget
    from OpenGL.GL import *
    from OpenGL.GLU import *
    import numpy as np
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False
    print("Warning: OpenGL dependencies not found. Running in fallback mode.")

class SpeakerGLWidget(QGLWidget):
    def __init__(self, parent=None):
        super(SpeakerGLWidget, self).__init__(parent)
        self.shape = "rectangular"
        self.drivers = {"tweeter": False, "woofer": True, "subwoofer": False}
        self.enclosure = "sealed"  # Default is sealed, no longer changeable
        self.rotation_x = 0
        self.rotation_y = 0
        
        # New aesthetic properties
        self.speaker_color = QColor(60, 60, 60)  # Default gray
        self.lettering = ""
        self.pattern = "none"  # none, stripes, gradient, etc.
        
        # Variables for mouse rotation control
        self.last_pos = None
        
        # Start automatic rotation (comment this out if you prefer mouse control only)
        self.timer_id = self.startTimer(30)

    def initializeGL(self):
        glClearColor(1, 1, 1, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        
        # Set up light position
        glLight(GL_LIGHT0, GL_POSITION, (10, 10, 10, 1))
        glLight(GL_LIGHT0, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
        glLight(GL_LIGHT0, GL_AMBIENT, (0.25, 0.25, 0.25, 1.0))

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width / height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Position camera
        glTranslatef(0, 0, -15)
        
        # Apply rotation
        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)
        
        # Set speaker color from QColor
        glColor3f(self.speaker_color.redF(), self.speaker_color.greenF(), self.speaker_color.blueF())
        
        # Draw speaker based on shape
        if self.shape == "rectangular":
            self.draw_box(3, 5, 2)
        elif self.shape == "square":
            self.draw_box(2, 2, 2)
        elif self.shape == "twisted":
            self.draw_twisted_box()
        
        # Draw pattern if specified
        if self.pattern != "none":
            self.draw_pattern()
            
        # Draw lettering if specified
        if self.lettering:
            self.draw_lettering()
        
        # Draw drivers based on selection
        self.draw_drivers()
        
        # If ported, draw port
        if self.enclosure == "ported" and self.drivers["subwoofer"]:
            glPushMatrix()
            glColor3f(0.0, 0.0, 0.0)
            glTranslatef(0, -1.8, 1.1)
            self.draw_circle(0.5, 20)
            glPopMatrix()
            
    def draw_pattern(self):
        # Draw patterns based on the selected pattern type
        if self.pattern == "checkered":
            self.draw_checkered()
        
    def draw_checkered(self):
        # Draw checkered pattern on the front face
        glPushMatrix()
        
        # Slightly offset from front face to avoid z-fighting
        glTranslatef(0, 0, -1.01)
        glNormal3f(0, 0, -1)
        # Darker color for checks
        r, g, b = self.speaker_color.redF(), self.speaker_color.greenF(), self.speaker_color.blueF()
        glColor3f(r * 0.7, g * 0.7, b * 0.7)
        
        # Draw 4x4 grid of alternating squares
        square_size = 0.25
        for x in range(-2, 2):
            for y in range(-2, 2):
                if (x + y) % 2 == 0:  # Only draw alternating squares
                    glBegin(GL_QUADS)
                    glVertex3f(x * square_size, y * square_size, 0)
                    glVertex3f((x+1) * square_size, y * square_size, 0)
                    glVertex3f((x+1) * square_size, (y+1) * square_size, 0)
                    glVertex3f(x * square_size, (y+1) * square_size, 0)
                    glEnd()
        
        glPopMatrix()
        
    def draw_lettering(self):
        # Simple representation of lettering on the speaker
        # OpenGL doesn't have built-in text rendering, so this is a placeholder
        # In a real implementation, you'd use a texture or proper text rendering library
        
        glPushMatrix()
        
        # Position at the bottom of the speaker
        glTranslatef(0, -2.2, 1.1)
        
        # Use black for the text
        glColor3f(0.1, 0.1, 0.1)
        
        # Draw a horizontal bar to represent text
        # In a real implementation, this would be actual text
        text_width = min(2.0, len(self.lettering) * 0.15)
        
        glBegin(GL_QUADS)
        glVertex3f(-text_width, -0.2, 0)
        glVertex3f(text_width, -0.2, 0)
        glVertex3f(text_width, 0.2, 0)
        glVertex3f(-text_width, 0.2, 0)
        glEnd()
        
        glPopMatrix()
            
    def draw_drivers(self):
        driver_positions = {
            "tweeter": (0, 1.9, 1.1),
            "woofer": (0, 0.5, 1.1),
            "subwoofer": (0, -1.2, 1.1)
        }
        
        driver_sizes = {
            "tweeter": 0.3,
            "woofer": 1.0,
            "subwoofer": 1.0
        }
        
        active_drivers = [d for d, active in self.drivers.items() if active]
        
        # Adjust sizes based on which drivers are selected
        if all(self.drivers.values()):
            # All three drivers are selected - make woofer smaller
            driver_sizes["woofer"] = 0.6
        elif len(active_drivers) == 2 and "woofer" in active_drivers and "subwoofer" in active_drivers:
            # Only woofer and subwoofer are selected - make subwoofer bigger
            driver_sizes["subwoofer"] = 1.1
        
        if len(active_drivers) == 1:
            # Only one driver - center it
            driver = active_drivers[0]
            glPushMatrix()
            glColor3f(0.1, 0.1, 0.1)
            glTranslatef(0, 0, 1.1)  # Center position
            radius = driver_sizes[driver] * 1.2  # Make it larger when alone
            self.draw_circle(radius, 30)
            glPopMatrix()
            
        elif len(active_drivers) == 2:
            # Two drivers - adjust positions
            positions = [(0, 1.1, 1.1), (0, -1.1, 1.1)]
            for i, driver in enumerate(active_drivers):
                glPushMatrix()
                glColor3f(0.1, 0.1, 0.1)
                glTranslatef(*positions[i])
                self.draw_circle(driver_sizes[driver], 30)
                glPopMatrix()
                
        else:
            # All three drivers or other combinations
            for driver, active in self.drivers.items():
                if active:
                    glPushMatrix()
                    glColor3f(0.1, 0.1, 0.1)
                    glTranslatef(*driver_positions[driver])
                    self.draw_circle(driver_sizes[driver], 25)
                    glPopMatrix()

    def draw_box(self, width, height, depth):
        w, h, d = width/2, height/2, depth/2
        
        # Front face
        glBegin(GL_QUADS)
        glNormal3f(0, 0, 1)
        glVertex3f(-w, -h, d)
        glVertex3f(w, -h, d)
        glVertex3f(w, h, d)
        glVertex3f(-w, h, d)
        
        # Back face
        glNormal3f(0, 0, -1)
        glVertex3f(-w, -h, -d)
        glVertex3f(-w, h, -d)
        glVertex3f(w, h, -d)
        glVertex3f(w, -h, -d)
        
        # Top face
        glNormal3f(0, 1, 0)
        glVertex3f(-w, h, -d)
        glVertex3f(-w, h, d)
        glVertex3f(w, h, d)
        glVertex3f(w, h, -d)
        
        # Bottom face
        glNormal3f(0, -1, 0)
        glVertex3f(-w, -h, -d)
        glVertex3f(w, -h, -d)
        glVertex3f(w, -h, d)
        glVertex3f(-w, -h, d)
        
        # Right face
        glNormal3f(1, 0, 0)
        glVertex3f(w, -h, -d)
        glVertex3f(w, h, -d)
        glVertex3f(w, h, d)
        glVertex3f(w, -h, d)
        
        # Left face
        glNormal3f(-1, 0, 0)
        glVertex3f(-w, -h, -d)
        glVertex3f(-w, -h, d)
        glVertex3f(-w, h, d)
        glVertex3f(-w, h, -d)
        glEnd()

    def draw_twisted_box(self):
        # Base dimensions
        w, h, d = 1.5, 2.5, 1.0
        
        # Draw a twisted box (bottom wider than top)
        glBegin(GL_QUADS)
        # Front face
        glNormal3f(0, 0, 1)
        glVertex3f(-w * 1.2, -h, d)
        glVertex3f(w * 1.2, -h, d)
        glVertex3f(w * 0.8, h, d)
        glVertex3f(-w * 0.8, h, d)
        
        # Back face
        glNormal3f(0, 0, -1)
        glVertex3f(-w * 1.2, -h, -d)
        glVertex3f(-w * 0.8, h, -d)
        glVertex3f(w * 0.8, h, -d)
        glVertex3f(w * 1.2, -h, -d)
        
        # Top face
        glNormal3f(0, 1, 0)
        glVertex3f(-w * 0.8, h, -d)
        glVertex3f(-w * 0.8, h, d)
        glVertex3f(w * 0.8, h, d)
        glVertex3f(w * 0.8, h, -d)
        
        # Bottom face
        glNormal3f(0, -1, 0)
        glVertex3f(-w * 1.2, -h, -d)
        glVertex3f(w * 1.2, -h, -d)
        glVertex3f(w * 1.2, -h, d)
        glVertex3f(-w * 1.2, -h, d)
        
        # Right face
        glNormal3f(1, 0, 0)
        glVertex3f(w * 1.2, -h, -d)
        glVertex3f(w * 0.8, h, -d)
        glVertex3f(w * 0.8, h, d)
        glVertex3f(w * 1.2, -h, d)
        
        # Left face
        glNormal3f(-1, 0, 0)
        glVertex3f(-w * 1.2, -h, -d)
        glVertex3f(-w * 1.2, -h, d)
        glVertex3f(-w * 0.8, h, d)
        glVertex3f(-w * 0.8, h, -d)
        glEnd()

    def draw_circle(self, radius, segments):
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0, 0)  # Center
        for i in range(segments + 1):
            angle = 2 * np.pi * i / segments
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            glVertex3f(x, y, 0)
        glEnd()

    def timerEvent(self, event):
        self.rotation_y += 1
        if self.rotation_y > 360:
            self.rotation_y = 0
        self.update()
        
    def mousePressEvent(self, event):
        self.last_pos = event.pos()
        
    def mouseMoveEvent(self, event):
        if self.last_pos is None:
            self.last_pos = event.pos()
            return
            
        dx = event.x() - self.last_pos.x()
        dy = event.y() - self.last_pos.y()
        
        # Adjust rotation based on mouse movement
        self.rotation_y += dx * 0.5
        self.rotation_x += dy * 0.5
        
        self.last_pos = event.pos()
        self.update()

    def set_shape(self, shape):
        self.shape = shape
        self.update()
        
    def set_driver(self, driver, enabled):
        self.drivers[driver] = enabled
        
        # Enforce rule: Tweeter can't be alone
        if driver != "tweeter" and not enabled:
            # Check if only tweeter would remain
            if self.drivers["tweeter"] and not any(self.drivers[d] for d in ["woofer", "subwoofer"]):
                # Force tweeter off too
                self.drivers["tweeter"] = False
                
        self.update()
    
    def set_color(self, color):
        self.speaker_color = color
        self.update()
        
    def set_lettering(self, text):
        self.lettering = text
        self.update()
        
    def set_pattern(self, pattern):
        self.pattern = pattern
        self.update()

class FallbackWidget(QWidget):
    """Fallback widget when OpenGL is not available"""
    def __init__(self, parent=None):
        super(FallbackWidget, self).__init__(parent)
        self.setMinimumSize(400, 400)
        self.shape = "rectangular"
        self.drivers = {"tweeter": False, "woofer": True, "subwoofer": False}
        self.enclosure = "sealed"
        
        # New aesthetic properties
        self.speaker_color = QColor(139, 69, 19)  # Brown
        self.lettering = ""
        self.pattern = "none"
        
    def paintEvent(self, event):
        from PyQt5.QtGui import QPainter, QBrush, QPen
        painter = QPainter(self)
        
        # Fill background
        painter.fillRect(self.rect(), QColor(50, 50, 50))
        
        # Set speaker box color
        color = self.speaker_color
        
        # Draw speaker based on shape
        width = 200
        height = 300
        
        x = (self.width() - width) // 2
        y = (self.height() - height) // 2
        
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(Qt.black, 2))
        
        if self.shape == "rectangular":
            painter.drawRect(x, y, width, height)
        elif self.shape == "square":
            side = min(width, height)
            x = (self.width() - side) // 2
            y = (self.height() - side) // 2
            painter.drawRect(x, y, side, side)
        elif self.shape == "twisted":
            points = [
                (x - int(width * 0.1), y + height),
                (x + width + int(width * 0.1), y + height),
                (x + width - int(width * 0.1), y),
                (x + int(width * 0.1), y)
            ]
            painter.drawPolygon(*points)
            
        # Draw pattern if applicable
        if self.pattern != "none":
            self.draw_pattern(painter, x, y, width, height)
            
        # Draw lettering if applicable
        if self.lettering:
            painter.setBrush(QBrush(QColor(0, 0, 0)))
            text_width = min(width * 0.8, len(self.lettering) * 10)
            text_height = 20
            text_x = x + (width - text_width) // 2
            text_y = y + height - 30
            painter.drawRect(text_x, text_y, text_width, text_height)
            
        # Draw drivers based on selection
        self.draw_drivers(painter, x, y, width, height)
            
        # If ported, draw port
        if self.enclosure == "ported" and self.drivers["subwoofer"]:
            port_radius = 20
            port_x = x + width // 2
            port_y = y + height - port_radius * 2
            
            painter.setBrush(QBrush(QColor(0, 0, 0)))
            painter.drawEllipse(port_x - port_radius, port_y - port_radius,
                              port_radius * 2, port_radius * 2)
    
    def draw_pattern(self, painter, x, y, width, height):
        if self.pattern == "stripes":
            # Draw horizontal stripes
            stripe_height = height // 6
            darker_color = QColor(
                int(self.speaker_color.red() * 0.7),
                int(self.speaker_color.green() * 0.7),
                int(self.speaker_color.blue() * 0.7)
            )
            
            painter.setBrush(QBrush(darker_color))
            for i in range(3):
                stripe_y = y + (i * 2 + 1) * stripe_height
                painter.drawRect(x, stripe_y, width, stripe_height)
                
        elif self.pattern == "checkered":
            # Draw checkered pattern
            darker_color = QColor(
                int(self.speaker_color.red() * 0.7),
                int(self.speaker_color.green() * 0.7),
                int(self.speaker_color.blue() * 0.7)
            )
            
            painter.setBrush(QBrush(darker_color))
            square_size = width // 4
            for i in range(4):
                for j in range(6):  # More vertical squares for rectangular speakers
                    if (i + j) % 2 == 0:
                        square_x = x + i * square_size
                        square_y = y + j * square_size
                        painter.drawRect(square_x, square_y, square_size, square_size)
        
        elif self.pattern == "gradient":
            # Simple gradient simulation with horizontal strips
            strips = 10
            strip_height = height // strips
            
            for i in range(strips):
                factor = 0.6 + (i / strips) * 0.8
                strip_color = QColor(
                    int(self.speaker_color.red() * factor),
                    int(self.speaker_color.green() * factor),
                    int(self.speaker_color.blue() * factor)
                )
                
                strip_y = y + i * strip_height
                painter.setBrush(QBrush(strip_color))
                painter.drawRect(x, strip_y, width, strip_height)
                              
    def draw_drivers(self, painter, box_x, box_y, box_width, box_height):
        # Define driver sizes
        driver_sizes = {
            "tweeter": 20,
            "woofer": 40,
            "subwoofer": 70
        }
        
        active_drivers = [d for d, active in self.drivers.items() if active]
        
        # Adjust sizes based on which drivers are selected
        if all(self.drivers.values()):
            # All three drivers are selected - make woofer smaller
            driver_sizes["woofer"] = 25
        elif len(active_drivers) == 2 and "woofer" in active_drivers and "subwoofer" in active_drivers:
            # Only woofer and subwoofer are selected - make subwoofer bigger
            driver_sizes["subwoofer"] = 85
        
        # Calculate center positions
        center_x = box_x + box_width // 2
        
        # Single driver case
        if len(active_drivers) == 1:
            # Only one driver - center it
            driver = active_drivers[0]
            radius = driver_sizes[driver] * 1.5  # Make it larger when alone
            painter.setBrush(QBrush(QColor(30, 30, 30)))
            painter.drawEllipse(center_x - radius, box_y + box_height//2 - radius, 
                              radius * 2, radius * 2)
                              
        elif len(active_drivers) == 2:
            # Two drivers - adjust positions
            positions = [
                (center_x, box_y + box_height//3),
                (center_x, box_y + box_height*2//3)
            ]
            
            for i, driver in enumerate(active_drivers):
                radius = driver_sizes[driver]
                x, y = positions[i]
                painter.setBrush(QBrush(QColor(30, 30, 30)))
                painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)
                
        else:
            # All drivers or other combinations
            positions = {
                "tweeter": (center_x, box_y + box_height//4),
                "woofer": (center_x, box_y + box_height//2),
                "subwoofer": (center_x, box_y + box_height*3//4)
            }
            
            for driver, active in self.drivers.items():
                if active:
                    radius = driver_sizes[driver]
                    x, y = positions[driver]
                    painter.setBrush(QBrush(QColor(30, 30, 30)))
                    painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)
    
    def set_shape(self, shape):
        self.shape = shape
        self.update()
        
    def set_driver(self, driver, enabled):
        self.drivers[driver] = enabled
        
        # Enforce rule: Tweeter can't be alone
        if driver != "tweeter" and not enabled:
            # Check if only tweeter would remain
            if self.drivers["tweeter"] and not any(self.drivers[d] for d in ["woofer", "subwoofer"]):
                # Force tweeter off too
                self.drivers["tweeter"] = False
                
        self.update()
    
    def set_color(self, color):
        self.speaker_color = color
        self.update()
        
    def set_lettering(self, text):
        self.lettering = text
        self.update()
        
    def set_pattern(self, pattern):
        self.pattern = pattern
        self.update()

class SpeakerDesignStudio(QMainWindow):
    def __init__(self):
        super(SpeakerDesignStudio, self).__init__()
        self.setWindowTitle("Maaleh Audio Studio")
        self.setMinimumSize(800, 600)
        
        # Create main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        if OPENGL_AVAILABLE:
            self.speaker_view = SpeakerGLWidget()
        else:
            self.speaker_view = FallbackWidget()
        
        # Create sidebar
        sidebar = QWidget()
        sidebar.setMaximumWidth(250)
        sidebar_layout = QVBoxLayout(sidebar)
        
        # Title
        title = QLabel("Design Your Speaker")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        sidebar_layout.addWidget(title)
        
        # Create button groups
        self.create_shape_group(sidebar_layout)
        self.create_driver_group(sidebar_layout)
        self.create_aesthetics_group(sidebar_layout)  # New aesthetics group
        
        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.speaker_view, 3)
        
        # Set dark theme
        # Set dark theme
        self.setStyleSheet("""
            QGLWidget, QWidget#fallback {
                background-color: #1a1a1a;
            }
            QMainWindow, QWidget {
                background-color: #000000;
                color: #DDDDDD;
            }
            QPushButton {
                background-color: #000000;
                color: #DDDDDD;
                border: none;
                padding: 8px;
                margin: 2px;
                border-radius: 4px;
            }
            QPushButton:hover   { background-color: #333333; }
            QPushButton:pressed { background-color: #444444; }
            QPushButton:checked {
                background-color: #5b4c81;
                font-weight: bold;
            }
            QGroupBox {
                background-color: #000000;
                border: 1px solid #444444;
                margin-top: 12px;
                padding-top: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #DDDDDD;
            }
            QCheckBox {
                background-color: #000000;
                color: #DDDDDD;
                padding: 8px;
                margin: 2px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:checked {
                background-color: #5b4c81;
                border: 2px solid #DDDDDD;
                border-radius: 4px;
            }
            QLineEdit {
                background-color: #333333;
                color: #DDDDDD;
                border: 1px solid #555555;
                padding: 4px;
                border-radius: 4px;
            }
            QComboBox {
                background-color: #444444;
                color: #DDDDDD;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QComboBox:hover {
                background-color: #555555;
            }
            QComboBox QAbstractItemView {
                background-color: #444444;
                color: #DDDDDD;
                selection-background-color: #5b4c81;
            }
        """)

        
    def create_shape_group(self, layout):
        group = QGroupBox("Shape")
        group_layout = QVBoxLayout()
        
        btn_rectangular = QPushButton("Rectangular")
        btn_rectangular.setCheckable(True)
        btn_rectangular.setChecked(True)
        btn_rectangular.clicked.connect(lambda: self.change_shape("rectangular"))
        
        btn_square = QPushButton("Square")
        btn_square.setCheckable(True)
        btn_square.clicked.connect(lambda: self.change_shape("square"))
        
        btn_twisted = QPushButton("Twisted")
        btn_twisted.setCheckable(True)
        btn_twisted.clicked.connect(lambda: self.change_shape("twisted"))
        
        # Group buttons for exclusive selection
        self.shape_buttons = [btn_rectangular, btn_square, btn_twisted]
        
        group_layout.addWidget(btn_rectangular)
        group_layout.addWidget(btn_square)
        group_layout.addWidget(btn_twisted)
        group.setLayout(group_layout)
        layout.addWidget(group)
        
    def create_driver_group(self, layout):
        group = QGroupBox("Drivers")
        group_layout = QVBoxLayout()
        
        # Use checkboxes for drivers since multiple can be selected
        self.chk_tweeter = QCheckBox("Tweeter")
        self.chk_tweeter.setChecked(False)
        self.chk_tweeter.stateChanged.connect(lambda state: self.change_driver("tweeter", state == Qt.Checked))
        
        self.chk_woofer = QCheckBox("Woofer")
        self.chk_woofer.setChecked(True)
        self.chk_woofer.stateChanged.connect(lambda state: self.change_driver("woofer", state == Qt.Checked))
        
        self.chk_subwoofer = QCheckBox("Subwoofer")
        self.chk_subwoofer.setChecked(False)
        self.chk_subwoofer.stateChanged.connect(lambda state: self.change_driver("subwoofer", state == Qt.Checked))
        
        # Add a note about tweeter restriction
        note = QLabel("Note: Tweeter can only be selected with at least one other driver")
        note.setWordWrap(True)
        note.setStyleSheet("font-style: italic; font-size: 10px; color: #aaa;")
        
        group_layout.addWidget(self.chk_tweeter)
        group_layout.addWidget(self.chk_woofer)
        group_layout.addWidget(self.chk_subwoofer)
        group_layout.addWidget(note)
        
        group.setLayout(group_layout)
        layout.addWidget(group)

    def create_aesthetics_group(self, layout):
        group = QGroupBox("Aesthetics")
        group_layout = QVBoxLayout()
        
        # Color selection
        color_label = QLabel("Speaker Color:")
        self.color_button = QPushButton("Choose Color")
        self.color_button.clicked.connect(self.choose_color)
        self.color_indicator = QLabel()
        self.color_indicator.setFixedSize(20, 20)
        self.color_indicator.setStyleSheet(f"background-color: {self.speaker_view.speaker_color.name()}; border: 1px solid white;")
        
        color_layout = QHBoxLayout()
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.color_indicator)
        color_layout.addWidget(self.color_button)
        
        # Lettering/branding
        lettering_label = QLabel("Logo Text:")
        self.lettering_input = QLineEdit()
        self.lettering_input.setPlaceholderText("Enter brand name...")
        self.lettering_input.textChanged.connect(self.change_lettering)
        
        # Pattern selection
        pattern_label = QLabel("Pattern:")
        self.pattern_combo = QComboBox()
        self.pattern_combo.addItems(["None", "Checkered"])
        self.pattern_combo.currentTextChanged.connect(self.change_pattern)
        
        # Add all widgets to the layout
        group_layout.addLayout(color_layout)
        group_layout.addSpacing(10)
        group_layout.addWidget(lettering_label)
        group_layout.addWidget(self.lettering_input)
        group_layout.addSpacing(10)
        group_layout.addWidget(pattern_label)
        group_layout.addWidget(self.pattern_combo)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
    
    def uncheck_other_buttons(self, button_list, selected_button):
        for button in button_list:
            if button != selected_button:
                button.setChecked(False)
    
    def change_shape(self, shape):
        button = self.sender()
        self.uncheck_other_buttons(self.shape_buttons, button)
        self.speaker_view.set_shape(shape)
    
    def change_driver(self, driver, enabled):
        # Set the driver state in the speaker view
        self.speaker_view.set_driver(driver, enabled)
        
        # Update checkbox UI to reflect any changes made in the speaker view
        # (particularly if the tweeter rule caused automatic changes)
        self.chk_tweeter.setChecked(self.speaker_view.drivers["tweeter"])
        self.chk_woofer.setChecked(self.speaker_view.drivers["woofer"])
        self.chk_subwoofer.setChecked(self.speaker_view.drivers["subwoofer"])
    
    def choose_color(self):
        color = QColorDialog.getColor(self.speaker_view.speaker_color, self, "Choose Speaker Color")
        if color.isValid():
            self.speaker_view.set_color(color)
            self.color_indicator.setStyleSheet(f"background-color: {color.name()}; border: 1px solid white;")
    
    def change_lettering(self, text):
        self.speaker_view.set_lettering(text)
        
    def change_pattern(self, pattern_name):
        pattern = pattern_name.lower()
        if pattern == "none":
            pattern = "none"  # Keep as is
        self.speaker_view.set_pattern(pattern)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SpeakerDesignStudio()
    window.show()
    sys.exit(app.exec_())