#!/usr/bin/env python3
"""
独立配置向导脚本 - 不依赖外部库
"""
import sys
import os
import json
import time

def print_header(title):
    """打印标题"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def check_python_version():
    """检查Python版本"""
    print_header("检查Python版本")
    
    version = sys.version_info
    print(f"Python版本: {sys.version}")
    
    if version.major == 3 and version.minor >= 8:
        print("✓ Python版本符合要求 (3.8+)")
        return True
    else:
        print("✗ Python版本过低，需要3.8或更高版本")
        print("建议升级到Python 3.9或更高版本")
        return False

def check_system():
    """检查系统环境"""
    import platform
    
    print_header("检查系统环境")
    
    system = platform.system()
    print(f"操作系统: {system} {platform.release()}")
    
    if system == "Darwin":
        print("✓ 运行在macOS上")
        
        # 检查macOS版本
        version = platform.mac_ver()[0]
        major_version = int(version.split('.')[0]) if '.' in version else 0
        if major_version >= 10:
            print(f"✓ macOS版本: {version}")
        else:
            print(f"⚠ macOS版本可能较低: {version}")
        
        return True
    else:
        print("⚠ 不是macOS系统，某些功能可能不可用")
        return True

def check_dependencies():
    """检查依赖包"""
    print_header("检查依赖包")
    
    required_packages = [
        ("PyYAML", "yaml"),
        ("pynput", "pynput"),
        ("keyboard", "keyboard"),
    ]
    
    missing_packages = []
    optional_missing = []
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"✓ {package_name}")
        except ImportError:
            if package_name in ["pynput", "keyboard"]:
                print(f"⚠ {package_name} (快捷键功能需要)")
                missing_packages.append(package_name)
            else:
                print(f"✗ {package_name}")
                missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\n缺少依赖包: {', '.join(missing_packages)}")
        print("请运行以下命令安装:")
        
        # 根据Python版本提供不同建议
        if sys.version_info.minor < 9:
            print("\n由于Python版本为3.8，某些库可能需要特殊处理:")
            print("1. 尝试使用较旧版本的pynput:")
            print("   pip install 'pynput==1.7.3'")
            print("2. 或者升级Python到3.9+:")
            print("   brew install python@3.9")
        else:
            print("   pip install " + " ".join(missing_packages))
        
        print("\n注意: pynput库可能需要macOS辅助功能权限")
        print("安装后请前往: 系统设置 > 隐私与安全性 > 辅助功能")
        print("并添加终端或Python应用程序到允许列表")
    
    return len(missing_packages) == 0

def setup_configuration():
    """配置设置（交互式或非交互式）"""
    print_header("AI uTools 配置向导")
    
    # 创建基本配置
    config = {
        "hotkey": {
            "modifier": ["command", "shift"],
            "key": "p",
            "enabled": True
        },
        "ai": {
            "provider": "rule",  # 默认使用规则引擎，避免API依赖
            "openai_api_key": "",
            "deepseek_api_key": "",
            "model": "gpt-4o-mini",
            "deepseek_model": "deepseek-chat",
            "temperature": 0.2,
            "max_tokens": 500
        },
        "ui": {
            "theme": "dark",
            "width": 600,
            "height": 80,
            "position": "center",
            "opacity": 0.95,
            "font_size": 16
        },
        "system": {
            "default_browser": "Safari",
            "terminal": "Terminal",
            "file_manager": "Finder"
        }
    }
    
    # 检查是否为交互式终端
    interactive = sys.stdin.isatty()
    
    if interactive:
        print("\n1. AI配置")
        print("当前AI提供商: 规则引擎 (无需API密钥)")
        print("可选: OpenAI API (需要API密钥), 本地模型 (需要下载模型)")
        
        try:
            choice = input("是否配置OpenAI API密钥？(y/n): ").strip().lower()
            if choice == 'y':
                api_key = input("请输入OpenAI API密钥: ").strip()
                if api_key:
                    config["ai"]["openai_api_key"] = api_key
                    config["ai"]["provider"] = "openai"
                    print("✓ OpenAI API密钥已设置")
        except EOFError:
            print("\n⚠ 检测到非交互式输入，跳过API密钥配置")
        
        print("\n2. 快捷键配置")
        print(f"当前快捷键: {config['hotkey']['modifier']}+{config['hotkey']['key']}")
        
        try:
            choice = input("是否更改快捷键？(y/n): ").strip().lower()
            if choice == 'y':
                print("可用的修饰键: command, ctrl, shift, alt")
                modifiers = input("请输入修饰键（用逗号分隔，如 command,shift）: ").strip()
                if modifiers:
                    modifier_list = [m.strip() for m in modifiers.split(",")]
                    config["hotkey"]["modifier"] = modifier_list
                
                key = input("请输入触发键（如 p, space, enter）: ").strip()
                if key:
                    config["hotkey"]["key"] = key
                
                print(f"新快捷键: {config['hotkey']['modifier']}+{config['hotkey']['key']}")
        except EOFError:
            print("⚠ 检测到非交互式输入，保持默认快捷键")
        
        print("\n3. UI配置")
        try:
            theme = input("选择主题 (dark/light) [默认: dark]: ").strip().lower()
            if theme in ["dark", "light"]:
                config["ui"]["theme"] = theme
            elif theme:
                print(f"无效主题，使用默认: dark")
        except EOFError:
            print("⚠ 检测到非交互式输入，使用默认主题: dark")
    else:
        print("\n⚠ 非交互式环境，使用默认配置")
        print("如需自定义配置，请手动编辑 config.yaml 文件")
    
    # 保存配置
    print("\n4. 保存配置")
    
    # 检查config.yaml是否存在
    config_path = "config.yaml"
    if os.path.exists(config_path):
        if interactive:
            try:
                backup = input("配置文件已存在，是否备份？(y/n): ").strip().lower()
                if backup == 'y':
                    import shutil
                    backup_path = f"config.yaml.backup"
                    shutil.copy2(config_path, backup_path)
                    print(f"✓ 已备份到: {backup_path}")
            except EOFError:
                print("⚠ 检测到非交互式输入，跳过备份")
        else:
            # 非交互式自动备份
            import shutil
            backup_path = f"config.yaml.backup.{int(time.time())}"
            shutil.copy2(config_path, backup_path)
            print(f"✓ 已自动备份到: {backup_path}")
    
    # 保存配置
    try:
        import yaml
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print(f"✓ 配置文件已保存: {config_path}")
        
        # 显示配置预览
        print("\n配置预览:")
        print(yaml.dump(config, default_flow_style=False, allow_unicode=True, sort_keys=False))
        
    except ImportError:
        # 如果yaml不可用，使用JSON格式
        config_path = "config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"✓ 配置文件已保存 (JSON格式): {config_path}")
        
        # 同时创建YAML占位文件
        with open("config.yaml", 'w', encoding='utf-8') as f:
            f.write("# 请安装PyYAML库后重新运行配置向导\n")
            f.write("# 或使用config.json文件\n")
        print("⚠ 需要安装PyYAML库以使用YAML格式配置文件")
    
    print("\n5. 依赖安装建议")
    print("运行以下命令安装必要依赖:")
    print("  pip install PyYAML")
    print("\n对于快捷键功能，建议安装:")
    print("  pip install 'pynput==1.7.3'  # Python 3.8兼容版本")
    print("\n对于完整AI功能，可选安装:")
    print("  pip install openai")
    
    print("\n配置完成！")
    print("\n运行测试:")
    print("  python3 test_installation.py")
    print("\n启动AI uTools:")
    print("  python3 main.py --test      # 运行功能测试")
    print("  python3 main.py             # 启动应用")

def main():
    """主函数"""
    print("AI uTools 配置向导")
    print("="*60)
    
    # 检查Python版本
    if not check_python_version():
        print("\n⚠ 请先升级Python版本到3.8+")
        return
    
    # 检查系统
    check_system()
    
    # 检查依赖
    check_dependencies()
    
    # 运行配置向导
    setup_configuration()
    
    print("\n" + "="*60)
    print("配置向导完成！")
    print("="*60)

if __name__ == "__main__":
    main()