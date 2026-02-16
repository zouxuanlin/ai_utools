#!/usr/bin/env python3
"""
AI uTools 主程序入口
"""
import sys
import os
import threading
import time
import logging
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config
from hotkey_manager import create_hotkey_manager
from launcher_ui import create_launcher_ui
from ai_agent import create_ai_agent
from system_executor import create_system_executor


class AIuTools:
    """AI uTools 主应用程序"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.ui = None
        self.hotkey_manager = None
        self.ai_agent = None
        self.system_executor = None
        self.is_running = False
        
        self.logger.info("AI uTools 初始化...")
        
    def _setup_logging(self):
        """设置日志系统"""
        # 创建日志目录
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # 配置日志
        logger = logging.getLogger("ai_utools")
        logger.setLevel(logging.INFO)
        
        # 文件处理器
        log_file = config.get("logging.file", "logs/ai_utools.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def initialize(self):
        """初始化应用程序组件"""
        try:
            self.logger.info("初始化组件...")
            
            # 创建AI代理
            self.ai_agent = create_ai_agent()
            
            # 创建系统执行器
            self.system_executor = create_system_executor(safe_mode=True)
            
            # 创建UI（传入命令处理回调）
            self.ui = create_launcher_ui(self._handle_user_command)
            
            # 创建快捷键管理器（传入UI切换回调）
            self.hotkey_manager = create_hotkey_manager(self.ui.toggle)
            
            self.logger.info("组件初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"初始化失败: {e}")
            return False
    
    def _handle_user_command(self, user_input: str):
        """
        处理用户输入的命令
        
        Args:
            user_input: 用户输入的自然语言命令
        """
        self.logger.info(f"处理用户命令: {user_input}")
        
        # 更新UI状态
        self.ui.set_status("AI解析中...")
        
        try:
            # 1. 使用AI代理解析命令
            parsed_command = self.ai_agent.parse_command(user_input)
            
            # 2. 执行命令
            self.ui.set_status("执行中...")
            success, message = self.system_executor.execute(parsed_command)
            
            # 3. 更新UI状态
            if success:
                self.ui.set_status("完成")
                # 显示执行结果
                display_text = parsed_command.get("display_text", "操作完成")
                if message and message != display_text:
                    self.ui.set_status(f"{display_text} - {message}")
                else:
                    self.ui.set_status(display_text)
            else:
                self.ui.set_status(f"失败: {message}")
                
            # 4. 记录结果
            self.logger.info(f"命令执行结果: {success}, 消息: {message}")
            
        except Exception as e:
            error_msg = f"处理命令时出错: {str(e)[:100]}"
            self.logger.error(error_msg)
            self.ui.set_status(f"错误: {error_msg}")
    
    def start(self):
        """启动应用程序"""
        if self.is_running:
            self.logger.warning("应用程序已在运行")
            return
        
        try:
            self.logger.info("启动 AI uTools...")
            
            # 初始化组件
            if not self.initialize():
                self.logger.error("初始化失败，应用程序退出")
                return
            
            # 启动快捷键监听
            self.hotkey_manager.start()
            
            # 显示启动消息
            hotkey_str = "+".join(config.hotkey_modifier) + "+" + config.hotkey_key
            self.logger.info(f"AI uTools 已启动，使用快捷键 {hotkey_str} 打开启动器")
            print(f"AI uTools 已启动")
            print(f"快捷键: {hotkey_str}")
            print(f"AI模式: {config.ai_provider}")
            print("按 Ctrl+C 退出程序")
            
            self.is_running = True
            
            # 启动UI（在主线程中运行）
            self.ui.run()
            
        except KeyboardInterrupt:
            self.logger.info("收到中断信号")
        except Exception as e:
            self.logger.error(f"启动失败: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """停止应用程序"""
        if not self.is_running:
            return
        
        self.logger.info("停止应用程序...")
        
        try:
            # 停止快捷键监听
            if self.hotkey_manager:
                self.hotkey_manager.stop()
            
            # 停止UI
            if self.ui:
                self.ui.quit()
            
            self.is_running = False
            self.logger.info("应用程序已停止")
            
        except Exception as e:
            self.logger.error(f"停止应用程序时出错: {e}")
    
    def run_in_background(self):
        """在后台运行应用程序"""
        self.logger.info("在后台运行应用程序...")
        
        # 初始化但不启动UI主循环
        if not self.initialize():
            return
        
        # 启动快捷键监听
        self.hotkey_manager.start()
        
        hotkey_str = "+".join(config.hotkey_modifier) + "+" + config.hotkey_key
        print(f"AI uTools 后台服务已启动")
        print(f"快捷键: {hotkey_str}")
        print(f"AI模式: {config.ai_provider}")
        print("按 Ctrl+C 退出程序")
        
        self.is_running = True
        
        try:
            # 保持主线程运行
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("收到中断信号")
        finally:
            self.stop()


def check_dependencies():
    """检查依赖是否安装"""
    required_packages = [
        "PyYAML",
        "pynput",
        "keyboard",
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("缺少依赖包:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\n请运行以下命令安装:")
        print("pip install " + " ".join(missing_packages))
        return False
    
    return True


def setup_configuration():
    """交互式配置设置"""
    from config import config
    
    print("=== AI uTools 配置向导 ===")
    print()
    
    # 检查OpenAI API密钥
    api_key = config.openai_api_key
    if not api_key:
        print("未检测到OpenAI API密钥")
        choice = input("是否要配置OpenAI API密钥？(y/n): ").strip().lower()
        if choice == 'y':
            api_key = input("请输入OpenAI API密钥: ").strip()
            config.set("ai.openai_api_key", api_key)
            if config.save():
                print("API密钥已保存")
            else:
                print("保存失败")
    
    # 检查快捷键配置
    hotkey_modifier = config.hotkey_modifier
    hotkey_key = config.hotkey_key
    print(f"当前快捷键: {hotkey_modifier}+{hotkey_key}")
    
    choice = input("是否要更改快捷键？(y/n): ").strip().lower()
    if choice == 'y':
        print("可用的修饰键: command, ctrl, shift, alt")
        modifiers = input("请输入修饰键（用逗号分隔）: ").strip()
        if modifiers:
            modifier_list = [m.strip() for m in modifiers.split(",")]
            config.set("hotkey.modifier", modifier_list)
        
        key = input("请输入触发键（如 p, space, enter）: ").strip()
        if key:
            config.set("hotkey.key", key)
        
        if config.save():
            print("快捷键配置已保存")
    
    print("配置完成！")
    print()


def main():
    """主函数"""
    print("AI uTools - macOS智能启动器")
    print("=" * 40)
    
    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description="AI uTools - macOS智能启动器")
    parser.add_argument("--setup", action="store_true", help="运行配置向导")
    parser.add_argument("--background", action="store_true", help="在后台运行（无UI窗口）")
    parser.add_argument("--test", action="store_true", help="运行测试")
    parser.add_argument("--install-autostart", action="store_true", help="安装为开机自启动")
    parser.add_argument("--uninstall-autostart", action="store_true", help="卸载开机自启动")
    
    args = parser.parse_args()
    
    # 运行配置向导
    if args.setup:
        setup_configuration()
        return
    
    # 安装开机自启动
    if args.install_autostart:
        install_autostart()
        return
    
    # 卸载开机自启动
    if args.uninstall_autostart:
        uninstall_autostart()
        return
    
    # 运行测试
    if args.test:
        run_tests()
        return
    
    # 检查依赖
    if not check_dependencies():
        print("\n请先安装依赖包，然后重新运行程序。")
        return
    
    # 创建应用程序实例
    app = AIuTools()
    
    # 运行应用程序
    if args.background:
        app.run_in_background()
    else:
        app.start()


def install_autostart():
    """安装为开机自启动"""
    print("安装为开机自启动...")
    
    try:
        # 获取当前脚本路径
        script_path = os.path.abspath(__file__)
        
        # 创建plist文件内容
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.app.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ai.utools</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>{script_path}</string>
        <string>--background</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/tmp/ai_utools.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/ai_utools_error.log</string>
</dict>
</plist>"""
        
        # 写入plist文件
        plist_path = os.path.expanduser("~/Library/LaunchAgents/com.ai.utools.plist")
        plist_dir = os.path.dirname(plist_path)
        os.makedirs(plist_dir, exist_ok=True)
        
        with open(plist_path, 'w') as f:
            f.write(plist_content)
        
        # 设置权限
        os.chmod(plist_path, 0o644)
        
        print(f"已创建启动项: {plist_path}")
        print("重启后生效，或手动运行: launchctl load ~/Library/LaunchAgents/com.ai.utools.plist")
        
    except Exception as e:
        print(f"安装失败: {e}")


