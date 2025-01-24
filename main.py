import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import os

class BBDownGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("BBDown GUI")
        self.root.geometry("600x400")
        
        # BBDown路径配置
        self.bbdown_path = os.path.join(os.path.dirname(__file__), "tools", "BBDown.exe")
        
        # 保存当前下载进程
        self.current_process = None
        
        # 设置窗口关闭事件处理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # URL输入框
        self.url_label = ttk.Label(self.main_frame, text="请输入视频URL或av/bv/ep/ss号：")
        self.url_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.url_entry = ttk.Entry(self.main_frame, width=50)
        self.url_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # 下载选项框架
        self.options_frame = ttk.LabelFrame(self.main_frame, text="下载选项", padding="5")
        self.options_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # 下载选项复选框
        self.video_only = tk.BooleanVar()
        self.audio_only = tk.BooleanVar()
        self.danmaku_only = tk.BooleanVar()
        self.sub_only = tk.BooleanVar()
        
        self.video_check = ttk.Checkbutton(self.options_frame, text="仅下载视频", variable=self.video_only)
        self.video_check.grid(row=0, column=0, padx=5, sticky=tk.W)
        
        self.audio_check = ttk.Checkbutton(self.options_frame, text="仅下载音频", variable=self.audio_only)
        self.audio_check.grid(row=0, column=1, padx=5, sticky=tk.W)
        
        self.danmaku_check = ttk.Checkbutton(self.options_frame, text="仅下载弹幕", variable=self.danmaku_only)
        self.danmaku_check.grid(row=1, column=0, padx=5, sticky=tk.W)
        
        self.sub_check = ttk.Checkbutton(self.options_frame, text="仅下载字幕", variable=self.sub_only)
        self.sub_check.grid(row=1, column=1, padx=5, sticky=tk.W)
        
        # 下载按钮
        self.download_button = ttk.Button(self.main_frame, text="开始下载", command=self.start_download)
        self.download_button.grid(row=3, column=0, pady=10)
        
        # 进度显示
        self.progress_label = ttk.Label(self.main_frame, text="")
        self.progress_label.grid(row=4, column=0, sticky=tk.W, pady=5)
        
        # 状态文本框
        self.status_text = tk.Text(self.main_frame, height=10, width=50)
        self.status_text.grid(row=5, column=0, pady=5)
        # 设置状态文本框为只读
        self.status_text.config(state='disabled')
        
    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("错误", "请输入视频URL或视频ID！")
            return
            
        self.download_button.state(['disabled'])
        self.progress_label.config(text="下载中...")
        
        # 在新线程中执行下载
        thread = threading.Thread(target=self.download_video, args=(url,))
        thread.daemon = True
        thread.start()
    
    def on_closing(self):
        # 如果有正在运行的进程，终止它
        if self.current_process is not None:
            self.current_process.terminate()
        self.root.destroy()

    def download_video(self, url):
        try:
            if not os.path.exists(self.bbdown_path):
                raise FileNotFoundError(f"找不到BBDown程序，请确保tools文件夹中包含BBDown.exe")
            
            # 确保download文件夹存在
            download_dir = os.path.join(os.path.dirname(__file__), "download")
            os.makedirs(download_dir, exist_ok=True)
            
            # 构建命令参数
            cmd = [self.bbdown_path, url, "--work-dir", download_dir]
            
            # 添加选项参数
            if self.video_only.get():
                cmd.append("--video-only")
            if self.audio_only.get():
                cmd.append("--audio-only")
            if self.danmaku_only.get():
                cmd.append("--danmaku-only")
            if self.sub_only.get():
                cmd.append("--sub-only")
                
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # 读取输出并更新状态
            while True:
                output = self.current_process.stdout.readline()
                if output == '' and self.current_process.poll() is not None:
                    break
                if output:
                    # 临时启用文本框以插入文本
                    self.status_text.config(state='normal')
                    self.status_text.insert(tk.END, output)
                    self.status_text.see(tk.END)
                    # 插入后重新禁用文本框
                    self.status_text.config(state='disabled')
                    self.root.update()
            
            rc = self.current_process.poll()
            if rc == 0:
                self.progress_label.config(text="下载完成！")
            else:
                self.progress_label.config(text="下载失败！")
        except Exception as e:
            # 临时启用文本框以插入错误信息
            self.status_text.config(state='normal')
            self.status_text.insert(tk.END, f"错误：{str(e)}\n")
            self.status_text.config(state='disabled')
            self.progress_label.config(text="下载失败！")
        finally:
            self.current_process = None
            self.download_button.state(['!disabled'])

def main():
    root = tk.Tk()
    app = BBDownGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
