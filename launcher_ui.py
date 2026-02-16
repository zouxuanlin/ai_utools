#!/usr/bin/env python3
"""
启动器UI界面
"""
import tkinter as tk
from tkinter import ttk, font
import threading
import time
import os
import sys
from typing import Callable, Optional

# 尝试导入customtkinter，如果不可用则使用标准tkinter
try:
    import customtkinter as ctk
    HAS_CTK = True
except ImportError:
    HAS_CTK = False
    ctk = None


class LauncherUI:
    """启动器UI主类"""
    
    def __init__(self, command_callback: Callable[[str], None]):
        """
        初始化启动器UI
        
        Args:
            command_callback: 当用户输入命令并按下Enter时调用的回调函数
        """
        self.command_callback = command_callback
        self.root = None
        self.is_visible = False
        self.entry = None
        self.status_label = None
        self.suggestions_listbox = None
        self.suggestions = []
        
        # 从配置获取UI设置
        from config import config
        self.config = config
        
        # 创建主窗口
        self._create_window()
    
    def _create_window(self):
        """创建UI窗口"""
        if HAS_CTK:
            self._create_customtkinter_window()
        else:
            self._create_tkinter_window()
    
    def _create_customtkinter_window(self):
        """使用customtkinter创建窗口"""
        # 设置主题
        theme = self.config.get("ui.theme", "dark")
        ctk.set_appearance_mode(theme)
        ctk.set_default_color_theme("blue")
        
        # 创建主窗口
        self.root = ctk.CTk()
        self.root.title("AI uTools")
        self.root.overrideredirect(True)  # 无边框
        
        # 设置窗口大小和位置
        width = self.config.get("ui.width", 600)
        height = self.config.get("ui.height", 80)
        self._set_window_geometry(width, height)
        
        # 设置透明度
        opacity = self.config.get("ui.opacity", 0.95)
        self.root.attributes("-alpha", opacity)
        
        # 创建UI组件
        self._create_widgets_ctk()
        
        # 绑定事件
        self._bind_events()
    
    def _create_tkinter_window(self):
        """使用标准tkinter创建窗口"""
        self.root = tk.Tk()
        self.root.title("AI uTools")
        self.root.overrideredirect(True)  # 无边框
        
        # 设置窗口大小和位置
        width = self.config.get("ui.width", 600)
        height = self.config.get("ui.height", 80)
        self._set_window_geometry(width, height)
        
        # 设置透明度
        opacity = self.config.get("ui.opacity", 0.95)
        self.root.attributes("-alpha", opacity)
        
        # 设置主题颜色
        theme = self.config.get("ui.theme", "dark")
        if theme == "dark":
            bg_color = "#2b2b2b"
            fg_color = "#ffffff"
            entry_bg = "#3c3c3c"
        else:
            bg_color = "#ffffff"
            fg_color = "#000000"
            entry_bg = "#f0f0f0"
        
        self.root.configure(bg=bg_color)
        
        # 创建UI组件
        self._create_widgets_tk(bg_color, fg_color, entry_bg)
        
        # 绑定事件
        self._bind_events()
    
    def _set_window_geometry(self, width: int, height: int):
        """设置窗口几何位置"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        position = self.config.get("ui.position", "center")
        
        if position == "top":
            x = (screen_width - width) // 2
            y = 50
        elif position == "bottom":
            x = (screen_width - width) // 2
            y = screen_height - height - 50
        else:  # center
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
        
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_widgets_ctk(self):
        """创建customtkinter组件"""
        # 主框架
        main_frame = ctk.CTkFrame(self.root, corner_radius=10)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 输入框
        self.entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="输入命令...",
            font=ctk.CTkFont(size=self.config.get("ui.font_size", 16)),
            height=40,
            corner_radius=8
        )
        self.entry.pack(fill="x", padx=10, pady=(10, 5))
        self.entry.focus_set()
        
        # 状态标签
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="就绪",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.status_label.pack(fill="x", padx=10, pady=(0, 5))
        
        # 建议列表框（初始隐藏）
        self.suggestions_frame = ctk.CTkFrame(main_frame, corner_radius=8)
        # 默认隐藏，在需要时显示
    
    def _create_widgets_tk(self, bg_color: str, fg_color: str, entry_bg: str):
        """创建标准tkinter组件"""
        # 主框架
        main_frame = tk.Frame(self.root, bg=bg_color, highlightthickness=1, highlightbackground="#555555")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 输入框
        self.entry = tk.Entry(
            main_frame,
            font=("Helvetica", self.config.get("ui.font_size", 16)),
            bg=entry_bg,
            fg=fg_color,
            insertbackground=fg_color,
            relief="flat",
            bd=0
        )
        self.entry.pack(fill="x", padx=10, pady=(10, 5), ipady=8)
        self.entry.insert(0, "输入命令...")
        self.entry.config(fg="gray")
        self.entry.focus_set()
        
        # 绑定输入框事件
        self.entry.bind("<FocusIn>", self._on_entry_focus_in)
        self.entry.bind("<FocusOut>", self._on_entry_focus_out)
        
        # 状态标签
        self.status_label = tk.Label(
            main_frame,
            text="就绪",
            font=("Helvetica", 10),
            fg="gray",
            bg=bg_color
        )
        self.status_label.pack(fill="x", padx=10, pady=(0, 5))
        
        # 建议列表框（初始隐藏）
        self.suggestions_listbox = tk.Listbox(
            main_frame,
            bg=entry_bg,
            fg=fg_color,
            font=("Helvetica", 12),
            relief="flat",
            bd=0,
            height=5
        )
        # 默认隐藏
    
    def _bind_events(self):
        """绑定键盘事件"""
        # 绑定Enter键
        self.entry.bind("<Return>", self._on_enter)
        
        # 绑定Escape键
        self.root.bind("<Escape>", self._on_escape)
        
        # 绑定Tab键（用于建议选择）
        self.entry.bind("<Tab>", self._on_tab)
        
        # 绑定上下箭头键
        self.entry.bind("<Up>", self._on_up_arrow)
        self.entry.bind("<Down>", self._on_down_arrow)
    
    def _on_entry_focus_in(self, event):
        """输入框获得焦点事件"""
        if self.entry.get() == "输入命令...":
            self.entry.delete(0, tk.END)
            self.entry.config(fg="white" if self.config.get("ui.theme") == "dark" else "black")
    
    def _on_entry_focus_out(self, event):
        """输入框失去焦点事件"""
        if not self.entry.get():
            self.entry.insert(0, "输入命令...")
            self.entry.config(fg="gray")
    
    def _on_enter(self, event):
        """Enter键事件处理"""
        command = self.entry.get().strip()
        if command and command != "输入命令...":
            self.set_status("处理中...")
            
            # 调用回调函数
            if self.command_callback:
                threading.Thread(target=self._execute_command, args=(command,), daemon=True).start()
            
            # 清空输入框
            self.entry.delete(0, tk.END)
        
        return "break"  # 阻止默认行为
    
    def _execute_command(self, command: str):
        """执行命令"""
        try:
            self.command_callback(command)
        except Exception as e:
            self.set_status(f"错误: {str(e)[:50]}")
    
    def _on_escape(self, event):
        """Escape键事件处理"""
        self.hide()
        return "break"
    
    def _on_tab(self, event):
        """Tab键事件处理"""
        # TODO: 实现建议选择
        return "break"
    
    def _on_up_arrow(self, event):
        """上箭头键事件处理"""
        # TODO: 实现建议导航
        return "break"
    
    def _on_down_arrow(self, event):
        """下箭头键事件处理"""
        # TODO: 实现建议导航
        return "break"
    
    def show(self):
        """显示启动器窗口"""
        if not self.is_visible:
            self.is_visible = True
            self.root.deiconify()
            self.entry.focus_set()
            
            # 设置窗口置顶
            self.root.attributes("-topmost", True)
            self.root.after_idle(self.root.attributes, "-topmost", False)
    
    def hide(self):
        """隐藏启动器窗口"""
        if self.is_visible:
            self.is_visible = False
            self.root.withdraw()
            self.set_status("就绪")
    
    def toggle(self):
        """切换显示/隐藏"""
        if self.is_visible:
            self.hide()
        else:
            self.show()
    
    def set_status(self, message: str):
        """设置状态消息"""
        def _update():
            if self.status_label:
                if HAS_CTK:
                    self.status_label.configure(text=message)
                else:
                    self.status_label.config(text=message)
        
        # 确保在UI线程中更新
        if self.root:
            self.root.after(0, _update)
    
    def update_suggestions(self, suggestions: list):
        """更新建议列表"""
        self.suggestions = suggestions
        # TODO: 实现建议列表更新
    
    def run(self):
        """运行UI主循环"""
        # 初始隐藏窗口
        self.hide()
        
        # 启动tkinter主循环
        if HAS_CTK:
            self.root.mainloop()
        else:
            self.root.mainloop()
    
    def quit(self):
        """退出UI"""
        if self.root:
            self.root.quit()
            self.root.destroy()


class DummyLauncherUI:
    """虚拟启动器UI，用于测试"""
    
    def __init__(self, command_callback: Callable[[str], None]):
        self.command_callback = command_callback
        self.is_visible = False
    
    def show(self):
        print("[UI] 启动器显示")
        self.is_visible = True
    
    def hide(self):
        print("[UI] 启动器隐藏")
        self.is_visible = False
    
    def toggle(self):
        if self.is_visible:
            self.hide()
        else:
            self.show()
    
    def set_status(self, message: str):
        print(f"[UI状态] {message}")
    
    def run(self):
        print("[UI] 虚拟UI运行中，按Ctrl+C退出")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    
    def quit(self):
        print("[UI] 虚拟UI退出")


def create_launcher_ui(command_callback: Callable[[str], None]):
    """创建启动器UI实例"""
    try:
        # 检查是否在图形环境下
        if os.environ.get("DISPLAY") or sys.platform == "darwin":
            return LauncherUI(command_callback)
        else:
            raise RuntimeError("无图形环境")
    except Exception as e:
        print(f"无法创建图形UI: {e}，使用虚拟UI")
        return DummyLauncherUI(command_callback)


if __name__ == "__main__":
    # 测试代码
    def test_callback(command: str):
        print(f"收到命令: {command}")
        time.sleep(1)
        print("命令处理完成")
    
    ui = create_launcher_ui(test_callback)
    
    # 启动UI线程
    ui_thread = threading.Thread(target=ui.run, daemon=True)
    ui_thread.start()
    
    print("UI已启动，3秒后显示...")
    time.sleep(3)
    ui.show()
    
    print("5秒后隐藏...")
    time.sleep(5)
    ui.hide()
    
    print("3秒后退出...")
    time.sleep(3)
    ui.quit()