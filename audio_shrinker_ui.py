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

# 修正 macOS 打包後的 PATH 問題，確保能找到 ffmpeg
# 許多 macOS App 不會繼承 Shell 的 PATH，導致 pydub 找不到 ffmpeg
os.environ["PATH"] += os.pathsep + "/usr/local/bin" + os.pathsep + "/opt/homebrew/bin" + os.pathsep + "/usr/bin"

# 初始化主題
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class AudioShrinkerApp(ctk.CTk):
    TRANSLATIONS = {
        "en": {
            "app_title": "Audio Shrinker Pro (Batch)",
            "header_title": "Batch Audio Compressor",
            "btn_select": "Add Files (Multi-select)",
            "lbl_out": "Output:",
            "radio_source": "Same Folder",
            "radio_custom": "Custom Folder...",
            "lbl_custom_none": "(Not Selected)",
            "lbl_custom_prefix": "Save to: ",
            "bitrate_label": "Target Quality (Bitrate):",
            "stats_initial": "Selected 0 files | Total Size: 0 MB",
            "stats_format": "Selected {} files | Total Size: {:.2f} MB",
            "pred_label": "Est. Output: -- MB",
            "pred_format": "Est. Output: Approx {:.2f} MB",
            "btn_run": "Start Batch Conversion",
            "btn_cancel": "Cancel",
            "status_ready": "Ready",
            "status_analyzing": "Analyzing files...",
            "status_done_analysis": "Analysis Complete",
            "status_converting": "Processing ({}/{}): {}",
            "status_cancelling": "Cancelling... (Stops after current file)",
            "status_cancelled": "⚠️ Operation Cancelled (Completed {}/{})",
            "status_completed_errors": "⚠️ Completed with errors (Success: {}, Failed: {})",
            "status_success": "✅ All Completed!",
            "msg_output_dir": "Please select an output folder",
            "msg_error_title": "Error",
            "msg_warning_title": "Warning",
            "msg_success_title": "Success",
            "msg_success_body": "Successfully converted {} files!",
            "msg_ffmpeg_missing": "FFmpeg or FFprobe not found!\nPlease install FFmpeg (e.g., brew install ffmpeg).\nThe app may not work correctly.",
            "hints": {
                "32": "Record only (Tiny size, robotic voice)",
                "64": "Best for Space Saving (Clear vocals, AI-ready)",
                "96": "Best Balance (Recommended for AI & Listening)",
                "128": "Standard Quality (Good for general use)",
                "192": "High Fidelity (Good for music/background)",
                "320": "Lossless-like (Archival quality)"
            }
        },
        "zh_TW": {
            "app_title": "錄音縮小大師 Pro (批次版)",
            "header_title": "錄音檔批次壓縮工具",
            "btn_select": "加入檔案 (可多選)",
            "lbl_out": "輸出位置:",
            "radio_source": "原資料夾",
            "radio_custom": "指定資料夾...",
            "lbl_custom_none": "(未選擇)",
            "lbl_custom_prefix": "儲存至: ",
            "bitrate_label": "目標品質 (Bitrate):",
            "stats_initial": "已選 0 個檔案 | 總大小: 0 MB",
            "stats_format": "已選 {} 個檔案 | 總大小: {:.2f} MB",
            "pred_label": "預估總產出: -- MB",
            "pred_format": "預估總產出: 約 {:.2f} MB",
            "btn_run": "開始批次轉檔",
            "btn_cancel": "取消",
            "status_ready": "準備就緒",
            "status_analyzing": "正在分析檔案資訊...",
            "status_done_analysis": "分析完成",
            "status_converting": "正在處理 ({}/{}): {}",
            "status_cancelling": "正在取消中... (將在目前檔案完成後停止)",
            "status_cancelled": "⚠️ 操作已取消 (完成 {}/{})",
            "status_completed_errors": "⚠️ 完成但有錯誤 (成功: {}, 失敗: {})",
            "status_success": "✅ 全部完成！",
            "msg_output_dir": "請選擇輸出資料夾",
            "msg_error_title": "錯誤",
            "msg_warning_title": "部分檔案讀取失敗",
            "msg_success_title": "成功",
            "msg_success_body": "成功轉換所有 {} 個檔案！",
            "msg_ffmpeg_missing": "找不到 ffmpeg 或 ffprobe！\n請確保已安裝 ffmpeg (例如透過 brew install ffmpeg)。\n程式可能無法正常運作。",
            "hints": {
                "32": "僅供紀錄 (檔案極小，有機械音)",
                "64": "節省空間首選 (適合 AI 辨識，人聲清晰)",
                "96": "AI 辨識最佳平衡 (推薦：檔案小且保留細節)",
                "128": "標準高品質 (與原音接近，適合一般聽感)",
                "192": "高保真 (音質優異，適合含背景音樂需求)",
                "320": "無損等級 (檔案較大，適合收藏或專業需求)"
            }
        }
    }

    def __init__(self):
        super().__init__()

        # Detect System Language
        sys_lang = locale.getdefaultlocale()[0]
        self.current_lang = "zh_TW" if sys_lang and "zh" in sys_lang.lower() else "en"

        self.geometry("600x750")
        
        # 檢查 ffmpeg 是否存在
        if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
            messagebox.showerror(self.t("msg_error_title"), self.t("msg_ffmpeg_missing"))

        # 資料變數
        self.files = []  # List of dict: {'path': str, 'size_mb': float, 'duration': float, 'tags': dict}
        self.total_size_mb = 0.0
        self.total_duration_secs = 0.0
        self.target_bitrate = 128
        
        self.output_mode = ctk.StringVar(value="source") # "source" or "custom"
        self.custom_output_dir = ""
        
        self.stop_event = threading.Event()
        self.is_converting = False
        
        self.setup_ui()
        self.update_ui_text() # Initial text set

    def t(self, key):
        """Helper to get translation"""
        return self.TRANSLATIONS[self.current_lang].get(key, key)

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)

        # Top Bar: Title + Language Switcher
        self.frame_top = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_top.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.frame_top.grid_columnconfigure(0, weight=1)

        self.label_title = ctk.CTkLabel(self.frame_top, text="", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_title.grid(row=0, column=0, sticky="w")

        self.lang_var = ctk.StringVar(value="繁體中文" if self.current_lang == "zh_TW" else "English")
        self.option_lang = ctk.CTkOptionMenu(self.frame_top, values=["English", "繁體中文"], 
                                             command=self.change_language, variable=self.lang_var, width=100)
        self.option_lang.grid(row=0, column=1, sticky="e")

        # 2. 檔案選擇與列表
        self.frame_files = ctk.CTkFrame(self)
        self.frame_files.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.frame_files.grid_columnconfigure(0, weight=1)

        self.btn_select = ctk.CTkButton(self.frame_files, text="", command=self.select_files)
        self.btn_select.grid(row=0, column=0, padx=10, pady=10)

        self.txt_filelist = ctk.CTkTextbox(self.frame_files, height=150, state="disabled")
        self.txt_filelist.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        # 3. 輸出設定
        self.frame_output = ctk.CTkFrame(self)
        self.frame_output.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.frame_output.grid_columnconfigure(1, weight=1)
        
        self.lbl_out = ctk.CTkLabel(self.frame_output, text="", font=ctk.CTkFont(weight="bold"))
        self.lbl_out.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.radio_source = ctk.CTkRadioButton(self.frame_output, text="", variable=self.output_mode, value="source")
        self.radio_source.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        self.radio_custom = ctk.CTkRadioButton(self.frame_output, text="", variable=self.output_mode, value="custom", command=self.choose_output_dir)
        self.radio_custom.grid(row=0, column=2, padx=10, pady=10, sticky="w")
        
        self.lbl_custom_path = ctk.CTkLabel(self.frame_output, text="", text_color="gray", font=ctk.CTkFont(size=10))
        self.lbl_custom_path.grid(row=1, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="w")

        # 4. 壓縮品質
        self.label_bitrate = ctk.CTkLabel(self, text="")
        self.label_bitrate.grid(row=3, column=0, padx=20, pady=(10, 0))

        self.slider = ctk.CTkSlider(self, from_=32, to=320, number_of_steps=9, command=self.on_slider_change)
        self.slider.set(self.target_bitrate)
        self.slider.grid(row=4, column=0, padx=20, pady=5)
        
        self.label_hint = ctk.CTkLabel(self, text="", text_color="#555555", font=ctk.CTkFont(size=12, slant="italic"))
        self.label_hint.grid(row=5, column=0, padx=20, pady=(0, 10))

        # 5. 統計資訊
        self.info_frame = ctk.CTkFrame(self)
        self.info_frame.grid(row=6, column=0, padx=40, pady=10, sticky="nsew")
        self.info_frame.grid_columnconfigure(0, weight=1)

        self.label_stats = ctk.CTkLabel(self.info_frame, text="")
        self.label_stats.grid(row=0, column=0, pady=5)

        self.label_pred = ctk.CTkLabel(self.info_frame, text="", 
                                      text_color="#1f538d", font=ctk.CTkFont(size=16, weight="bold"))
        self.label_pred.grid(row=1, column=0, pady=5)

        # 6. 執行與取消
        self.frame_actions = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_actions.grid(row=7, column=0, padx=20, pady=20)
        
        self.btn_run = ctk.CTkButton(self.frame_actions, text="", command=self.start_conversion, 
                                     fg_color="#2c6e49", hover_color="#1e462f", state="disabled")
        self.btn_run.pack(side="left", padx=10)

        self.btn_cancel = ctk.CTkButton(self.frame_actions, text="", command=self.cancel_conversion,
                                        fg_color="#c0392b", hover_color="#922b21", state="disabled")
        self.btn_cancel.pack(side="left", padx=10)

        # 7. 進度與狀態
        self.progress = ctk.CTkProgressBar(self, width=450)
        self.progress.set(0)
        self.progress.grid(row=8, column=0, padx=20, pady=10)

        self.label_status = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=11))
        self.label_status.grid(row=9, column=0, padx=20, pady=5)

    def change_language(self, selection):
        self.current_lang = "zh_TW" if selection == "繁體中文" else "en"
        self.update_ui_text()

    def update_ui_text(self):
        self.title(self.t("app_title"))
        self.label_title.configure(text=self.t("header_title"))
        self.btn_select.configure(text=self.t("btn_select"))
        self.lbl_out.configure(text=self.t("lbl_out"))
        self.radio_source.configure(text=self.t("radio_source"))
        self.radio_custom.configure(text=self.t("radio_custom"))
        
        # Output path label
        if not self.custom_output_dir:
            self.lbl_custom_path.configure(text=self.t("lbl_custom_none"))
        else:
            self.lbl_custom_path.configure(text=f"{self.t('lbl_custom_prefix')}{self.custom_output_dir}")

        self.label_bitrate.configure(text=f"{self.t('bitrate_label')} {self.target_bitrate} kbps")
        self.update_hint(self.target_bitrate)
        
        # Stats
        if self.files:
            self.label_stats.configure(text=self.t("stats_format").format(len(self.files), self.total_size_mb))
        else:
            self.label_stats.configure(text=self.t("stats_initial"))
            
        self.update_prediction()
        
        self.btn_run.configure(text=self.t("btn_run"))
        self.btn_cancel.configure(text=self.t("btn_cancel"))
        
        # Status (Only update if ready or done, not during process to avoid overwriting progress text)
        if not self.is_converting and "..." not in self.label_status.cget("text"):
             self.label_status.configure(text=self.t("status_ready"))

    def choose_output_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.custom_output_dir = path
            self.output_mode.set("custom")
            self.lbl_custom_path.configure(text=f"{self.t('lbl_custom_prefix')}{path}")
        else:
            if self.output_mode.get() == "custom" and not self.custom_output_dir:
                 self.output_mode.set("source") # Revert if cancelled and no path set

    def select_files(self):
        paths = filedialog.askopenfilenames(filetypes=[("Audio Files", "*.wav *.m4a *.mp3 *.aiff *.flac *.ogg")])
        if not paths:
            return

        # Disable UI during analysis
        self.btn_select.configure(state="disabled")
        self.btn_run.configure(state="disabled")
        self.label_status.configure(text=self.t("status_analyzing"))
        
        # Add to list and analyze in thread
        threading.Thread(target=self._analyze_files_thread, args=(paths,), daemon=True).start()

    def _analyze_files_thread(self, paths):
        new_files = []
        errors = []
        for path in paths:
            # Check if already added
            if any(f['path'] == path for f in self.files):
                continue
                
            try:
                size_mb = os.path.getsize(path) / (1024 * 1024)
                
                # Metadata & Duration
                info = mediainfo(path)
                duration = float(info.get('duration', 0))
                
                # Try simple tags extraction
                tags = info.get('TAG', {})
                # Some versions/formats might not put tags in 'TAG' dict, but flat. 
                # For simplicity, we use what mediainfo gives or common keys.
                if not tags:
                    tags = {k: v for k, v in info.items() if k in ['artist', 'title', 'album', 'year', 'date', 'genre']}

                if duration == 0: # Fallback
                    audio = AudioSegment.from_file(path)
                    duration = len(audio) / 1000.0
                
                new_files.append({
                    'path': path,
                    'size_mb': size_mb,
                    'duration': duration,
                    'tags': tags
                })
            except Exception as e:
                errors.append(f"{os.path.basename(path)}: {str(e)}")

        # Update data
        self.files.extend(new_files)
        self.after(0, lambda: self._update_ui_after_analysis(errors))

    def _update_ui_after_analysis(self, errors):
        # Refresh File List UI
        self.txt_filelist.configure(state="normal")
        self.txt_filelist.delete("1.0", "end")
        
        self.total_size_mb = 0
        self.total_duration_secs = 0
        
        for i, f in enumerate(self.files):
            name = os.path.basename(f['path'])
            self.txt_filelist.insert("end", f"{i+1}. {name} ({f['size_mb']:.1f}MB)\n")
            self.total_size_mb += f['size_mb']
            self.total_duration_secs += f['duration']
            
        self.txt_filelist.configure(state="disabled")
        self.txt_filelist.see("end")

        # Update Stats
        self.label_stats.configure(text=self.t("stats_format").format(len(self.files), self.total_size_mb))
        self.update_prediction()
        
        if errors:
            err_msg = "\n".join(errors[:5])
            if len(errors) > 5:
                err_msg += f"\n... (+{len(errors)-5} more)"
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
        hints = self.TRANSLATIONS[self.current_lang]["hints"]
        if bitrate <= 48:
            hint = hints["32"]
        elif bitrate <= 64:
            hint = hints["64"]
        elif bitrate <= 96:
            hint = hints["96"]
        elif bitrate <= 128:
            hint = hints["128"]
        elif bitrate <= 192:
            hint = hints["192"]
        else:
            hint = hints["320"]
        
        prefix = "建議：" if self.current_lang == "zh_TW" else "Tip: "
        self.label_hint.configure(text=f"{prefix}{hint}")

    def update_prediction(self):
        if self.total_duration_secs > 0:
            est_mb = (self.target_bitrate * self.total_duration_secs) / 8192
            if self.current_lang == "zh_TW":
                self.label_pred.configure(text=self.t("pred_format").format(est_mb))
            else:
                self.label_pred.configure(text=self.t("pred_format").format(est_mb))
        else:
             self.label_pred.configure(text=self.t("pred_label"))

    def cancel_conversion(self):
        if self.is_converting:
            self.stop_event.set()
            self.label_status.configure(text=self.t("status_cancelling"))
            self.btn_cancel.configure(state="disabled")

    def start_conversion(self):
        if not self.files:
            return
        
        # Verify output path
        if self.output_mode.get() == "custom" and not self.custom_output_dir:
            messagebox.showwarning(self.t("msg_warning_title"), self.t("msg_output_dir"))
            return

        self.is_converting = True
        self.stop_event.clear()
        
        # UI State
        self.btn_run.configure(state="disabled")
        self.btn_select.configure(state="disabled")
        self.btn_cancel.configure(state="normal")
        self.slider.configure(state="disabled")
        self.radio_source.configure(state="disabled")
        self.radio_custom.configure(state="disabled")
        self.progress.set(0)

        threading.Thread(target=self._batch_convert_thread, daemon=True).start()

    def _batch_convert_thread(self):
        total_files = len(self.files)
        success_count = 0
        error_count = 0
        errors = []

        for i, file_data in enumerate(self.files):
            if self.stop_event.is_set():
                break

            path = file_data['path']
            filename = os.path.basename(path)
            
            self.after(0, lambda p=i/total_files, t=self.t("status_converting").format(i+1, total_files, filename): (
                self.progress.set(p),
                self.label_status.configure(text=t)
            ))

            try:
                # Determine Save Path
                if self.output_mode.get() == "source":
                    out_dir = os.path.dirname(path)
                else:
                    out_dir = self.custom_output_dir
                
                name_root = os.path.splitext(filename)[0]
                save_path = os.path.join(out_dir, f"{name_root}_sm.mp3")

                # Conversion
                bitrate_str = f"{self.target_bitrate}k"
                audio = AudioSegment.from_file(path)
                
                # Export with Metadata
                audio.export(save_path, format="mp3", bitrate=bitrate_str, tags=file_data['tags'])
                
                success_count += 1
                
            except Exception as e:
                error_msg = f"{filename}: {str(e)}"
                print(f"Error converting {path}: {e}")
                errors.append(error_msg)
                error_count += 1

        self.is_converting = False
        self.after(0, lambda: self._conversion_finished(success_count, error_count, total_files, errors))

    def _conversion_finished(self, success, errors_count, total, error_list):
        self.progress.set(1.0)
        
        if self.stop_event.is_set():
            status_text = self.t("status_cancelled").format(success, total)
        elif errors_count > 0:
            status_text = self.t("status_completed_errors").format(success, errors_count)
            err_details = "\n".join(error_list[:5])
            if len(error_list) > 5:
                err_details += f"\n... (+{len(error_list)-5} more)"
            messagebox.showwarning(self.t("msg_warning_title"), f"Errors:\n{err_details}")
        else:
            status_text = self.t("status_success")
            messagebox.showinfo(self.t("msg_success_title"), self.t("msg_success_body").format(success))

        self.label_status.configure(text=status_text)
        
        # Reset UI
        self.btn_run.configure(state="normal")
        self.btn_select.configure(state="normal")
        self.btn_cancel.configure(state="disabled")
        self.slider.configure(state="normal")
        self.radio_source.configure(state="normal")
        self.radio_custom.configure(state="normal")
        
        # Open last folder if successful
        if success > 0:
            out_dir = self.custom_output_dir if self.output_mode.get() == "custom" and self.custom_output_dir else os.path.dirname(self.files[0]['path'])
            self._open_file_in_explorer(out_dir)

    def _open_file_in_explorer(self, path):
        try:
            if sys.platform == 'darwin':
                subprocess.run(['open', path])
            elif sys.platform == 'win32':
                os.startfile(path)
            else:
                subprocess.run(['xdg-open', path])
        except Exception:
            pass
