#!/usr/bin/env python3
"""
系统操作执行模块 - 负责执行AI解析出的系统命令
"""
import subprocess
import os
import shutil
import time
import logging
import json
from typing import Dict, Any, Tuple, Optional
import platform

from config import config


class SystemExecutor:
    """系统操作执行器"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.system_info = self._get_system_info()
        
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
    
    def _get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        return {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version()
        }
    
    def execute(self, parsed_command: Dict[str, Any]) -> Tuple[bool, str]:
        """
        执行解析后的命令
        
        Args:
            parsed_command: AI解析后的命令结构
            
        Returns:
            (成功标志, 结果消息)
        """
        try:
            action = parsed_command.get("action", "unknown")
            target = parsed_command.get("target", "")
            parameters = parsed_command.get("parameters", {})
            execution_command = parsed_command.get("execution_command", "")
            
            self.logger.info(f"执行操作: {action}, 目标: {target}")
            
            # 根据action类型执行
            if action == "open_app":
                return self._open_application(target, parameters)
            elif action == "file_operation":
                return self._file_operation(target, parameters)
            elif action == "search":
                return self._search(target, parameters)
            elif action == "calculate":
                return self._calculate(target, parameters)
            elif action == "system_control":
                return self._system_control(target, parameters)
            elif action == "query":
                return self._query(target, parameters)
            elif action == "error":
                return False, parsed_command.get("display_text", "AI解析出错")
            elif execution_command:
                # 如果有直接的执行命令，执行它
                return self._execute_shell_command(execution_command)
            else:
                return False, f"未知操作类型: {action}"
                
        except Exception as e:
            self.logger.error(f"执行命令时出错: {e}")
            return False, f"执行出错: {str(e)[:100]}"
    
    def _open_application(self, app_name: str, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """打开应用程序"""
        try:
            # 构建open命令
            cmd = ["open", "-a", app_name]
            
            # 添加参数（如果有）
            if "args" in parameters:
                if isinstance(parameters["args"], list):
                    cmd.extend(parameters["args"])
                elif isinstance(parameters["args"], str):
                    cmd.append(parameters["args"])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return True, f"已打开 {app_name}"
            else:
                # 尝试使用其他方式打开
                return self._try_alternative_open(app_name)
                
        except subprocess.TimeoutExpired:
            return True, f"正在打开 {app_name}..."
        except FileNotFoundError:
            return self._try_alternative_open(app_name)
        except Exception as e:
            self.logger.error(f"打开应用失败: {e}")
            return False, f"打开 {app_name} 失败"
    
    def _try_alternative_open(self, app_name: str) -> Tuple[bool, str]:
        """尝试其他方式打开应用"""
        try:
            # 尝试直接使用app名称（不含空格）
            clean_name = app_name.replace(" ", "")
            cmd = ["open", "-a", clean_name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                return True, f"已打开 {clean_name}"
            
            # 尝试使用系统搜索
            cmd = ["mdfind", f"kMDItemDisplayName == '{app_name}'"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if result.stdout.strip():
                app_path = result.stdout.split("\n")[0].strip()
                if app_path:
                    subprocess.run(["open", app_path], timeout=5)
                    return True, f"已打开 {app_name}"
            
            return False, f"未找到应用程序: {app_name}"
        except Exception as e:
            return False, f"无法打开应用: {str(e)[:50]}"
    
    def _file_operation(self, target: str, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """文件操作"""
        operation = parameters.get("operation", "open")
        
        try:
            if operation == "open":
                # 打开文件或目录
                if os.path.exists(target):
                    subprocess.run(["open", target], timeout=5)
                    return True, f"已打开 {target}"
                else:
                    # 尝试在Finder中显示
                    target_dir = os.path.dirname(target) or "."
                    subprocess.run(["open", target_dir], timeout=5)
                    return True, f"已打开所在目录"
                    
            elif operation == "delete":
                # 删除文件
                if os.path.exists(target):
                    if os.path.isfile(target):
                        os.remove(target)
                    elif os.path.isdir(target):
                        shutil.rmtree(target)
                    return True, f"已删除 {target}"
                else:
                    return False, f"文件不存在: {target}"
                    
            elif operation == "create":
                # 创建文件
                if not os.path.exists(target):
                    if target.endswith("/") or "." not in os.path.basename(target):
                        os.makedirs(target, exist_ok=True)
                    else:
                        with open(target, "w") as f:
                            f.write("")
                    return True, f"已创建 {target}"
                else:
                    return True, f"文件已存在: {target}"
                    
            elif operation == "list":
                # 列出目录内容
                if os.path.isdir(target):
                    files = os.listdir(target)
                    file_list = "\n".join(files[:10])  # 只显示前10个
                    if len(files) > 10:
                        file_list += f"\n...共 {len(files)} 个文件"
                    return True, f"{target} 内容:\n{file_list}"
                else:
                    return False, f"不是目录: {target}"
                    
            else:
                return False, f"不支持的文件操作: {operation}"
                
        except Exception as e:
            self.logger.error(f"文件操作失败: {e}")
            return False, f"文件操作失败: {str(e)[:50]}"
    
    def _search(self, query: str, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """搜索操作"""
        search_engine = parameters.get("engine", "google")
        
        try:
            if search_engine == "google":
                url = f"https://www.google.com/search?q={query}"
            elif search_engine == "bing":
                url = f"https://www.bing.com/search?q={query}"
            elif search_engine == "duckduckgo":
                url = f"https://duckduckgo.com/?q={query}"
            elif search_engine == "youtube":
                url = f"https://www.youtube.com/results?search_query={query}"
            else:
                url = f"https://www.google.com/search?q={query}"
            
            subprocess.run(["open", url], timeout=5)
            return True, f"正在搜索: {query}"
            
        except Exception as e:
            self.logger.error(f"搜索失败: {e}")
            return False, f"搜索失败: {str(e)[:50]}"
    
    def _calculate(self, expression: str, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """计算操作"""
        try:
            # 如果有计算结果，直接显示
            if "result" in parameters:
                result = parameters["result"]
                return True, f"{expression} = {result}"
            
            # 否则尝试计算
            # 安全检查：只允许数字和基本运算符
            safe_chars = set('0123456789+-*/(). ')
            if all(c in safe_chars for c in expression):
                # 使用eval计算（生产环境应考虑更安全的方法）
                result = eval(expression)
                return True, f"{expression} = {result}"
            else:
                # 打开计算器
                subprocess.run(["open", "-a", "Calculator"], timeout=5)
                return True, f"已打开计算器，请手动计算: {expression}"
                
        except Exception as e:
            self.logger.error(f"计算失败: {e}")
            return False, f"计算失败: {str(e)[:50]}"
    
    def _system_control(self, control_type: str, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """系统控制操作"""
        try:
            if control_type == "empty_trash":
                # 清空废纸篓
                script = 'tell application "Finder" to empty trash'
                subprocess.run(["osascript", "-e", script], timeout=10)
                return True, "废纸篓已清空"
                
            elif control_type == "sleep_display":
                # 睡眠显示器
                subprocess.run(["pmset", "displaysleepnow"], timeout=5)
                return True, "显示器已进入睡眠"
                
            elif control_type == "lock_screen":
                # 锁定屏幕
                subprocess.run(["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession", "-suspend"], timeout=5)
                return True, "屏幕已锁定"
                
            elif control_type == "show_hidden_files":
                # 显示隐藏文件
                subprocess.run(["defaults", "write", "com.apple.finder", "AppleShowAllFiles", "YES"], timeout=5)
                subprocess.run(["killall", "Finder"], timeout=5)
                return True, "已显示隐藏文件，请重启Finder"
                
            elif control_type == "hide_hidden_files":
                # 隐藏隐藏文件
                subprocess.run(["defaults", "write", "com.apple.finder", "AppleShowAllFiles", "NO"], timeout=5)
                subprocess.run(["killall", "Finder"], timeout=5)
                return True, "已隐藏隐藏文件，请重启Finder"
                
            elif control_type == "restart_finder":
                # 重启Finder
                subprocess.run(["killall", "Finder"], timeout=5)
                return True, "Finder已重启"
                
            elif control_type == "take_screenshot":
                # 截屏
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                screenshot_path = os.path.expanduser(f"~/Desktop/Screenshot_{timestamp}.png")
                subprocess.run(["screencapture", screenshot_path], timeout=5)
                return True, f"截图已保存到: {screenshot_path}"
                
            elif control_type == "volume_up":
                # 音量增加
                subprocess.run(["osascript", "-e", "set volume output volume (output volume of (get volume settings) + 10)"], timeout=5)
                return True, "音量已增加"
                
            elif control_type == "volume_down":
                # 音量减少
                subprocess.run(["osascript", "-e", "set volume output volume (output volume of (get volume settings) - 10)"], timeout=5)
                return True, "音量已减少"
                
            elif control_type == "mute":
                # 静音
                subprocess.run(["osascript", "-e", "set volume output volume 0"], timeout=5)
                return True, "已静音"
                
            else:
                return False, f"不支持的系统控制: {control_type}"
                
        except Exception as e:
            self.logger.error(f"系统控制失败: {e}")
            return False, f"系统控制失败: {str(e)[:50]}"
    
    def _query(self, query_type: str, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """查询操作"""
        try:
            if query_type == "current_time":
                import datetime
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return True, f"当前时间: {current_time}"
                
            elif query_type == "battery_status":
                result = subprocess.run(["pmset", "-g", "batt"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    # 提取电池信息
                    lines = result.stdout.split("\n")
                    for line in lines:
                        if "InternalBattery" in line:
                            return True, f"电池状态: {line.strip()}"
                    return True, "电池信息: " + result.stdout[:100]
                else:
                    return True, "无法获取电池信息"
                    
            elif query_type == "system_info":
                info_str = json.dumps(self.system_info, indent=2, ensure_ascii=False)
                return True, f"系统信息:\n{info_str}"
                
            elif query_type == "disk_space":
                result = subprocess.run(["df", "-h", "/"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    lines = result.stdout.split("\n")
                    if len(lines) > 1:
                        return True, f"磁盘空间:\n{lines[1]}"
                return True, "磁盘空间: " + result.stdout[:100]
                
            elif query_type == "network_info":
                result = subprocess.run(["ifconfig"], capture_output=True, text=True, timeout=5)
                return True, "网络信息: " + result.stdout[:200]
                
            else:
                return False, f"不支持的查询类型: {query_type}"
                
        except Exception as e:
            self.logger.error(f"查询失败: {e}")
            return False, f"查询失败: {str(e)[:50]}"
    
    def _execute_shell_command(self, command: str) -> Tuple[bool, str]:
        """执行shell命令"""
        try:
            # 安全考虑：限制一些危险命令
            dangerous_commands = ["rm -rf /", "dd", "mkfs", ":(){ :|:& };:", "> /dev/sda"]
            for dangerous in dangerous_commands:
                if dangerous in command:
                    return False, "拒绝执行危险命令"
            
            # 执行命令
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if len(output) > 200:
                    output = output[:200] + "..."
                return True, f"命令执行成功:\n{output}"
            else:
                error = result.stderr.strip()
                if len(error) > 200:
                    error = error[:200] + "..."
                return False, f"命令执行失败:\n{error}"
                
        except subprocess.TimeoutExpired:
            return False, "命令执行超时"
        except Exception as e:
            self.logger.error(f"执行shell命令失败: {e}")
            return False, f"执行失败: {str(e)[:100]}"
    
    def get_system_capabilities(self) -> Dict[str, Any]:
        """获取系统支持的能力"""
        capabilities = {
            "open_app": True,
            "file_operations": ["open", "delete", "create", "list"],
            "search_engines": ["google", "bing", "duckduckgo", "youtube"],
            "system_controls": [
                "empty_trash", "sleep_display", "lock_screen",
                "show_hidden_files", "hide_hidden_files", "restart_finder",
                "take_screenshot", "volume_up", "volume_down", "mute"
            ],
            "queries": [
                "current_time", "battery_status", "system_info",
                "disk_space", "network_info"
            ]
        }
        
        # 检查特定命令是否存在
        try:
            subprocess.run(["osascript", "-e", "return 1"], capture_output=True, timeout=2)
            capabilities["has_applescript"] = True
        except:
            capabilities["has_applescript"] = False
            
        return capabilities


class SafeSystemExecutor(SystemExecutor):
    """安全系统执行器，增加额外安全检查"""
    
    def __init__(self, allowed_commands: list = None):
        super().__init__()
        self.allowed_commands = allowed_commands or [
            "open", "mdfind", "osascript", "defaults", "killall",
            "pmset", "df", "ifconfig", "screencapture"
        ]
    
    def _execute_shell_command(self, command: str) -> Tuple[bool, str]:
        """安全执行shell命令"""
        # 检查命令是否允许
        command_parts = command.split()
        if command_parts:
            base_cmd = command_parts[0]
            if base_cmd not in self.allowed_commands:
                return False, f"命令不允许: {base_cmd}"
        
        # 调用父类方法
        return super()._execute_shell_command(command)
    
    def execute(self, parsed_command: Dict[str, Any]) -> Tuple[bool, str]:
        """安全执行命令"""
        # 检查命令是否安全
        action = parsed_command.get("action", "")
        if action in ["delete", "system_control"]:
            # 二次确认
            self.logger.warning(f"执行可能危险的操作: {action}")
        
        return super().execute(parsed_command)


def create_system_executor(safe_mode: bool = True) -> SystemExecutor:
    """
    创建系统执行器实例
    
    Args:
        safe_mode: 是否使用安全模式
        
    Returns:
        系统执行器实例
    """
    if safe_mode:
        return SafeSystemExecutor()
    else:
        return SystemExecutor()


if __name__ == "__main__":
    # 测试代码
    executor = create_system_executor()
    
    # 测试各种操作
    test_commands = [
        {
            "action": "open_app",
            "target": "Calculator",
            "parameters": {},
            "execution_command": "",
            "display_text": "打开计算器"
        },
        {
            "action": "query",
            "target": "current_time",
            "parameters": {},
            "execution_command": "",
            "display_text": "查询当前时间"
        },
        {
            "action": "search",
            "target": "Python tutorial",
            "parameters": {"engine": "google"},
            "execution_command": "",
            "display_text": "搜索Python教程"
        }
    ]
    
    for i, cmd in enumerate(test_commands):
        print(f"\n测试命令 {i+1}: {cmd['display_text']}")
        success, message = executor.execute(cmd)
        print(f"结果: {success}, 消息: {message}")
        time.sleep(1)
    
    # 显示系统能力
    print(f"\n系统能力: {json.dumps(executor.get_system_capabilities(), indent=2)}")