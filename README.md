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
