<div align="center">

# 🚀 Gesture-Based Intelligent AI Assistant (GBIAS)

**An AI assistant that interprets real-time hand gestures and user intent to control your PC.**

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.33-0097A7?style=flat)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-API-8E44AD?style=flat)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 📖 Overview

**Gesture-Based Intelligent AI Assistant (GBIAS)** is an intelligent, hands-free computer interaction system. By combining computer vision with LLM-powered context awareness, GBIAS tracks hand gestures in real time using MediaPipe and proactively interprets user intent using Google Gemini.

Rather than relying solely on static, one-to-one gesture mappings, GBIAS records gesture patterns, session context, and frequency. A passive AI Intent Engine queries Google Gemini in the background to infer user needs (e.g., auto-pausing media, adjusting volume, or suggesting breaks) and dynamically dispatches native PC automation commands.

## ✨ Features

- **Real-Time Hand Tracking & Gesture Recognition** — Utilizes MediaPipe Hand Landmarker and OpenCV to detect left/right hand landmarks and classify hand gestures with high precision.
- **AI-Powered Passive Intent Engine** — A background inference loop periodically sends gesture snapshots, active profiles, time-of-day, and gesture frequency to Google Gemini (`gemini-flash-latest`) to predict intent and trigger automated actions.
- **Dynamic Profile Management** — Supports profile switching (`PC`, `Lights`, `Zen`, `Music`) to dynamically remap hand gestures to context-specific operations.
- **Native PC Control** — Automates computer interactions via `pyautogui`, controlling media playback (play/pause, next/previous track) and system volume (mute, volume up/down).
- **Interactive Visual HUD** — Displays landmarker skeletons, gesture hold progress bars, profile indicators, active status, and real-time LLM intent predictions directly on the video feed.
- **System Gesture Overrides** — Dedicated gesture shortcuts for pausing/resuming tracking (`SPIDERMAN`), switching profiles (`PROFILE_1`–`PROFILE_4`), and safely exiting (`QUIT`).

## 🛠️ Tech Stack

| Layer | Technology |
|:------|:-----------|
| **Language** | Python 3.9+ |
| **Computer Vision** | MediaPipe (`mediapipe`), OpenCV (`opencv-python`) |
| **AI / Intent Inference** | Google GenAI SDK (`google-genai`), Gemini API (`gemini-flash-latest`) |
| **PC Automation** | PyAutoGUI (`pyautogui`) |
| **Configuration & Utilities** | `python-dotenv`, `pydantic`, `numpy`, `matplotlib` |

## ⚡ Quick Start

### Prerequisites

- Python 3.9 or higher
- A connected webcam
- A Google Gemini API Key ([Obtain one from Google AI Studio](https://aistudio.google.com/))

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/gesture-based-intelligent-ai-assistant.git
   cd gesture-based-intelligent-ai-assistant
   ```

2. **Set up a virtual environment**:
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

1. **Configure Environment Variables**:
   Create a `.env` file in the project root with your Gemini API key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

2. **Run the Application**:

   **Using the Windows launcher batch file:**
   ```cmd
   run.bat
   ```

   **Or manually via Python:**
   ```bash
   python src/gesture/hand_detector.py
   ```

3. **Gesture Controls & Controls Summary**:
   - `SPIDERMAN` — Toggle Pause / Resume control system.
   - `PROFILE_1` to `PROFILE_4` — Switch active profile (PC, Lights, Zen, Music).
   - `OPEN_HAND` / `CLOSED_FIST` — Play/Pause or Mute based on active profile.
   - `THUMB_UP` / `THUMB_DOWN` — Volume Up / Volume Down (repeatable action).
   - `PREV_TRACK` / `NEXT_TRACK` — Previous or Next audio track.
   - `QUIT` (or press `Q` on keyboard) — Exit application.

## 📁 Project Structure

```
gesture-based-intelligent-ai-assistant/
├── .env
├── .gitignore
├── LICENSE
├── README.md
├── assets/
├── config/
│   └── settings.json
├── docs/
├── hand_landmarker.task
├── requirements.txt
├── run.bat
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── action_dispatcher.py
│   │   ├── intent_engine.py
│   │   ├── observation_logger.py
│   │   └── profile_manager.py
│   ├── gesture/
│   │   ├── __init__.py
│   │   ├── gesture_classifier.py
│   │   └── hand_detector.py
│   ├── hardware/
│   │   └── __init__.py
│   └── integrations/
│       ├── __init__.py
│       └── pc_controller.py
├── test.py
└── tests/
```

## 🔧 Configuration

- `.env`: Configures runtime environment variables, specifically `GEMINI_API_KEY`.
- `config/settings.json`: Settings configuration file for customizing default parameters.
- `hand_landmarker.task`: MediaPipe model file for hand landmark detection (automatically downloaded on first execution if not present).

## 🧪 Testing

To test the background intent inference thread and context logger without running the full webcam interface, run the test script:

```bash
python test.py
```

## 🤝 Contributing

Contributions are welcome! Follow these steps to contribute:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/NewFeature`).
3. Commit your changes (`git commit -m 'Add NewFeature'`).
4. Push to the branch (`git push origin feature/NewFeature`).
5. Open a Pull Request.

## 📄 License

This project is licensed under the [MIT License](LICENSE).