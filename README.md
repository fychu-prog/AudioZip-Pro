# 錄音縮小大師 Pro (Audio Shrinker Pro)

一個專為 **語音轉文字 (AI STT)** 與 **會議記錄** 設計的輕量級音訊壓縮工具。
能將龐大的錄音檔體積縮小 **90% 以上**，同時保留適合 AI 辨識的高清晰度人聲。

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ 主要功能

*   **極致壓縮**：將 500MB 的 WAV 錄音檔壓縮至 30MB 以下的 MP3，方便上傳與分享。
*   **AI 辨識最佳化**：預設參數 (64k-96k Bitrate) 專為 Whisper、Google STT 等 AI 模型調校，確保高辨識率。
*   **批次處理**：一次選取多個錄音檔，自動排程轉換。
*   **跨平台支援**：支援 macOS 與 Windows，自動偵測系統環境。
*   **Metadata 保留**：自動保留原始錄音的標籤資訊（如標題、演出者）。
*   **安全轉檔**：內建防呆機制與錯誤偵測，避免轉檔失敗或檔案損毀。

## 🚀 快速開始 (macOS App)

1.  前往 `dist` 資料夾。
2.  找到 `AudioShrinkerPro.app`。
3.  **首次開啟**：請按住 `Control` 鍵並點擊 App 圖示，選擇「打開」以繞過安全檢查。
4.  拖曳或選取您的錄音檔，調整品質滑桿，點擊「開始批次轉檔」。

## 🛠️ 開發與安裝

如果您想自行修改程式碼或在其他平台執行：

### 1. 安裝依賴
```bash
pip install -r requirements.txt
# 或手動安裝：
pip install customtkinter pydub
```

### 2. 安裝 FFmpeg (必要)
本工具依賴 FFmpeg 進行音訊處理。

*   **macOS (Homebrew)**:
    ```bash
    brew install ffmpeg
    ```
*   **Windows**:
    請下載 FFmpeg 並將 `bin` 資料夾加入系統環境變數 PATH 中。

### 3. 執行程式
```bash
python audio_shrinker_ui.py
```

### 4. 打包成 App (macOS)
```bash
pip install pyinstaller
pyinstaller --name "AudioShrinkerPro" --onefile --windowed --add-data "$(python3 -c 'import customtkinter; print(customtkinter.__path__[0])'):customtkinter/" audio_shrinker_ui.py
```

## 🎚️ 壓縮品質建議

| Bitrate | 用途建議 | 一小時檔案大小 |
| :--- | :--- | :--- |
| **32 kbps** | 僅供紀錄，檔案極小 (有機械音) | ~14 MB |
| **64 kbps** | **AI 辨識首選** (人聲清晰，極省空間) | **~28 MB** |
| **96 kbps** | **通用推薦** (AI 與聽感平衡) | **~43 MB** |
| **128 kbps**| 標準音質 (適合一般音樂或廣播) | ~57 MB |

## 📝 授權
MIT License
