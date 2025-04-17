import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QGroupBox, QCheckBox)
from PyQt5.QtGui import QColor
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
        self.enclosure = "sealed"
        self.rotation_x = 0
        self.rotation_y = 0
        
        # Variables for mouse rotation control
        self.last_pos = None
        
        # Start automatic rotation (comment this out if you prefer mouse control only)
        ##self.timer_id = self.startTimer(30)

    def initializeGL(self):
        glClearColor(0.15, 0.15, 0.15, 1.0)
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
        
        # Set default speaker color - medium brown
        glColor3f(0.55, 0.27, 0.07)
        
        # Draw speaker based on shape
        if self.shape == "rectangular":
            self.draw_box(3, 5, 2)
        elif self.shape == "square":
            self.draw_box(3, 3, 3)
        elif self.shape == "twisted":
            self.draw_twisted_box()
        
        # Draw drivers based on selection
        self.draw_drivers()
        
        # If ported, draw port
        if self.enclosure == "ported" and self.drivers["subwoofer"]:
            glPushMatrix()
            glColor3f(0.0, 0.0, 0.0)
            glTranslatef(0, -1.8, 1.1)
            self.draw_circle(0.5, 20)
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
        
    def set_enclosure(self, enclosure):
        self.enclosure = enclosure
        self.update()

class FallbackWidget(QWidget):
    """Fallback widget when OpenGL is not available"""
    def __init__(self, parent=None):
        super(FallbackWidget, self).__init__(parent)
        self.setMinimumSize(400, 400)
        self.shape = "rectangular"
        self.drivers = {"tweeter": False, "woofer": True, "subwoofer": False}
        self.enclosure = "sealed"
        
    def paintEvent(self, event):
        from PyQt5.QtGui import QPainter, QBrush, QPen
        painter = QPainter(self)
        
        # Fill background
        painter.fillRect(self.rect(), QColor(50, 50, 50))
        
        # Set speaker box color
        color = QColor(139, 69, 19)  # Brown
        
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
        
    def set_enclosure(self, enclosure):
        self.enclosure = enclosure
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
        self.create_enclosure_group(sidebar_layout)
        
        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)
        
        # Create 3D view
        if OPENGL_AVAILABLE:
            self.speaker_view = SpeakerGLWidget()
        else:
            self.speaker_view = FallbackWidget()
        main_layout.addWidget(self.speaker_view, 3)
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow, QWidget { background-color: #1a1a1a; color: white; }
            QPushButton { 
                background-color: #444; 
                color: white; 
                border: none; 
                padding: 8px; 
                margin: 2px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #555; }
            QPushButton:pressed { background-color: #666; }
            QPushButton:checked { 
                background-color: #b45309; 
                font-weight: bold;
            }
            QGroupBox { 
                border: 1px solid #444; 
                margin-top: 12px; 
                padding-top: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QCheckBox {
                padding: 8px;
                margin: 2px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:checked {
                background-color: #b45309;
                border: 2px solid white;
                border-radius: 4px;
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
        
    def create_enclosure_group(self, layout):
        group = QGroupBox("Enclosure Type")
        group_layout = QVBoxLayout()
        
        btn_sealed = QPushButton("Sealed")
        btn_sealed.setCheckable(True)
        btn_sealed.setChecked(True)
        btn_sealed.clicked.connect(lambda: self.change_enclosure("sealed"))
        
        btn_ported = QPushButton("Ported")
        btn_ported.setCheckable(True)
        btn_ported.clicked.connect(lambda: self.change_enclosure("ported"))
        
        # Group buttons for exclusive selection
        self.enclosure_buttons = [btn_sealed, btn_ported]
        
        group_layout.addWidget(btn_sealed)
        group_layout.addWidget(btn_ported)
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
    
    def change_enclosure(self, enclosure):
        button = self.sender()
        self.uncheck_other_buttons(self.enclosure_buttons, button)
        self.speaker_view.set_enclosure(enclosure)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SpeakerDesignStudio()
    window.show()
    sys.exit(app.exec_())