<<<<<<< HEAD
# Continuous Authentication Using Face Presence 🛡️

A next-generation biometric security application designed to protect workstations by continuously verifying the user's presence. Unlike traditional "login-once" systems, this application runs a **Continuous Authentication Loop** at 60 FPS, ensuring that the system automatically locks the moment the authorized user steps away or an unauthorized person sits down.

## ✨ Key Features

- **Continuous Loop Authentication**: Constantly monitors face presence, identity, and authorization. 
- **Lightning-Fast Engine (60 FPS)**: Built using an advanced Split-Process Architecture (Multiprocessing) to bypass Python's Global Interpreter Lock (GIL). 
  - *Process 1* handles the UI & Camera for a silky smooth 60 FPS video feed.
  - *Process 2* handles heavy AI Face Recognition independently in the background.
- **"Zero-Copy" Video Pipeline**: Ultra-low latency camera rendering (~1ms) by avoiding expensive memory-copy operations.
- **3D-Like Guided Enrollment**: Solves the "half-face" detection issue with a 5-step interactive wizard (Front, Left, Right, Up, Down) to capture a robust biometric profile.
- **Uncapped Motion Tracking**: Evaluates up to 30-60 scans per second, allowing it to track faces instantly even during fast head movements.
- **Full-Resolution Analysis**: Processes raw 640x480 images without downscaling, allowing it to accurately detect distant or partial faces.

## 🚀 How It Works

1. **Enrollment**: The system registers authorized users by capturing their face from multiple angles to create a robust 3D-like profile.
2. **Monitoring**: Once active, the application constantly scans the camera feed in the background.
3. **Action**:
   - **Green Box (Verified)**: System remains unlocked.
   - **Red Box / No Face**: Triggers a warning timer. If an authorized face is not detected within the timeout window, the workstation automatically locks.

## 🛠️ Built With
- **Python 3**
- **OpenCV** (Computer Vision & Camera input)
- **face_recognition** (State-of-the-Art Dlib facial recognition)
- **PyQt6** (Modern, thread-safe UI)
- **Multiprocessing** (True parallel execution)

## 📦 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/continuous-authentication.git
   cd continuous-authentication
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: `face_recognition` requires `dlib`, which may require a C++ compiler like Visual Studio build tools on Windows).*

3. **Run the Application:**
   ```bash
   python main.py
   ```

## 🔮 Future Roadmap
- **Spy Mode / System Tray:** Silent background operation.
- **Shoulder Surfing Protection:** Instant screen-blurring when an intruder looks over your shoulder.
- **Liveness Detection (Anti-Spoofing):** Require a blink or smile to prove physical presence.

---
*Created as a high-performance continuous security prototype for modern workstations.*
=======
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

>>>>>>> f7bc179ea1e2b4de98651ad468dfdd3c13716306
