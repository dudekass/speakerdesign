# Maaleh Audio Studio — Speaker Design Tool
 
A real-time 3D speaker enclosure design and visualization tool built in Python, developed as part of the R&D foundation for **Maaleh**, an independent audio electronics brand focused on high-fidelity speaker design and DSP-driven audio hardware.
 
---
 
## Overview
 
This desktop application allows users to interactively design and visualize speaker enclosures in 3D, configuring enclosure geometry, driver configuration, materials, and aesthetic branding in real time. It was built to apply acoustic enclosure design principles — crossover theory, driver placement, ported vs. sealed tuning — in a hands-on software environment.
 
The tool renders a live 3D model of the speaker that responds immediately to design changes, with full mouse-controlled rotation and OpenGL-accelerated rendering. A 2D fallback renderer is included for environments without OpenGL support.
 
---
 
## Features
 
- **3D OpenGL rendering** with real-time mouse-controlled rotation (drag to orbit)
- **Enclosure geometry selection** — Rectangular, Square, or Tapered (wider base) profiles
- **Driver configuration** — Tweeter, Woofer, and Subwoofer with acoustic placement rules enforced (tweeter cannot operate without a mid/low driver)
- **Enclosure type** — Sealed or Ported, with port geometry rendered automatically for ported + subwoofer configurations
- **Material selection** — Internal and external material choices (Plywood, MDF, Concrete) with corresponding color rendering
- **Custom color picker** — Full RGB color selection for enclosure exterior via system color dialog
- **Logo / branding text** — Live brand name overlay on enclosure face
- **Surface pattern** — Checkered pattern overlay option
- **Fallback 2D renderer** — Automatic fallback to Qt-native 2D painting when OpenGL/PyOpenGL is unavailable
- **Application launcher** — Main menu with routing to Speaker Design, Tube Amp (planned), and future modules
---
 
## Project Structure
 
```
maaleh-audio-studio/
├── main.py            
├── speaker_design.py
|–– speaker.py
|–— requirements.txt
└── README.md
```
 
---
 
## Requirements
 
```
Python 3.8+
PyQt5
PyOpenGL
PyOpenGL-accelerate  (optional, improves performance)
numpy
```
 
Install dependencies:
 
```bash
pip install PyQt5 PyOpenGL PyOpenGL-accelerate numpy
```
 
---
 
## Running the App
 
```bash
python main.py
```
 
Or launch the Speaker Design Studio directly:
 
```bash
python speaker_design.py
```
 
---
 
## Technical Notes
 
**Rendering architecture:**
 
The application detects OpenGL availability at runtime and selects the appropriate renderer:
 
- `SpeakerGLWidget` — PyQt5 `QGLWidget` subclass using legacy OpenGL (GL_QUADS, GL_TRIANGLE_FAN) for maximum compatibility across hardware
- `FallbackWidget` — Pure Qt `QPainter`-based 2D renderer implementing the same interface, enabling the app to run on any Python environment
Both renderers implement an identical interface (`set_shape`, `set_driver`, `set_color`, `set_enclosure`, etc.), making the UI layer fully renderer-agnostic.
 
**Enclosure geometry:**
 
The tapered enclosure profile approximates a trapezoidal cross-section (wider base, narrower top), which in real acoustic design reduces internal standing wave resonances by eliminating parallel wall pairs. This mirrors a real design technique used in high-end enclosure construction.
 
**Driver placement logic:**
 
Driver positions and sizes adjust dynamically based on active configuration — a single driver centers and scales up; two drivers split vertically; three drivers use fixed acoustic positions optimized for a standard 3-way layout. A constraint is enforced preventing the tweeter from being enabled without at least one low/mid driver, reflecting real crossover network requirements.
 
---
 
## Roadmap
 
- [ ] Tube amplifier design module
- [ ] Thiele-Small parameter input with enclosure volume calculator
- [ ] Frequency response estimation based on driver and enclosure parameters
- [ ] Export to DXF/SVG for CNC fabrication
- [ ] Crossover network designer with component value calculator
---
 
## About Maaleh
 
**Maaleh** is an independent audio electronics brand in development, focused on building high-fidelity speakers and DSP-driven amplification hardware from the ground up — spanning analog circuit design, embedded firmware, and digital signal processing. This tool is part of the internal R&D toolkit being developed alongside the brand.
 
---
 
## Author
 
Eduarda (Duda) [Last Name]  
Computer Engineering, Brigham Young University  
[your email] · [your LinkedIn] · [your GitHub]
