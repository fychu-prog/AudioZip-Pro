import os
import sys
import threading
import subprocess
import shutil
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
    def __init__(self):
        super().__init__()

        self.title("錄音縮小大師 Pro (批次版)")
        self.geometry("600x750")
        
        # 檢查 ffmpeg 是否存在
        if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
            messagebox.showerror("錯誤", "找不到 ffmpeg 或 ffprobe！\n請確保已安裝 ffmpeg (例如透過 brew install ffmpeg)。\n程式可能無法正常運作。")

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

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)

        # 1. 標題
        self.label_title = ctk.CTkLabel(self, text="錄音檔批次壓縮工具", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_title.grid(row=0, column=0, padx=20, pady=(20, 10))

        # 2. 檔案選擇與列表
        self.frame_files = ctk.CTkFrame(self)
        self.frame_files.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.frame_files.grid_columnconfigure(0, weight=1)

        self.btn_select = ctk.CTkButton(self.frame_files, text="加入檔案 (可多選)", command=self.select_files)
        self.btn_select.grid(row=0, column=0, padx=10, pady=10)

        self.txt_filelist = ctk.CTkTextbox(self.frame_files, height=150, state="disabled")
        self.txt_filelist.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        # 3. 輸出設定
        self.frame_output = ctk.CTkFrame(self)
        self.frame_output.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.frame_output.grid_columnconfigure(1, weight=1)
        
        self.lbl_out = ctk.CTkLabel(self.frame_output, text="輸出位置:", font=ctk.CTkFont(weight="bold"))
        self.lbl_out.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.radio_source = ctk.CTkRadioButton(self.frame_output, text="原資料夾", variable=self.output_mode, value="source")
        self.radio_source.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        self.radio_custom = ctk.CTkRadioButton(self.frame_output, text="指定資料夾...", variable=self.output_mode, value="custom", command=self.choose_output_dir)
        self.radio_custom.grid(row=0, column=2, padx=10, pady=10, sticky="w")
        
        self.lbl_custom_path = ctk.CTkLabel(self.frame_output, text="(未選擇)", text_color="gray", font=ctk.CTkFont(size=10))
        self.lbl_custom_path.grid(row=1, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="w")

        # 4. 壓縮品質
        self.label_bitrate = ctk.CTkLabel(self, text=f"目標品質 (Bitrate): {self.target_bitrate} kbps")
        self.label_bitrate.grid(row=3, column=0, padx=20, pady=(10, 0))

        self.slider = ctk.CTkSlider(self, from_=32, to=320, number_of_steps=9, command=self.on_slider_change)
        self.slider.set(self.target_bitrate)
        self.slider.grid(row=4, column=0, padx=20, pady=5)
        
        self.label_hint = ctk.CTkLabel(self, text="", text_color="#555555", font=ctk.CTkFont(size=12, slant="italic"))
        self.label_hint.grid(row=5, column=0, padx=20, pady=(0, 10))
        self.update_hint(self.target_bitrate)

        # 5. 統計資訊
        self.info_frame = ctk.CTkFrame(self)
        self.info_frame.grid(row=6, column=0, padx=40, pady=10, sticky="nsew")
        self.info_frame.grid_columnconfigure(0, weight=1)

        self.label_stats = ctk.CTkLabel(self.info_frame, text="已選 0 個檔案 | 總大小: 0 MB")
        self.label_stats.grid(row=0, column=0, pady=5)

        self.label_pred = ctk.CTkLabel(self.info_frame, text="預估總產出: -- MB", 
                                      text_color="#1f538d", font=ctk.CTkFont(size=16, weight="bold"))
        self.label_pred.grid(row=1, column=0, pady=5)

        # 6. 執行與取消
        self.frame_actions = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_actions.grid(row=7, column=0, padx=20, pady=20)
        
        self.btn_run = ctk.CTkButton(self.frame_actions, text="開始批次轉檔", command=self.start_conversion, 
                                     fg_color="#2c6e49", hover_color="#1e462f", state="disabled")
        self.btn_run.pack(side="left", padx=10)

        self.btn_cancel = ctk.CTkButton(self.frame_actions, text="取消", command=self.cancel_conversion,
                                        fg_color="#c0392b", hover_color="#922b21", state="disabled")
        self.btn_cancel.pack(side="left", padx=10)

        # 7. 進度與狀態
        self.progress = ctk.CTkProgressBar(self, width=450)
        self.progress.set(0)
        self.progress.grid(row=8, column=0, padx=20, pady=10)

        self.label_status = ctk.CTkLabel(self, text="準備就緒", font=ctk.CTkFont(size=11))
        self.label_status.grid(row=9, column=0, padx=20, pady=5)

    def choose_output_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.custom_output_dir = path
            self.output_mode.set("custom")
            self.lbl_custom_path.configure(text=f"儲存至: {path}")
        else:
            if self.output_mode.get() == "custom" and not self.custom_output_dir:
                 self.output_mode.set("source") # Revert if cancelled and no path set

    def select_files(self):
        paths = filedialog.askopenfilenames(filetypes=[("音訊檔案", "*.wav *.m4a *.mp3 *.aiff *.flac *.ogg")])
        if not paths:
            return

        # Disable UI during analysis
        self.btn_select.configure(state="disabled")
        self.btn_run.configure(state="disabled")
        self.label_status.configure(text="正在分析檔案資訊...")
        
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
        self.label_stats.configure(text=f"已選 {len(self.files)} 個檔案 | 總大小: {self.total_size_mb:.2f} MB")
        self.update_prediction()
        
        if errors:
            err_msg = "\n".join(errors[:5])
            if len(errors) > 5:
                err_msg += f"\n... 以及其他 {len(errors)-5} 個錯誤"
            messagebox.showwarning("部分檔案讀取失敗", f"以下檔案無法讀取：\n{err_msg}")

        self.label_status.configure(text="分析完成")
        self.btn_select.configure(state="normal")
        self.btn_run.configure(state="normal" if self.files else "disabled")

    def on_slider_change(self, value):
        self.target_bitrate = int(value)
        self.label_bitrate.configure(text=f"目標品質 (Bitrate): {self.target_bitrate} kbps")
        self.update_hint(self.target_bitrate)
        self.update_prediction()

    def update_hint(self, bitrate):
        if bitrate <= 48:
            hint = "僅供紀錄 (檔案極小，有機械音)"
        elif bitrate <= 64:
            hint = "節省空間首選 (適合 AI 辨識，人聲清晰)"
        elif bitrate <= 96:
            hint = "AI 辨識最佳平衡 (推薦：檔案小且保留細節)"
        elif bitrate <= 128:
            hint = "標準高品質 (與原音接近，適合一般聽感)"
        elif bitrate <= 192:
            hint = "高保真 (音質優異，適合含背景音樂需求)"
        else:
            hint = "無損等級 (檔案較大，適合收藏或專業需求)"
        self.label_hint.configure(text=f"建議：{hint}")

    def update_prediction(self):
        if self.total_duration_secs > 0:
            est_mb = (self.target_bitrate * self.total_duration_secs) / 8192
            self.label_pred.configure(text=f"預估總產出: 約 {est_mb:.2f} MB")

    def cancel_conversion(self):
        if self.is_converting:
            self.stop_event.set()
            self.label_status.configure(text="正在取消中... (將在目前檔案完成後停止)")
            self.btn_cancel.configure(state="disabled")

    def start_conversion(self):
        if not self.files:
            return
        
        # Verify output path
        if self.output_mode.get() == "custom" and not self.custom_output_dir:
            messagebox.showwarning("提示", "請選擇輸出資料夾")
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
            
            self.after(0, lambda p=i/total_files, t=f"正在處理 ({i+1}/{total_files}): {filename}": (
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
            status_text = f"⚠️ 操作已取消 (完成 {success}/{total})"
        elif errors_count > 0:
            status_text = f"⚠️ 完成但有錯誤 (成功: {success}, 失敗: {errors_count})"
            err_details = "\n".join(error_list[:5])
            if len(error_list) > 5:
                err_details += f"\n... 以及其他 {len(error_list)-5} 個錯誤"
            messagebox.showwarning("完成", f"處理結束\n成功: {success}\n失敗: {errors_count}\n\n錯誤詳情:\n{err_details}")
        else:
            status_text = "✅ 全部完成！"
            messagebox.showinfo("成功", f"成功轉換所有 {success} 個檔案！")

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

if __name__ == "__main__":
    app = AudioShrinkerApp()
    app.mainloop()