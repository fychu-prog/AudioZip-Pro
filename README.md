# Audio Shrinker Pro

A lightweight, powerful audio compression tool designed for **AI Speech-to-Text (STT)** and **meeting recordings**.
Shrink massive audio files by **over 90%** while preserving high-clarity vocals optimized for AI transcription models like OpenAI Whisper.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Key Features

*   **Extreme Compression**: Compress 500MB WAV files to under 30MB MP3s, perfect for uploading and sharing.
*   **AI-Optimized**: Default bitrate settings (64k-96k) are tuned for AI models (Whisper, Google STT) to ensure high accuracy.
*   **Batch Processing**: Select multiple files and convert them automatically in a queue.
*   **Cross-Platform**: Supports macOS and Windows with automatic environment detection.
*   **Metadata Preservation**: Automatically keeps original tags (Artist, Title, Album, etc.).
*   **Robust & Safe**: Built-in error handling prevents crashes and ensures file integrity.
*   **Broad Format Support**: Supports MP3, M4A, WAV, FLAC, AIFF, OGG, and more.

## 🚀 Quick Start (macOS App)

1.  Navigate to the `dist` folder.
2.  Locate `AudioShrinkerPro.app`.
3.  **First Launch**: Right-click (or Control-click) the app icon and select "Open" to bypass security checks.
4.  Drag & drop or select your audio files, adjust the quality slider, and click "Start Batch Conversion".

## 🛠️ Development & Installation

If you want to modify the code or run it on other platforms:

### 1. Install Dependencies
```bash
pip install -r requirements.txt
# Or manually:
pip install customtkinter pydub
```

### 2. Install FFmpeg (Required)
This tool relies on FFmpeg for audio processing.

*   **macOS (Homebrew)**:
    ```bash
    brew install ffmpeg
    ```
*   **Windows**:
    Download FFmpeg and add the `bin` folder to your system PATH.

### 3. Run the Script
```bash
python audio_shrinker_ui.py
```

### 4. Build App (macOS)
```bash
pip install pyinstaller
pyinstaller --name "AudioShrinkerPro" --onefile --windowed --add-data "$(python3 -c 'import customtkinter; print(customtkinter.__path__[0])'):customtkinter/" audio_shrinker_ui.py
```

## 🎚️ Bitrate Guide

| Bitrate | Best For | 1 Hour File Size |
| :--- | :--- | :--- |
| **32 kbps** | Record only, smallest size (robotic voice) | ~14 MB |
| **64 kbps** | **Best for AI STT** (Clear vocals, tiny size) | **~28 MB** |
| **96 kbps** | **Recommended** (Balance of AI & listening) | **~43 MB** |
| **128 kbps**| Standard Quality (Music, Podcasts) | ~57 MB |

## 📝 License
MIT License