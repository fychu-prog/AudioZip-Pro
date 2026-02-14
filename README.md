# AudioZip Pro 🎧

[English](#english) | [繁體中文](#繁體中文)

---

<a name="english"></a>
## English

AudioZip Pro is a lightweight and powerful batch audio compression tool. Designed for users who need to quickly compress large volumes of recordings (class lectures, meeting notes, interviews, etc.). You can significantly reduce file sizes while maintaining optimal quality for listening or AI transcription.

![Preview](preview_screenshot.png)

### ✨ Key Features
- **Batch Processing:** Add multiple files and convert them all at once.
- **Smart Estimation:** Real-time calculation of estimated output file sizes.
- **Multi-language Support:** Interface available in **English, Traditional Chinese, Japanese, and Spanish**.
- **Quality Control:** Precise bitrate adjustment from 32kbps to 320kbps with professional hints.
- **Cross-platform:** Compatible with both macOS and Windows.

### 🚀 Quick Start

#### 1. Install Dependency (FFmpeg)
The core engine requires **FFmpeg**. Please install it based on your OS:
- **macOS:** `brew install ffmpeg`
- **Windows:** Download from [FFmpeg.org](https://ffmpeg.org/download.html), and add the `bin` folder to your System PATH.

#### 2. Install Python Libraries
```bash
pip install -r requirements.txt
```

#### 3. Run Application
```bash
python audiozip.py
```

---

<a name="繁體中文"></a>
## 繁體中文

AudioZip Pro 是一款輕量級且強大的音訊批次壓縮工具。專為需要快速、大量壓縮錄音檔（如課堂錄音、會議記錄、訪談等）的使用者設計。透過智慧壓縮算法，您可以大幅縮小音訊體積，同時保持適合聽感或 AI 逐字稿辨識的音質。

### ✨ 主要特色
- **批次處理：** 一次加入多個檔案，一鍵完成轉換。
- **智慧預估：** 即時計算壓縮後的預估檔案總大小。
- **多語支援：** 提供 **繁體中文、English、日本語、Español** 介面。
- **品質調整：** 支援 32kbps 到 320kbps 的細膩調整，並附有專業情境提示。
- **跨平台支援：** 完美相容 macOS 與 Windows。

### 🚀 快速開始

#### 1. 安裝必要組件 (FFmpeg)
本工具的核心功能依賴於 **FFmpeg**。請根據您的作業系統安裝：
- **macOS:** `brew install ffmpeg`
- **Windows:** 請至 [FFmpeg 官網](https://ffmpeg.org/download.html) 下載預編譯檔，並將 `bin` 資料夾路徑加入系統環境變數 `PATH` 中。

#### 2. 安裝 Python 函式庫
```bash
pip install -r requirements.txt
```

#### 3. 執行程式
```bash
python audiozip.py
```

## 🛠 Quality Hints / 品質建議
- **64 kbps:** Space Saving (Space saver, clear vocals for AI) / 節省空間首選。
- **96 kbps:** **Best Balance (Recommended)** / 最佳平衡（推薦：聽感與辨識兼具）。
- **128 kbps:** High Quality (Standard audio) / 標準高品質。

## ⚖️ License / 授權條款
This project is licensed under the [MIT License](LICENSE).

---
*Developed with ❤️ for efficient audio management.*
