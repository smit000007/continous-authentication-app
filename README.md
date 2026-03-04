# continous-authentication-app 🛡️

**continous-authentication-app** is a continuous user authentication and workspace security system designed to protect your computer precisely when you step away—or if an unauthorized person tries to use it. 

Built with Python, **PyQt6**, **OpenCV**, and **dlib-based Face Recognition**, this application runs a lightweight background presence monitor. It continuously verifies the identity of the person sitting in front of the computer via the webcam. If the authorized user leaves the desk or an unknown face is detected, the app automatically locks the system to ensure maximum privacy and security.

## ✨ Key Features

- **Continuous Face Authentication**: Uses the webcam to continuously identify the user in real-time.
- **Auto-Lock Mechanism**: Instantly locks the computer screen when the authorized user is absent or an unauthorized person is detected.
- **High-Performance & Lag-Free GUI**: Specifically architected using Multiprocessing and PyQt6 `QPainter`. Artificial Intelligence (AI) and UI workloads are structurally separated to ensure up to 60 FPS vision processing and video playback without stuttering.
- **Guided Face Enrollment**: Provides a sophisticated registration setup that captures various facial angles to guarantee top-tier robust recognition under different lighting and positions.
- **"Cyber Security" Themed UI**: Features a sleek, modern, and dark aesthetic suitable for security applications.
- **Efficient Resource Management**: Intelligent pausing and threading to ensure minimal CPU usage when the user is authenticated and active.

## 🛠️ Technology Stack

- **Python 3.x**
- **PyQt6**: For the graphical user interface.
- **OpenCV (`opencv-python`)**: For capturing and processing real-time video feeds.
- **Face Recognition (`face-recognition`, `dlib`)**: For state-of-the-art, deep-learning-based face detection and facial feature encoding.
- **NumPy**: For matrix operations and image data manipulation.

## 🗂️ Project Architecture

The project has been refactored for professional scalability, separating concerns effectively:
- `core/`: Contains the central multiprocessing operations, presence monitoring logic ([presence_monitor.py], and background workers ([vision_worker.py]
- `vision/`: Houses the webcam interaction ([camera.py] and AI recognition logic
- `ui/`: Contains all PyQt6 GUI components, including the main dashboard, registration flows, warning frames, and the custom QSS stylesheets.
- `system/`: Holds platform-specific commands, such as triggering the Windows `.dll` lock screen command.

# how to run:
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate


python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt

python main.py

