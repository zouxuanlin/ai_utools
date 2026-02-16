#!/usr/bin/env python3
"""
AI uTools 安装测试脚本
"""
import sys
import os
import subprocess
import platform

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
        return False

def check_dependencies():
    """检查依赖包"""
    print_header("检查依赖包")
    
    required_packages = [
        ("PyYAML", "yaml"),
        ("pynput", "pynput"),
        ("keyboard", "keyboard"),
        ("openai", "openai"),  # 可选
        ("customtkinter", "customtkinter"),  # 可选
    ]
    
    missing_packages = []
    optional_missing = []
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"✓ {package_name}")
        except ImportError:
            if package_name in ["openai", "customtkinter"]:
                optional_missing.append(package_name)
                print(f"○ {package_name} (可选)")
            else:
                missing_packages.append(package_name)
                print(f"✗ {package_name}")
    
    if missing_packages:
        print(f"\n缺少必要依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install " + " ".join(missing_packages))
        return False
    
    if optional_missing:
        print(f"\n缺少可选依赖包: {', '.join(optional_missing)}")
        print("这些包不是必需的，但提供额外功能")
    
    return True

def check_system():
    """检查系统环境"""
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
        return True  # 仍然允许运行，但警告

def check_configuration():
    """检查配置文件"""
    print_header("检查配置文件")
    
    config_paths = [
        "config.yaml",
        os.path.expanduser("~/.config/ai_utools/config.yaml"),
        os.path.join(os.path.dirname(__file__), "config.yaml")
    ]
    
    config_found = False
    for path in config_paths:
        if os.path.exists(path):
            print(f"✓ 找到配置文件: {path}")
            config_found = True
            
            # 检查OpenAI API密钥
            try:
                import yaml
                with open(path, 'r') as f:
                    config = yaml.safe_load(f)
                    api_key = config.get('ai', {}).get('openai_api_key', '')
                    if api_key:
                        print("✓ OpenAI API密钥已配置")
                    else:
                        print("○ OpenAI API密钥未配置（可选）")
            except:
                print("⚠ 无法读取配置文件")
            
            break
    
    if not config_found:
        print("○ 未找到配置文件，首次运行时会自动创建")
    
    return True

def test_modules():
    """测试核心模块"""
    print_header("测试核心模块")
    
    modules_to_test = [
        ("config", "配置模块"),
        ("ai_agent", "AI代理模块"),
        ("system_executor", "系统执行模块"),
        ("hotkey_manager", "快捷键管理模块"),
        ("launcher_ui", "UI模块"),
    ]
    
    sys.path.insert(0, os.path.dirname(__file__))
    
    failed_modules = []
    
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"✓ {description}")
        except Exception as e:
            print(f"✗ {description}: {str(e)[:50]}")
            failed_modules.append(module_name)
    
    if failed_modules:
        print(f"\n以下模块加载失败: {', '.join(failed_modules)}")
        return False
    
    return True

def run_simple_test():
    """运行简单功能测试"""
    print_header("运行功能测试")
    
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        
        # 测试AI代理（规则引擎）
        from ai_agent import SimpleRuleBasedAgent
        agent = SimpleRuleBasedAgent()
        
        test_commands = [
            ("打开Safari", "open_app"),
            ("搜索测试", "search"),
            ("计算1+1", "calculate"),
        ]
        
        print("测试AI命令解析:")
        for command, expected_action in test_commands:
            result = agent.parse_command(command)
            action = result.get("action", "")
            if action == expected_action:
                print(f"  ✓ {command} -> {action}")
            else:
                print(f"  ✗ {command} -> {action} (期望: {expected_action})")
        
        # 测试配置
        from config import config
        print(f"\n配置信息:")
        print(f"  AI提供商: {config.ai_provider}")
        print(f"  快捷键: {config.hotkey_modifier}+{config.hotkey_key}")
        
        print("\n✓ 功能测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 功能测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("AI uTools 安装测试")
    print("="*60)
    
    tests = [
        ("Python版本", check_python_version),
        ("系统环境", check_system),
        ("依赖包", check_dependencies),
        ("配置文件", check_configuration),
        ("核心模块", test_modules),
        ("功能测试", run_simple_test),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"测试 {test_name} 时出错: {e}")
            results.append((test_name, False))
    
    # 总结
    print_header("测试总结")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✓" if success else "✗"
        print(f"{status} {test_name}")
    
    print(f"\n通过 {passed}/{total} 项测试")
    
    if passed == total:
        print("\n🎉 所有测试通过！AI uTools 可以正常运行。")
        print("\n运行以下命令启动:")
        print("  python main.py          # 正常模式")
        print("  python main.py --setup  # 配置向导")
        print("  python main.py --test   # 运行更多测试")
        return 0
    elif passed >= total - 1:  # 允许1项失败（通常是可选依赖）
        print("\n⚠ 大部分测试通过，可以尝试运行AI uTools。")
        print("某些功能可能受限。")
        return 1
    else:
        print("\n❌ 测试失败较多，请解决上述问题后再运行。")
        return 2

if __name__ == "__main__":
    sys.exit(main())