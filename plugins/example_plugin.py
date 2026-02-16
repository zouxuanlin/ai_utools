#!/usr/bin/env python3
"""
示例插件 - 演示如何创建AI uTools插件
"""
import os
import subprocess
from typing import Dict, Any


def get_plugin_info() -> Dict[str, Any]:
    """
    返回插件信息
    
    Returns:
        插件信息字典
    """
    return {
        "name": "示例插件",
        "version": "1.0.0",
        "description": "演示插件，提供一些示例命令",
        "author": "AI uTools",
        "commands": [
            {
                "name": "问候",
                "description": "向用户问好",
                "pattern": r"^(你好|hello|hi|打招呼)"
            },
            {
                "name": "天气查询",
                "description": "查询天气信息",
                "pattern": r"^(天气|weather|查询天气)"
            },
            {
                "name": "笑话",
                "description": "讲一个笑话",
                "pattern": r"^(笑话|讲个笑话|funny)"
            }
        ]
    }


def execute(command: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    执行插件命令
    
    Args:
        command: 用户输入的命令
        parameters: 额外参数（可选）
        
    Returns:
        执行结果字典
    """
    if parameters is None:
        parameters = {}
    
    # 根据命令模式执行相应操作
    if any(word in command.lower() for word in ["你好", "hello", "hi", "打招呼"]):
        return _greet_user(command)
    
    elif any(word in command.lower() for word in ["天气", "weather", "查询天气"]):
        return _get_weather(command)
    
    elif any(word in command.lower() for word in ["笑话", "讲个笑话", "funny"]):
        return _tell_joke(command)
    
    else:
        return {
            "action": "unknown",
            "target": command,
            "parameters": parameters,
            "execution_command": "",
            "display_text": f"示例插件无法处理命令: {command}"
        }


def _greet_user(command: str) -> Dict[str, Any]:
    """问候用户"""
    import datetime
    
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        greeting = "早上好！"
    elif 12 <= hour < 18:
        greeting = "下午好！"
    else:
        greeting = "晚上好！"
    
    return {
        "action": "query",
        "target": "greeting",
        "parameters": {"greeting": greeting},
        "execution_command": "",
        "display_text": f"{greeting} 我是AI uTools助手，有什么可以帮您？"
    }


def _get_weather(command: str) -> Dict[str, Any]:
    """获取天气信息"""
    # 在实际应用中，这里可以调用天气API
    # 这里只是返回示例数据
    
    import datetime
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 模拟天气数据
    weather_data = {
        "location": "上海",
        "temperature": "22°C",
        "condition": "晴朗",
        "humidity": "65%",
        "wind": "东南风 3级"
    }
    
    return {
        "action": "query",
        "target": "weather",
        "parameters": weather_data,
        "execution_command": "",
        "display_text": f"当前天气 ({current_time}):\n"
                       f"地点: {weather_data['location']}\n"
                       f"温度: {weather_data['temperature']}\n"
                       f"天气: {weather_data['condition']}\n"
                       f"湿度: {weather_data['humidity']}\n"
                       f"风力: {weather_data['wind']}"
    }


def _tell_joke(command: str) -> Dict[str, Any]:
    """讲一个笑话"""
    jokes = [
        "为什么程序员总是分不清万圣节和圣诞节？\n因为 Oct 31 == Dec 25！",
        "为什么Java程序员要戴眼镜？\n因为他们不能C#！",
        "问：如何生成一个随机字符串？\n答：让新手退出Vim。",
        "为什么Python程序员很少得感冒？\n因为他们有强大的import免疫系统！",
        "两个比特在散步，一个比特对另一个比特说：\n『我们要不要找个地方坐一下？』",
    ]
    
    import random
    joke = random.choice(jokes)
    
    return {
        "action": "query",
        "target": "joke",
        "parameters": {"joke": joke},
        "execution_command": "",
        "display_text": f"笑话时间:\n{joke}"
    }


def register_commands(plugin_manager):
    """
    向插件管理器注册命令
    
    Args:
        plugin_manager: 插件管理器实例
    """
    plugin_info = get_plugin_info()
    
    for cmd in plugin_info["commands"]:
        plugin_manager.register_command(
            pattern=cmd["pattern"],
            handler=lambda c, p=cmd: execute(c),
            description=cmd["description"]
        )
    
    print(f"示例插件已注册: {plugin_info['name']} v{plugin_info['version']}")


if __name__ == "__main__":
    # 测试插件
    print("测试示例插件:")
    
    test_commands = [
        "你好",
        "天气怎么样",
        "讲个笑话",
        "测试命令"
    ]
    
    for cmd in test_commands:
        print(f"\n命令: {cmd}")
        result = execute(cmd)
        print(f"结果: {result.get('display_text', '无结果')[:50]}...")