def uninstall_autostart():
    """卸载开机自启动"""
    print("卸载开机自启动...")
    
    try:
        plist_path = os.path.expanduser("~/Library/LaunchAgents/com.ai.utools.plist")
        
        if os.path.exists(plist_path):
            os.remove(plist_path)
            print(f"已删除启动项: {plist_path}")
            print("请手动运行: launchctl unload ~/Library/LaunchAgents/com.ai.utools.plist")
        else:
            print("未找到启动项")
            
    except Exception as e:
        print(f"卸载失败: {e}")


def run_tests():
    """运行测试"""
    print("运行测试...")
    
    try:
        # 导入测试模块
        from ai_agent import SimpleRuleBasedAgent
        from system_executor import SystemExecutor
        
        # 测试AI代理
        print("\n1. 测试AI代理:")
        agent = SimpleRuleBasedAgent()
        test_inputs = [
            "打开Safari",
            "搜索机器学习",
            "计算15+23",
            "清空废纸篓",
            "当前时间",
        ]
        
        for test_input in test_inputs:
            result = agent.parse_command(test_input)
            print(f"  输入: {test_input}")
            print(f"  动作: {result.get('action')}")
            print(f"  目标: {result.get('target')}")
        
        # 测试系统执行器
        print("\n2. 测试系统执行器:")
        executor = SystemExecutor()
        capabilities = executor.get_system_capabilities()
        print(f"  系统能力: {list(capabilities.keys())}")
        
        # 测试配置
        print("\n3. 测试配置:")
        from config import config
        print(f"  AI提供商: {config.ai_provider}")
        print(f"  快捷键: {config.hotkey_modifier}+{config.hotkey_key}")
        
        print("\n测试完成！")
        
    except Exception as e:
        print(f"测试失败: {e}")


if __name__ == "__main__":
    main()