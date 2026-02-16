#!/usr/bin/env python3
"""
全局快捷键管理模块
"""
import threading
import time
import logging
from typing import Callable, Optional

# pynput导入将在需要时动态进行
# from pynput import keyboard
# from pynput.keyboard import Key, KeyCode, Controller


class HotkeyManager:
    """全局快捷键管理器"""
    
    def __init__(self, toggle_callback: Callable[[], None]):
        """
        初始化快捷键管理器
        
        Args:
            toggle_callback: 当快捷键触发时调用的回调函数
        """
        self.toggle_callback = toggle_callback
        self.listener = None
        self.is_listening = False
        self.current_keys = set()
        
        # 从配置获取快捷键
        from config import config
        
        self.modifier_keys = self._parse_modifiers(config.hotkey_modifier)
        self.trigger_key = self._parse_key(config.hotkey_key)
        
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """设置日志器"""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _parse_modifiers(self, modifiers: list) -> set:
        """解析修饰键"""
        from pynput.keyboard import Key
        
        modifier_map = {
            "command": Key.cmd,
            "ctrl": Key.ctrl,
            "shift": Key.shift,
            "alt": Key.alt,
            "option": Key.alt,
            "control": Key.ctrl
        }
        
        parsed = set()
        for mod in modifiers:
            mod_lower = mod.lower()
            if mod_lower in modifier_map:
                parsed.add(modifier_map[mod_lower])
            else:
                self.logger.warning(f"未知修饰键: {mod}")
        
        return parsed
    
    def _parse_key(self, key_str: str):
        """解析触发键"""
        from pynput.keyboard import Key, KeyCode
        
        # 特殊键映射
        special_keys = {
            "space": Key.space,
            "enter": Key.enter,
            "tab": Key.tab,
            "escape": Key.esc,
            "backspace": Key.backspace,
            "delete": Key.delete,
            "up": Key.up,
            "down": Key.down,
            "left": Key.left,
            "right": Key.right,
            "home": Key.home,
            "end": Key.end,
            "pageup": Key.page_up,
            "pagedown": Key.page_down,
            "f1": Key.f1,
            "f2": Key.f2,
            "f3": Key.f3,
            "f4": Key.f4,
            "f5": Key.f5,
            "f6": Key.f6,
            "f7": Key.f7,
            "f8": Key.f8,
            "f9": Key.f9,
            "f10": Key.f10,
            "f11": Key.f11,
            "f12": Key.f12,
        }
        
        key_str_lower = key_str.lower()
        
        if key_str_lower in special_keys:
            return special_keys[key_str_lower]
        elif len(key_str) == 1:
            # 单个字符键
            return KeyCode.from_char(key_str.lower())
        else:
            # 尝试作为字母键处理
            if key_str_lower.isalpha() and len(key_str_lower) == 1:
                return KeyCode.from_char(key_str_lower)
            else:
                self.logger.warning(f"无法识别的键: {key_str}, 使用默认键 'p'")
                return KeyCode.from_char('p')
    
    def _on_press(self, key):
        """按键按下事件处理"""
        try:
            # 记录按下的键
            self.current_keys.add(key)
            
            # 检查是否满足快捷键条件
            if self._check_hotkey_combination():
                self.logger.debug("快捷键触发")
                # 清除当前按键状态，避免重复触发
                self.current_keys.clear()
                # 调用回调函数
                if self.toggle_callback:
                    threading.Thread(target=self.toggle_callback, daemon=True).start()
                # 返回False会停止事件传播
                return False
                
        except Exception as e:
            self.logger.error(f"按键处理错误: {e}")
    
    def _on_release(self, key):
        """按键释放事件处理"""
        try:
            # 从当前按键集合中移除
            if key in self.current_keys:
                self.current_keys.remove(key)
        except Exception as e:
            self.logger.error(f"释放按键处理错误: {e}")
    
    def _check_hotkey_combination(self) -> bool:
        """检查当前按键组合是否符合快捷键设置"""
        # 需要所有修饰键都被按下
        for modifier in self.modifier_keys:
            if modifier not in self.current_keys:
                return False
        
        # 需要触发键被按下
        if self.trigger_key not in self.current_keys:
            return False
        
        # 检查是否有其他非修饰键被按下（除了我们的组合键）
        for key in self.current_keys:
            if key not in self.modifier_keys and key != self.trigger_key:
                return False
        
        return True
    
    def start(self):
        """开始监听快捷键"""
        if self.is_listening:
            self.logger.warning("快捷键监听已经在运行")
            return
        
        try:
            from pynput import keyboard
            self.listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release
            )
            self.listener.start()
            self.is_listening = True
            
            hotkey_str = self._get_hotkey_string()
            self.logger.info(f"快捷键监听已启动: {hotkey_str}")
            
        except ImportError:
            self.logger.error("pynput库未安装，无法启动快捷键监听")
            self.is_listening = False
            raise
        except Exception as e:
            self.logger.error(f"启动快捷键监听失败: {e}")
            self.is_listening = False
    
    def stop(self):
        """停止监听快捷键"""
        if self.listener:
            self.listener.stop()
            self.listener = None
        self.is_listening = False
        self.logger.info("快捷键监听已停止")
    
    def _get_hotkey_string(self) -> str:
        """获取快捷键字符串表示"""
        from config import config
        
        modifiers = config.get("hotkey.modifier", ["command", "shift"])
        key = config.get("hotkey.key", "p")
        
        return "+".join(modifiers) + "+" + key
    
    def update_hotkey(self, modifiers: list, key: str):
        """更新快捷键设置"""
        self.stop()
        
        self.modifier_keys = self._parse_modifiers(modifiers)
        self.trigger_key = self._parse_key(key)
        
        self.start()
        self.logger.info(f"快捷键已更新: {self._get_hotkey_string()}")


class DummyHotkeyManager:
    """虚拟快捷键管理器，用于测试或当pynput不可用时"""
    
    def __init__(self, toggle_callback: Callable[[], None]):
        self.toggle_callback = toggle_callback
        self.is_listening = False
        self.logger = logging.getLogger(__name__)
    
    def start(self):
        self.is_listening = True
        self.logger.warning("使用虚拟快捷键管理器，实际快捷键功能不可用")
        self.logger.info("请确保安装了pynput库: pip install pynput")
    
    def stop(self):
        self.is_listening = False
        self.logger.info("虚拟快捷键管理器已停止")
    
    def update_hotkey(self, modifiers: list, key: str):
        self.logger.info(f"虚拟快捷键更新为: {modifiers}+{key}")


def create_hotkey_manager(toggle_callback: Callable[[], None]) -> HotkeyManager:
    """创建快捷键管理器实例"""
    try:
        # 检查pynput是否可用
        import pynput
        return HotkeyManager(toggle_callback)
    except ImportError:
        logging.warning("pynput库未安装，使用虚拟快捷键管理器")
        return DummyHotkeyManager(toggle_callback)


if __name__ == "__main__":
    # 测试代码
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    def test_callback():
        print("快捷键触发！")
    
    manager = create_hotkey_manager(test_callback)
    manager.start()
    
    print(f"正在监听快捷键: {manager._get_hotkey_string()}")
    print("按 Ctrl+C 退出...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        manager.stop()
        print("程序退出")