import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGroupBox
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt


# Check if OpenGL is available and import the necessary modules
# If OpenGL is not available, set OPENGL_AVAILABLE to False and use a fallback widget
try:
    from PyQt5.QtOpenGL import QGLWidget
    from OpenGL.GL import *
    from OpenGL.GLU import *
    import numpy as np
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False
    print("Warning: OpenGL dependencies not found. Running in fallback mode.")



# SpeakerGLWidget is the class that handles the 3D visualization of the speaker using OpenGL

## Structure explanation:
#
### initialization
#### __init__(): Sets up initial speaker properties and starts the animation timer
#### - Stores the state variables (material, size, enclosure, shape)
#
### OpenGL Methods/Setup
#### - initializeGL(): Sets up the OpenGL environment, lighting, and depth testing
#### - resizeGL(): Handles window resize events and updates the perspective
#### - paintGL(): Main rendering function called each frame to draw the speaker
#
### Update Methods (changes per interactions)
#### - set_internal_material(): Updates internal material property
#### - set_external_material(): Updates external material property
#### - set_size(): Updates size property
#### - set_enclosure(): Updates enclosure type property
#### - set_shape(): Updates shape property
#### - set_material_color(): Sets the color based on the selected material
#
### Drawing Methods
#### - draw_box(): Draws a rectangular box with specified dimensions
#### - draw_twisted_box(): Draws a trapezoid-like shape for the twisted speaker option
#### - draw_circle(): Helper method to draw circular speaker driver and port
#
### The speaker animation is handled by a timer event
#### - timerEvent(): Updates the rotation angle and triggers a repaint

class SpeakerGLWidget(QGLWidget):
    def __init__(self, parent=None):
        super(SpeakerGLWidget, self).__init__(parent)
        self.internal_material = "Plywood"
        self.external_material = "Plywood"
        self.size = "medium"
        self.enclosure = "sealed"
        self.shape = "rectangular"
        self.rotation_x = 0
        self.rotation_y = 0
        ##self.timer_id = self.startTimer(30)  # Start rotation timer
        self.last_pos = None

    # Mouse event handlers
    def mousePressEvent(self, event):
        self.last_pos = event.pos()
        
    def mouseMoveEvent(self, event):
        if self.last_pos is None:
            self.last_pos = event.pos()
            return
            
        dx = event.x() - self.last_pos.x()
        dy = event.y() - self.last_pos.y()
        
        # Adjust rotation based on mouse movement
        # You can adjust these values to control rotation sensitivity
        self.rotation_y += dx * 0.5
        self.rotation_x += dy * 0.5
        
        self.last_pos = event.pos()
        self.update()  # Request a redraw with new rotation values

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
        
        # Set material color based on selections
        self.set_material_color()
        
        # Draw speaker based on shape
        if self.shape == "rectangular":
            self.draw_box(3, 5, 2.5)
        elif self.shape == "square":
            self.draw_box(3, 3, 3)
        elif self.shape == "twisted":
            self.draw_twisted_box()
        
        # Draw speaker driver
        glPushMatrix()
        glColor3f(0.1, 0.1, 0.1)
        glTranslatef(0, 0, 1.1)
        self.draw_circle(0.75, 30)
        glPopMatrix()
        
        # If ported, draw port
        if self.enclosure == "ported":
            glPushMatrix()
            glColor3f(0.0, 0.0, 0.0)
            glTranslatef(0, -1.8, 1.1)
            self.draw_circle(0.25, 20)
            glPopMatrix()

    def set_material_color(self):
        # Set colors based on material selection
        if self.external_material == "Plywood":
            glColor3f(0.60, 0.35, 0.10)  # Brown
        elif self.external_material == "MDF wood":
            glColor3f(0.3255, 0.2, 0.1562)  # Darker brown
        elif self.external_material == "concrete":
            glColor3f(0.4, 0.4, 0.4)  # Gray
            
    def draw_box(self, width, height, depth):
        # Apply scaling based on size
        scale_factor = 1.0
        if self.size == "small":
            scale_factor = 0.7
        elif self.size == "large":
            scale_factor = 1.3
            
        width *= scale_factor
        height *= scale_factor
        depth *= scale_factor
        
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
        # Apply scaling based on size
        scale_factor = 1.0
        if self.size == "small":
            scale_factor = 0.7
        elif self.size == "large":
            scale_factor = 1.3
            
        # Base dimensions
        w, h, d = 1.5 * scale_factor, 2.5 * scale_factor, 1.0 * scale_factor
        
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

    def set_internal_material(self, material):
        self.internal_material = material
        self.update()
        
    def set_external_material(self, material):
        self.external_material = material
        self.update()
        
    def set_size(self, size):
        self.size = size
        self.update()
        
    def set_enclosure(self, enclosure):
        self.enclosure = enclosure
        self.update()
        
    def set_shape(self, shape):
        self.shape = shape
        self.update()



