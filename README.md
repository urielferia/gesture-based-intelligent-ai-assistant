<div align="center">

# 🚀 Gesture-based Intelligent AI Assistant

**An AI assistant that interprets hand gestures and intent to perform actions and control your PC.**

![Python](https://img.shields.io/badge/Language-Python-blue.svg) ![License](https://img.shields.io/badge/License-See%20LICENSE%20file-blue.svg) ![Built With](https://img.shields.io/badge/Built%20With-MediaPipe%2C%20Gemini%20API-orange.svg)

</div>

---

## 📖 Overview

This project implements an intelligent AI assistant that utilizes real-time hand gesture recognition to understand user commands. It leverages MediaPipe for accurate hand tracking and Google Gemini for advanced intent recognition, enabling a natural and intuitive way to interact with your computer. The system processes gestures and inferred intent to dispatch specific actions, aiming to enhance productivity and accessibility.

## ✨ Features

-   **Real-time Gesture Recognition** — Detects and classifies various hand gestures using MediaPipe for precise input.
-   **AI-Powered Intent Engine** — Uses Google Gemini to interpret user intent from recognized gestures and contextual information.
-   **Dynamic Action Dispatching** — Executes predefined system actions based on both direct gesture commands and inferred intent (e.g., media control, volume adjustment).
-   **PC Integration** — Interacts with and controls various aspects of the computer system, such as multimedia playback or application control.
-   **Configurable Gestures** — Allows mapping specific gestures to system actions for personalized control.

## 🛠️ Tech Stack

| Layer | Technology |
|:------|:-----------|
| Language | Python |
| Computer Vision | MediaPipe, OpenCV |
| AI/LLM | Google Gemini API (via `httpx`, `anthropic`) |
| Data Validation | Pydantic |
| Environment Mgmt. | python-dotenv |
| Other | NumPy, Matplotlib |

## ⚡ Quick Start

### Prerequisites
-   Python 3.x (tested with versions compatible with `requirements.txt`)
-   A Google Gemini API Key
-   `pip` package manager

### Installation
```bash
# Clone the repository
git clone https://github.com/your-username/gesture-based-intelligent-ai-assistant.git # TODO: Update with actual repository URL
cd gesture-based-intelligent-ai-assistant

# Install dependencies
pip install -r requirements.txt
```

### Usage
1.  **Obtain a Gemini API Key**: Visit the Google AI Studio to get your API key.
2.  **Configure Environment**: Create a `.env` file in the project root and add your Gemini API key:
    ```
    GEMINI_API_KEY=YOUR_GEMINI_API_KEY
    ```
3.  **Run the application**:
    **Using the batch file (Windows):**
    Double-click `run.bat` or run:
    ```cmd
    run.bat
    ```

    **Or manually with Python:**
    ```bash
    python src/gesture/hand_detector.py
    ```
    The application should start detecting gestures and dispatching actions based on configuration.

## 📁 Project Structure

```
gesture-based-intelligent-ai-assistant/
├── .env
├── .gitignore
├── README.md
├── config/
│   └── settings.json
├── hand_landmarker.task
├── requirements.txt
└── src/
    ├── __init__.py
    ├── core/
    │   ├── __init__.py
    │   ├── action_dispatcher.py
    │   ├── intent_engine.py
    │   ├── observation_logger.py
    │   └── profile_manager.py
    ├── gesture/
    │   ├── __init__.py
    │   ├── gesture_classifier.py
    │   └── hand_detector.py
    ├── hardware/
    │   └── __init__.py
    └── integrations/
        ├── __init__.py
        └── pc_controller.py
```

## 🔧 Configuration

-   `.env`: This file is used to store sensitive information such as your `GEMINI_API_KEY`.
-   `config/settings.json`: This file is currently empty but is intended for future configuration settings of the application.

## 🤝 Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.

## 📄 License

See LICENSE file