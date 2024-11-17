Software Requirements:
- Python 3.12
- Camera: A webcam or external camera for capturing hand gestures.
- FreeCAD (latest version)
- Socket Server: A server script running on localhost to receive coordinates (e.g., integrated with FreeCAD).

Installation:
Clone repository into an IDE
Make sure you have 'pip' to install dependecies from the requirements.txt file
run: pip install -r requirements.txt

Run:
*Make sure server program (FreeCAD) is running BEFORE you run the gesture tracking program, otherwise the socket cannot connect
Run connection_test.py for interaction with FreeCAD environment
Run main.py for basic hand gesture recognition (no socket communication)