# FallbackWidget is a simple QWidget that serves as a placeholder when OpenGL is not available
#
## Structure explanation:
#
### Initialization
#### __init__(): Sets up initial speaker properties and minimum size
### - Stores the state variables (material, size, enclosure, shape)
#
### Paint Event
#### - paintEvent(): Handles the drawing of the speaker using basic Qt drawing methods
#### - Draws the speaker based on the selected properties (material, size, enclosure, shape)
#
### Interface matching
#### all set_seomething methods are the same as in the OpenGL widget

class FallbackWidget(QWidget):
    def __init__(self, parent=None):
        super(FallbackWidget, self).__init__(parent)
        self.setMinimumSize(400, 400)
        self.internal_material = "Plywood"
        self.external_material = "Plywood"
        self.size = "medium"
        self.enclosure = "sealed"
        self.shape = "rectangular"
        
    def paintEvent(self, event):
        from PyQt5.QtGui import QPainter, QBrush, QPen
        painter = QPainter(self)
        
        # Fill background
        painter.fillRect(self.rect(), QColor(50, 50, 50))
        
        # Set material color
        if self.external_material == "Plywood":
            color = QColor(139, 69, 19)
        elif self.external_material == "MDF wood":
            color = QColor(160, 82, 45)
        elif self.external_material == "concrete":
            color = QColor(128, 128, 128)
        
        # Adjust size
        size_factor = 1.0
        if self.size == "small":
            size_factor = 0.7
        elif self.size == "large":
            size_factor = 1.3
        
        width = int(200 * size_factor)
        height = int(300 * size_factor)
        
        # Draw speaker based on shape
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
            
        # Draw speaker driver
        driver_x = x + width // 2
        driver_y = y + height // 2
        driver_radius = min(width, height) // 4
        
        painter.setBrush(QBrush(QColor(30, 30, 30)))
        painter.drawEllipse(driver_x - driver_radius, driver_y - driver_radius, 
                           driver_radius * 2, driver_radius * 2)
        
        # If ported, draw port
        if self.enclosure == "ported":
            port_radius = driver_radius // 3
            port_x = driver_x
            port_y = y + height - port_radius * 2
            
            painter.setBrush(QBrush(QColor(0, 0, 0)))
            painter.drawEllipse(port_x - port_radius, port_y - port_radius,
                              port_radius * 2, port_radius * 2)
    
    def set_internal_material(self, material):
        self.internal_material = material
        self.update()
        
    def set_external_material(self, material):
        self.external_material = material
        self.update()
        
    def set_size(self, size):
        self.size = size
        self.update()
        
    def set_enclosure(self, enclosure):
        self.enclosure = enclosure
        self.update()
        
    def set_shape(self, shape):
        self.shape = shape
        self.update()



