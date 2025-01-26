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
        
        # 保存下载目录
        self.download_dir = os.path.join(os.path.dirname(__file__), "download")
        # 将下载目录第一个字符改为大写
        if self.download_dir:
            self.download_dir = self.download_dir[0].upper() + self.download_dir[1:]
        
        # 设置窗口关闭事件处理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 左侧主要内容框架
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # URL输入框
        self.url_label = ttk.Label(self.left_frame, text="请输入视频URL或av/bv/ep/ss号：")
        self.url_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.url_entry = ttk.Entry(self.left_frame, width=50)
        self.url_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # 下载目录选择
        self.dir_frame = ttk.Frame(self.left_frame)
        self.dir_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.dir_label = ttk.Label(self.dir_frame, text="下载目录：")
        self.dir_label.grid(row=0, column=0, padx=5)
        
        self.dir_entry = ttk.Entry(self.dir_frame, width=40)
        self.dir_entry.grid(row=0, column=1, padx=5)
        self.dir_entry.insert(0, self.download_dir)  # 已经是大写的目录路径
        
        self.dir_button = ttk.Button(self.dir_frame, text="选择目录", command=self.choose_directory)
        self.dir_button.grid(row=0, column=2, padx=5)
        
        # 下载按钮
        self.download_button = ttk.Button(self.left_frame, text="开始下载", command=self.start_download)
        self.download_button.grid(row=3, column=0, pady=10)
        
        # 进度显示
        self.progress_label = ttk.Label(self.left_frame, text="")
        self.progress_label.grid(row=4, column=0, sticky=tk.W, pady=5)
        
        # 状态文本框
        self.status_text = tk.Text(self.left_frame, height=10, width=50)
        self.status_text.grid(row=5, column=0, pady=5)
        self.status_text.config(state='disabled')
        
        # 右侧下载选项框架
        self.options_frame = ttk.LabelFrame(self.main_frame, text="下载选项", padding="5")
        self.options_frame.grid(row=0, column=1, sticky=(tk.N, tk.S), padx=10)
        
        # 下载选项复选框
        self.video_only = tk.BooleanVar()
        self.audio_only = tk.BooleanVar()
        self.danmaku_only = tk.BooleanVar()
        self.sub_only = tk.BooleanVar()
        
        self.video_check = ttk.Checkbutton(self.options_frame, text="仅下载视频", variable=self.video_only)
        self.video_check.grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        
        self.audio_check = ttk.Checkbutton(self.options_frame, text="仅下载音频", variable=self.audio_only)
        self.audio_check.grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        
        self.danmaku_check = ttk.Checkbutton(self.options_frame, text="仅下载弹幕", variable=self.danmaku_only)
        self.danmaku_check.grid(row=2, column=0, padx=5, pady=2, sticky=tk.W)
        
        self.sub_check = ttk.Checkbutton(self.options_frame, text="仅下载字幕", variable=self.sub_only)
        self.sub_check.grid(row=3, column=0, padx=5, pady=2, sticky=tk.W)

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

    def choose_directory(self):
        """选择下载目录"""
        from tkinter import filedialog
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.download_dir = dir_path
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, dir_path)
            # 将第一个字符改为大写
            text = self.dir_entry.get()
            if text:
                self.dir_entry.delete(0, 1)
                self.dir_entry.insert(0, text[0].upper())

    def download_video(self, url):
        try:
            if not os.path.exists(self.bbdown_path):
                raise FileNotFoundError(f"找不到BBDown程序，请确保tools文件夹中包含BBDown.exe")
            
            # 获取当前下载目录
            self.download_dir = self.dir_entry.get()
            os.makedirs(self.download_dir, exist_ok=True)
            
            # 获取所有需要下载的类型
            download_types = []
            if self.video_only.get():
                download_types.append("--video-only")
            if self.audio_only.get():
                download_types.append("--audio-only")
            if self.danmaku_only.get():
                download_types.append("--danmaku-only")
            if self.sub_only.get():
                download_types.append("--sub-only")
            
            # 如果没有选择任何类型，执行一次完整下载
            if not download_types:
                download_types.append("")
            
            # 对每个类型分别执行下载
            for download_type in download_types:
                cmd = [self.bbdown_path, url, "--work-dir", self.download_dir]
                if download_type:
                    cmd.append(download_type)
                    
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
                        self.status_text.config(state='normal')
                        self.status_text.insert(tk.END, output)
                        self.status_text.see(tk.END)
                        self.status_text.config(state='disabled')
                        self.root.update()
                
                rc = self.current_process.poll()
                if rc != 0:
                    raise Exception(f"下载失败：{download_type if download_type else '完整内容'}")
            
            self.progress_label.config(text="下载完成！")
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
