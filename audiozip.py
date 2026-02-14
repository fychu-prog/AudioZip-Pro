import os
import sys
import threading
import subprocess
import shutil
import locale
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pydub import AudioSegment
from pydub.utils import mediainfo
from PIL import Image

# 修正 macOS 打包後的 PATH 問題
os.environ["PATH"] += os.pathsep + "/usr/local/bin" + os.pathsep + "/opt/homebrew/bin" + os.pathsep + "/usr/bin"

# 初始化主題
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class AudioZipApp(ctk.CTk):
    TRANSLATIONS = {
        "en": {
            "app_title": "AudioZip Pro",
            "header_title": "Batch Audio Compressor",
            "btn_select": "Add Files (Multi-select)",
            "lbl_out": "Destination:",
            "radio_source": "Original Folder",
            "radio_custom": "Select Folder...",
            "lbl_custom_none": "(Not Selected)",
            "lbl_custom_prefix": "Save to: ",
            "bitrate_label": "Target Quality:",
            "stats_initial": "0 files selected | Total: 0 MB",
            "stats_format": "{} files selected | Total: {:.2f} MB",
            "pred_label": "Est. Output: -- MB",
            "pred_format": "Est. Output: ~ {:.2f} MB",
            "btn_run": "Start Conversion",
            "btn_cancel": "Cancel",
            "status_ready": "Ready",
            "status_analyzing": "Analyzing files...",
            "status_done_analysis": "Analysis Complete",
            "status_converting": "Processing ({}/{}): {}",
            "status_cancelling": "Cancelling...",
            "status_cancelled": "⚠️ Operation Cancelled ({}/{})",
            "status_completed_errors": "⚠️ Completed with errors (Success: {}, Failed: {})",
            "status_success": "✅ All Tasks Completed!",
            "msg_output_dir": "Please select an output folder",
            "msg_error_title": "Error",
            "msg_warning_title": "Warning",
            "msg_success_title": "Success",
            "msg_success_body": "Successfully converted {} files!",
            "msg_ffmpeg_missing": "FFmpeg not found! Please install it to continue.",
            "file_duration": "{:.1f} min",
            "file_size": "{:.1f} MB",
            "hints": {
                "32": "Voice Memo (Tiny size, low quality)",
                "64": "Space Saving (Clear vocals, AI-ready)",
                "96": "Best Balance (Recommended for general use)",
                "128": "High Quality (Standard audio)",
                "192": "Ultra Quality (Good for music)",
                "320": "Archive Quality (Lossless-like)"
            }
        },
        "zh_TW": {
            "app_title": "AudioZip Pro (錄音縮小大師)",
            "header_title": "音訊批次壓縮工具",
            "btn_select": "加入檔案 (可多選)",
            "lbl_out": "儲存位置：",
            "radio_source": "原資料夾",
            "radio_custom": "指定資料夾...",
            "lbl_custom_none": "(未選擇)",
            "lbl_custom_prefix": "儲存至：",
            "bitrate_label": "目標品質：",
            "stats_initial": "已選 0 個檔案 | 總大小：0 MB",
            "stats_format": "已選 {} 個檔案 | 總大小：{:.2f} MB",
            "pred_label": "預估總產出：-- MB",
            "pred_format": "預估總產出：約 {:.2f} MB",
            "btn_run": "開始批次轉檔",
            "btn_cancel": "取消",
            "status_ready": "準備就緒",
            "status_analyzing": "正在分析檔案...",
            "status_done_analysis": "分析完成",
            "status_converting": "正在處理 ({}/{}): {}",
            "status_cancelling": "正在取消中...",
            "status_cancelled": "⚠️ 操作已取消 (完成 {}/{})",
            "status_completed_errors": "⚠️ 完成但有錯誤 (成功：{}, 失敗：{})",
            "status_success": "✅ 全部完成！",
            "msg_output_dir": "請選擇輸出資料夾",
            "msg_error_title": "錯誤",
            "msg_warning_title": "警告",
            "msg_success_title": "成功",
            "msg_success_body": "成功轉換所有 {} 個檔案！",
            "msg_ffmpeg_missing": "找不到 FFmpeg！請安裝後再使用。",
            "file_duration": "{:.1f} 分鐘",
            "file_size": "{:.1f} MB",
            "hints": {
                "32": "語音紀錄 (檔案極小，音質較低)",
                "64": "節省空間首選 (適合 AI 辨識，人聲清晰)",
                "96": "最佳平衡 (推薦：聽感與辨識兼具)",
                "128": "標準高品質 (與原音接近)",
                "192": "高保真 (適合含背景音樂需求)",
                "320": "無損等級 (適合專業收藏)"
            }
        },
        "ja": {
            "app_title": "AudioZip Pro",
            "header_title": "音声一括圧縮ツール",
            "btn_select": "ファイルを追加 (複数選択可)",
            "lbl_out": "保存場所:",
            "radio_source": "元のフォルダ",
            "radio_custom": "フォルダを選択...",
            "lbl_custom_none": "(未選択)",
            "lbl_custom_prefix": "保存先: ",
            "bitrate_label": "目標品質:",
            "stats_initial": "選択済み: 0 | 合計: 0 MB",
            "stats_format": "選択済み: {} | 合計: {:.2f} MB",
            "pred_label": "推定出力: -- MB",
            "pred_format": "推定出力: 約 {:.2f} MB",
            "btn_run": "変換を開始",
            "btn_cancel": "キャンセル",
            "status_ready": "準備完了",
            "status_analyzing": "解析中...",
            "status_done_analysis": "解析完了",
            "status_converting": "処理中 ({}/{}): {}",
            "status_cancelling": "キャンセル中...",
            "status_cancelled": "⚠️ 中断されました ({}/{})",
            "status_completed_errors": "⚠️ 完了（一部エラーあり） (成功: {}, 失敗: {})",
            "status_success": "✅ すべて完了しました！",
            "msg_output_dir": "出力フォルダを選択してください",
            "msg_error_title": "エラー",
            "msg_warning_title": "警告",
            "msg_success_title": "成功",
            "msg_success_body": "{} 個のファイルの変換が完了しました！",
            "msg_ffmpeg_missing": "FFmpeg が見つかりません。インストールしてから再試行してください。",
            "file_duration": "{:.1f} 分",
            "file_size": "{:.1f} MB",
            "hints": {
                "32": "記録・メモ用 (最小サイズ、音質は低い)",
                "64": "容量優先 (文字起こし・AI認識に最適)",
                "96": "バランス重視 (おすすめ：AI・リスニング両用)",
                "128": "標準的な高音質 (一般利用に最適)",
                "192": "高音質 (音楽やBGMを含む場合に推奨)",
                "320": "最高音質 (アーカイブ・保存用)"
            }
        },
        "es": {
            "app_title": "AudioZip Pro",
            "header_title": "Compresor de audio",
            "btn_select": "Añadir archivos",
            "lbl_out": "Destino:",
            "radio_source": "Carpeta de origen",
            "radio_custom": "Elegir carpeta...",
            "lbl_custom_none": "(No seleccionado)",
            "lbl_custom_prefix": "Guardar en: ",
            "bitrate_label": "Calidad:",
            "stats_initial": "0 archivos seleccionados | 0 MB",
            "stats_format": "{} archivos seleccionados | {:.2f} MB",
            "pred_label": "Salida est.: -- MB",
            "pred_format": "Salida est.: ~{:.2f} MB",
            "btn_run": "Iniciar conversión",
            "btn_cancel": "Cancelar",
            "status_ready": "Listo",
            "status_analyzing": "Analizando archivos...",
            "status_done_analysis": "Análisis completo",
            "status_converting": "Procesando ({}/{}): {}",
            "status_cancelling": "Cancelando...",
            "status_cancelled": "⚠️ Operación cancelada ({}/{})",
            "status_completed_errors": "⚠️ Finalizado con errores (Éxito: {}, Error: {})",
            "status_success": "✅ ¡Todo completado con éxito!",
            "msg_output_dir": "Seleccione una carpeta de salida",
            "msg_error_title": "Error",
            "msg_warning_title": "Advertencia",
            "msg_success_title": "Éxito",
            "msg_success_body": "¡{} archivos convertidos con éxito!",
            "msg_ffmpeg_missing": "No se encontró FFmpeg. Por favor, instálelo.",
            "file_duration": "{:.1f} min",
            "file_size": "{:.1f} MB",
            "hints": {
                "32": "Notas de voz (Tamaño mínimo)",
                "64": "Ahorro de espacio (Voz clara, para IA)",
                "96": "Balance ideal (Recomendado)",
                "128": "Calidad estándar",
                "192": "Alta fidelidad (Para música)",
                "320": "Máxima calidad (Sin pérdida)"
            }
        }
    }

    def __init__(self):
        super().__init__()

        # Detect System Language
        sys_lang = locale.getdefaultlocale()[0]
        if sys_lang and "zh" in sys_lang.lower(): self.current_lang = "zh_TW"
        elif sys_lang and "ja" in sys_lang.lower(): self.current_lang = "ja"
        elif sys_lang and "es" in sys_lang.lower(): self.current_lang = "es"
        else: self.current_lang = "en"

        self.geometry("520x640")
        
        # Try to set icon
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "appicon.png")
            if os.path.exists(icon_path):
                self.icon_image = Image.open(icon_path)
                self.after(200, lambda: self.wm_iconphoto(True, ctk.CTkImage(light_image=self.icon_image, dark_image=self.icon_image)._light_image))
        except:
            pass
        
        # Fonts
        self.font_large = ctk.CTkFont(size=18, weight="bold")
        self.font_normal = ctk.CTkFont(size=13)
        self.font_small = ctk.CTkFont(size=11)
        self.font_tiny = ctk.CTkFont(size=10)

        # 檢查 ffmpeg
        if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
            messagebox.showerror(self.t("msg_error_title"), self.t("msg_ffmpeg_missing"))

        self.files = []
        self.total_size_mb = 0.0
        self.total_duration_secs = 0.0
        self.target_bitrate = 96
        self.output_mode = ctk.StringVar(value="source")
        self.custom_output_dir = ""
        self.stop_event = threading.Event()
        self.is_converting = False
        
        self.setup_ui()
        self.update_ui_text()

    def t(self, key):
        return self.TRANSLATIONS[self.current_lang].get(key, key)

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Top Bar
        self.frame_top = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_top.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        self.frame_top.grid_columnconfigure(0, weight=1)
        self.label_title = ctk.CTkLabel(self.frame_top, text="", font=self.font_large)
        self.label_title.grid(row=0, column=0, sticky="w")
        
        self.lang_map = {"English": "en", "繁體中文": "zh_TW", "日本語": "ja", "Español": "es"}
        self.lang_var = ctk.StringVar(value=[k for k, v in self.lang_map.items() if v == self.current_lang][0])
        self.option_lang = ctk.CTkOptionMenu(self.frame_top, values=list(self.lang_map.keys()), 
                                             command=self.change_language, variable=self.lang_var, 
                                             width=110, font=self.font_small)
        self.option_lang.grid(row=0, column=1, sticky="e")

        # File List
        self.frame_files = ctk.CTkScrollableFrame(self, label_text="Files")
        self.frame_files.grid(row=1, column=0, padx=10, pady=(5,5), sticky="nsew")
        self.frame_files.grid_columnconfigure(0, weight=1)
        
        # Settings
        self.frame_settings = ctk.CTkFrame(self)
        self.frame_settings.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.frame_settings.grid_columnconfigure(1, weight=1)
        
        self.btn_select = ctk.CTkButton(self.frame_settings, text="", command=self.select_files, font=self.font_normal)
        self.btn_select.grid(row=0, column=0, columnspan=3, padx=5, pady=(5, 2), sticky="ew")

        self.lbl_out = ctk.CTkLabel(self.frame_settings, text="", font=self.font_normal)
        self.lbl_out.grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.radio_source = ctk.CTkRadioButton(self.frame_settings, text="", variable=self.output_mode, value="source", font=self.font_small)
        self.radio_source.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        self.radio_custom = ctk.CTkRadioButton(self.frame_settings, text="", variable=self.output_mode, value="custom", command=self.choose_output_dir, font=self.font_small)
        self.radio_custom.grid(row=1, column=2, padx=5, pady=2, sticky="w")
        self.lbl_custom_path = ctk.CTkLabel(self.frame_settings, text="", text_color="gray", font=self.font_tiny)
        self.lbl_custom_path.grid(row=2, column=0, columnspan=3, padx=5, pady=(0, 5), sticky="w")

        self.label_bitrate = ctk.CTkLabel(self.frame_settings, text="", font=self.font_normal)
        self.label_bitrate.grid(row=3, column=0, columnspan=3, padx=5, pady=(5, 0))
        self.slider = ctk.CTkSlider(self.frame_settings, from_=32, to=320, number_of_steps=9, command=self.on_slider_change)
        self.slider.set(self.target_bitrate)
        self.slider.grid(row=4, column=0, columnspan=3, padx=5, pady=2, sticky="ew")
        self.label_hint = ctk.CTkLabel(self.frame_settings, text="", text_color="#666666", font=self.font_small)
        self.label_hint.grid(row=5, column=0, columnspan=3, padx=5, pady=(0, 5))

        # Bottom Frame
        self.frame_bottom = ctk.CTkFrame(self)
        self.frame_bottom.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        self.frame_bottom.grid_columnconfigure(0, weight=1)
        self.frame_bottom.grid_columnconfigure(1, weight=1)

        self.label_stats = ctk.CTkLabel(self.frame_bottom, text="", font=self.font_small)
        self.label_stats.grid(row=0, column=0, pady=(2,2), padx=5, sticky="w")
        self.label_pred = ctk.CTkLabel(self.frame_bottom, text="", text_color="#1f538d", font=self.font_normal)
        self.label_pred.grid(row=0, column=1, pady=(2,2), padx=5, sticky="e")
        
        self.btn_run = ctk.CTkButton(self.frame_bottom, text="", command=self.start_conversion, fg_color="#2c6e49", hover_color="#1e462f", state="disabled", font=self.font_normal)
        self.btn_run.grid(row=1, column=0, padx=5, pady=(5, 2), sticky="ew")
        self.btn_cancel = ctk.CTkButton(self.frame_bottom, text="", command=self.cancel_conversion, fg_color="#c0392b", hover_color="#922b21", state="disabled", font=self.font_normal)
        self.btn_cancel.grid(row=1, column=1, padx=5, pady=(5, 2), sticky="ew")

        # Progress
        self.progress = ctk.CTkProgressBar(self, height=6)
        self.progress.set(0)
        self.progress.grid(row=4, column=0, padx=10, pady=(0,2), sticky="ew")
        self.label_status = ctk.CTkLabel(self, text="", font=self.font_tiny)
        self.label_status.grid(row=5, column=0, padx=10, pady=0, sticky="w")

    def change_language(self, selection):
        self.current_lang = self.lang_map.get(selection, "en")
        self.update_ui_text()

    def update_ui_text(self):
        self.title(self.t("app_title"))
        self.label_title.configure(text=self.t("app_title"))
        self.btn_select.configure(text=self.t("btn_select"))
        self.lbl_out.configure(text=self.t("lbl_out"))
        self.radio_source.configure(text=self.t("radio_source"))
        self.radio_custom.configure(text=self.t("radio_custom"))
        
        if not self.custom_output_dir:
            self.lbl_custom_path.configure(text=self.t("lbl_custom_none"))
        else:
            self.lbl_custom_path.configure(text=f"{self.t('lbl_custom_prefix')}{self.custom_output_dir}")

        self.label_bitrate.configure(text=f"{self.t('bitrate_label')} {self.target_bitrate} kbps")
        self.update_hint(self.target_bitrate)
        
        if not self.files:
            self.label_stats.configure(text=self.t("stats_initial"))
        else:
            self.label_stats.configure(text=self.t("stats_format").format(len(self.files), self.total_size_mb))
            
        self.update_prediction()
        self.btn_run.configure(text=self.t("btn_run"))
        self.btn_cancel.configure(text=self.t("btn_cancel"))
        
        if not self.is_converting and "..." not in self.label_status.cget("text"):
             self.label_status.configure(text=self.t("status_ready"))
        
        self.frame_files.configure(label_text=self.t("header_title"))

    def choose_output_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.custom_output_dir = path
            self.output_mode.set("custom")
            self.lbl_custom_path.configure(text=f"{self.t('lbl_custom_prefix')}{path}")
        else:
            if self.output_mode.get() == "custom" and not self.custom_output_dir:
                 self.output_mode.set("source")

    def select_files(self):
        paths = filedialog.askopenfilenames(filetypes=[("Audio Files", "*.wav *.m4a *.mp3 *.aiff *.flac *.ogg")])
        if not paths: return
        self.btn_select.configure(state="disabled")
        self.btn_run.configure(state="disabled")
        self.label_status.configure(text=self.t("status_analyzing"))
        threading.Thread(target=self._analyze_files_thread, args=(paths,), daemon=True).start()

    def _analyze_files_thread(self, paths):
        new_files, errors = [], []
        for path in paths:
            if any(f['path'] == path for f in self.files): continue
            try:
                size_mb = os.path.getsize(path) / (1024 * 1024)
                info = mediainfo(path)
                duration = float(info.get('duration', 0))
                tags = info.get('TAG', {})
                if not tags: tags = {k: v for k, v in info.items() if k in ['artist', 'title', 'album']}
                if duration == 0: duration = len(AudioSegment.from_file(path)) / 1000.0
                new_files.append({'path': path, 'size_mb': size_mb, 'duration': duration, 'tags': tags})
            except Exception as e:
                errors.append(f"{os.path.basename(path)}: {str(e)}")
        self.files.extend(new_files)
        self.after(0, lambda: self._update_ui_after_analysis(errors))

    def _update_ui_after_analysis(self, errors):
        for widget in self.frame_files.winfo_children(): widget.destroy()
        self.total_size_mb = 0
        self.total_duration_secs = 0
        
        for i, f in enumerate(self.files):
            self.total_size_mb += f['size_mb']
            self.total_duration_secs += f['duration']
            file_frame = ctk.CTkFrame(self.frame_files, fg_color=("gray90", "gray20"))
            file_frame.grid(row=i, column=0, padx=5, pady=2, sticky="ew")
            file_frame.grid_columnconfigure(0, weight=1)

            name = os.path.basename(f['path'])
            duration_min = f['duration'] / 60.0
            label_name = ctk.CTkLabel(file_frame, text=f"{i+1}. {name}", font=self.font_small, anchor="w")
            label_name.grid(row=0, column=0, padx=5, pady=2, sticky="w")
            
            label_details = ctk.CTkLabel(file_frame, 
                                         text=f"{self.t('file_duration').format(duration_min)} | {self.t('file_size').format(f['size_mb'])}", 
                                         font=self.font_tiny, text_color="gray", anchor="e")
            label_details.grid(row=0, column=1, padx=5, pady=2, sticky="e")

        self.label_stats.configure(text=self.t("stats_format").format(len(self.files), self.total_size_mb))
        self.update_prediction()
        
        if errors:
            err_msg = "\n".join(errors[:5])
            messagebox.showwarning(self.t("msg_warning_title"), f"Errors:\n{err_msg}")

        self.label_status.configure(text=self.t("status_done_analysis"))
        self.btn_select.configure(state="normal")
        self.btn_run.configure(state="normal" if self.files else "disabled")

    def on_slider_change(self, value):
        self.target_bitrate = int(value)
        self.label_bitrate.configure(text=f"{self.t('bitrate_label')} {self.target_bitrate} kbps")
        self.update_hint(self.target_bitrate)
        self.update_prediction()

    def update_hint(self, bitrate):
        hints = self.t("hints")
        key = "32"
        if bitrate <= 48: key = "32"
        elif bitrate <= 64: key = "64"
        elif bitrate <= 96: key = "96"
        elif bitrate <= 128: key = "128"
        elif bitrate <= 192: key = "192"
        else: key = "320"
        self.label_hint.configure(text=f"{hints.get(key, '')}")

    def update_prediction(self):
        if self.total_duration_secs > 0:
            est_mb = (self.target_bitrate * self.total_duration_secs) / 8192
            self.label_pred.configure(text=self.t("pred_format").format(est_mb))
        else:
             self.label_pred.configure(text=self.t("pred_label"))

    def cancel_conversion(self):
        if self.is_converting:
            self.stop_event.set()
            self.label_status.configure(text=self.t("status_cancelling"))
            self.btn_cancel.configure(state="disabled")

    def start_conversion(self):
        if not self.files: return
        if self.output_mode.get() == "custom" and not self.custom_output_dir:
            messagebox.showwarning(self.t("msg_warning_title"), self.t("msg_output_dir"))
            return

        self.is_converting = True
        self.stop_event.clear()
        self.btn_run.configure(state="disabled")
        self.btn_select.configure(state="disabled")
        self.btn_cancel.configure(state="normal")
        self.slider.configure(state="disabled")
        self.radio_source.configure(state="disabled")
        self.radio_custom.configure(state="disabled")
        self.progress.set(0)
        threading.Thread(target=self._batch_convert_thread, daemon=True).start()

    def _batch_convert_thread(self):
        total_files, success_count, error_count, errors = len(self.files), 0, 0, []
        for i, file_data in enumerate(self.files):
            if self.stop_event.is_set(): break
            path, filename = file_data['path'], os.path.basename(file_data['path'])
            self.after(0, lambda p=i/total_files, t=self.t("status_converting").format(i+1, total_files, filename): (
                self.progress.set(p), self.label_status.configure(text=t)
            ))
            try:
                out_dir = self.custom_output_dir if self.output_mode.get() == "custom" else os.path.dirname(path)
                save_path = os.path.join(out_dir, f"{os.path.splitext(filename)[0]}_sm.mp3")
                audio = AudioSegment.from_file(path)
                audio.export(save_path, format="mp3", bitrate=f"{self.target_bitrate}k", tags=file_data['tags'])
                success_count += 1
            except Exception as e:
                errors.append(f"{filename}: {str(e)}")
                error_count += 1
        self.is_converting = False
        self.after(0, lambda: self._conversion_finished(success_count, error_count, total_files, errors))

    def _conversion_finished(self, success, errors_count, total, error_list):
        self.progress.set(1.0)
        if self.stop_event.is_set(): status_text = self.t("status_cancelled").format(success, total)
        elif errors_count > 0:
            status_text = self.t("status_completed_errors").format(success, errors_count)
            messagebox.showwarning(self.t("msg_warning_title"), f"Errors:\n{error_list[0]}")
        else:
            status_text = self.t("status_success")
            messagebox.showinfo(self.t("msg_success_title"), self.t("msg_success_body").format(success))

        self.label_status.configure(text=status_text)
        self.btn_run.configure(state="normal"); self.btn_select.configure(state="normal")
        self.btn_cancel.configure(state="disabled"); self.slider.configure(state="normal")
        self.radio_source.configure(state="normal"); self.radio_custom.configure(state="normal")
        if success > 0:
            out_dir = self.custom_output_dir if self.output_mode.get() == "custom" else os.path.dirname(self.files[-1]['path'])
            self._open_file_in_explorer(out_dir)

    def _open_file_in_explorer(self, path):
        try:
            if sys.platform == 'darwin': subprocess.run(['open', path])
            elif sys.platform == 'win32': os.startfile(path)
            else: subprocess.run(['xdg-open', path])
        except Exception: pass

if __name__ == "__main__":
    app = AudioZipApp()
    app.mainloop()