# The SpeakerDesignStudio class is the main window of the application and is responsible for the UI creation and for connecting the different parts of the project
#
## Structure explanation:
#
### Initialization
#### __init__(): Sets up the main window, sidebar, and speaker visualization area
### - Creates the layout structure with sidebar on the left (1/4 width) and speaker view on the right (3/4 width)
### - Applies dark theme styling using stylesheet
#
### Group Creation Methods
#### - create_material_group(): Creates internal material selection buttons
#### - create_ext_material_group(): Creates external material selection buttons
#### - create_size_group(): Creates size selection buttons
#### - create_enclosure_group(): Creates enclosure type selection buttons
#### - create_shape_group(): Creates speaker shape selection buttons
#
### Helper Methods
#### - uncheck_other_buttons(): Unchecks all buttons in a group except the selected one
#
### Event Methods
#### - change_internal_material(): Updates internal material selection
#### - change_external_material(): Updates external material selection
#### - change_size(): Updates speaker size
#### - change_enclosure(): Updates enclosure type
#### - change_shape(): Updates speaker shape

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
        self.create_material_group(sidebar_layout)
        self.create_ext_material_group(sidebar_layout)
        self.create_size_group(sidebar_layout)
        self.create_enclosure_group(sidebar_layout)
        self.create_shape_group(sidebar_layout)
        
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
        """)
        
    def create_material_group(self, layout):
        group = QGroupBox("Internal Material")
        group_layout = QVBoxLayout()
        
        btn_plywood = QPushButton("Plywood")
        btn_plywood.setCheckable(True)
        btn_plywood.setChecked(True)
        btn_plywood.clicked.connect(lambda: self.change_internal_material("Plywood"))
        
        btn_mdf = QPushButton("MDF Wood")
        btn_mdf.setCheckable(True)
        btn_mdf.clicked.connect(lambda: self.change_internal_material("MDF wood"))
        
        # Group buttons for exclusive selection
        self.internal_material_buttons = [btn_plywood, btn_mdf]
        
        group_layout.addWidget(btn_plywood)
        group_layout.addWidget(btn_mdf)
        group.setLayout(group_layout)
        layout.addWidget(group)
        
    def create_ext_material_group(self, layout):
        group = QGroupBox("External Material")
        group_layout = QVBoxLayout()
        
        btn_concrete = QPushButton("Concrete")
        btn_concrete.setCheckable(True)
        btn_concrete.clicked.connect(lambda: self.change_external_material("concrete"))
        
        btn_plywood = QPushButton("Plywood")
        btn_plywood.setCheckable(True)
        btn_plywood.setChecked(True)
        btn_plywood.clicked.connect(lambda: self.change_external_material("Plywood"))
        
        btn_mdf = QPushButton("MDF Wood")
        btn_mdf.setCheckable(True)
        btn_mdf.clicked.connect(lambda: self.change_external_material("MDF wood"))
        
        # Group buttons for exclusive selection
        self.external_material_buttons = [btn_concrete, btn_plywood, btn_mdf]
        
        group_layout.addWidget(btn_concrete)
        group_layout.addWidget(btn_plywood)
        group_layout.addWidget(btn_mdf)
        group.setLayout(group_layout)
        layout.addWidget(group)
        
    def create_size_group(self, layout):
        group = QGroupBox("Size")
        group_layout = QVBoxLayout()
        
        btn_small = QPushButton("Small")
        btn_small.setCheckable(True)
        btn_small.clicked.connect(lambda: self.change_size("small"))
        
        btn_medium = QPushButton("Medium")
        btn_medium.setCheckable(True)
        btn_medium.setChecked(True)
        btn_medium.clicked.connect(lambda: self.change_size("medium"))
        
        btn_large = QPushButton("Large")
        btn_large.setCheckable(True)
        btn_large.clicked.connect(lambda: self.change_size("large"))
        
        # Group buttons for exclusive selection
        self.size_buttons = [btn_small, btn_medium, btn_large]
        
        group_layout.addWidget(btn_small)
        group_layout.addWidget(btn_medium)
        group_layout.addWidget(btn_large)
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
    
    def uncheck_other_buttons(self, button_list, selected_button):
        for button in button_list:
            if button != selected_button:
                button.setChecked(False)
    
    def change_internal_material(self, material):
        button = self.sender()
        self.uncheck_other_buttons(self.internal_material_buttons, button)
        self.speaker_view.set_internal_material(material)
    
    def change_external_material(self, material):
        button = self.sender()
        self.uncheck_other_buttons(self.external_material_buttons, button)
        self.speaker_view.set_external_material(material)
    
    def change_size(self, size):
        button = self.sender()
        self.uncheck_other_buttons(self.size_buttons, button)
        self.speaker_view.set_size(size)
    
    def change_enclosure(self, enclosure):
        button = self.sender()
        self.uncheck_other_buttons(self.enclosure_buttons, button)
        self.speaker_view.set_enclosure(enclosure)
    
    def change_shape(self, shape):
        button = self.sender()
        self.uncheck_other_buttons(self.shape_buttons, button)
        self.speaker_view.set_shape(shape)



# Main execution block
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SpeakerDesignStudio()
    window.show()
    sys.exit(app.exec_())