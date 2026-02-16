#!/usr/bin/env python3
"""
配置文件管理模块
"""
import os
import yaml
from pathlib import Path
from typing import Any, Dict


class Config:
    """配置管理类"""
    
    _instance = None
    _config: Dict[str, Any] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        config_path = self._get_config_path()
        
        # 默认配置
        default_config = {
            "hotkey": {
                "modifier": ["command", "shift"],
                "key": "p",
                "enabled": True
            },
            "ai": {
                "provider": "openai",
                "openai_api_key": "",
                "model": "gpt-4o-mini",
                "temperature": 0.2,
                "max_tokens": 500,
                "local_model": {
                    "path": "models/llama-2-7b.Q4_K_M.gguf",
                    "context_size": 2048
                },
                "system_prompt": """你是一个macOS系统助手，负责解析用户命令并执行相应的系统操作。
用户会输入自然语言命令，你需要将其解析为具体的操作指令。
支持的操作类型：
1. 打开应用：如"打开Safari"、"启动终端"
2. 文件操作：如"打开文档文件夹"、"删除test.txt"
3. 搜索：如"搜索机器学习"、"谷歌AI新闻"
4. 计算：如"计算15%的小费"、"100美元换算成人民币"
5. 系统控制：如"清空废纸篓"、"睡眠显示器"
6. 信息查询：如"当前时间"、"天气情况"

请以JSON格式回复，包含以下字段：
{
  "action": "open_app|file_operation|search|calculate|system_control|query",
  "target": "具体目标",
  "parameters": { },
  "execution_command": "实际执行的shell命令（如需要）",
  "display_text": "给用户的友好提示"
}"""
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
            },
            "plugins": {
                "enabled": True,
                "directory": "plugins",
                "auto_load": True
            },
            "logging": {
                "level": "INFO",
                "file": "logs/ai_utools.log",
                "max_size_mb": 10,
                "backup_count": 5
            }
        }
        
        try:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                    # 合并配置
                    self._merge_configs(default_config, user_config)
            else:
                self._config = default_config
                # 创建示例配置文件
                self._create_example_config(config_path)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            self._config = default_config
    
    def _merge_configs(self, default: Dict, user: Dict):
        """深度合并配置"""
        import copy
        self._config = copy.deepcopy(default)
        
        def merge(dest, src):
            for key, value in src.items():
                if key in dest and isinstance(dest[key], dict) and isinstance(value, dict):
                    merge(dest[key], value)
                else:
                    dest[key] = value
        
        merge(self._config, user)
    
    def _get_config_path(self) -> Path:
        """获取配置文件路径"""
        # 首先检查当前目录
        current_dir = Path.cwd() / "config.yaml"
        if current_dir.exists():
            return current_dir
        
        # 检查用户配置目录
        home = Path.home()
        config_dir = home / ".config" / "ai_utools"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "config.yaml"
    
    def _create_example_config(self, config_path: Path):
        """创建示例配置文件"""
        config_dir = config_path.parent
        config_dir.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        print(f"已创建示例配置文件: {config_path}")
        print("请编辑该文件并设置您的OpenAI API密钥和其他配置。")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        config = self._config
        
        for i, k in enumerate(keys[:-1]):
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self):
        """保存配置到文件"""
        config_path = self._get_config_path()
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    @property
    def hotkey_modifier(self):
        """获取快捷键修饰键"""
        return self.get("hotkey.modifier", ["command", "shift"])
    
    @property
    def hotkey_key(self):
        """获取快捷键键位"""
        return self.get("hotkey.key", "p")
    
    @property
    def openai_api_key(self):
        """获取OpenAI API密钥"""
        key = self.get("ai.openai_api_key", "")
        if not key:
            # 从环境变量读取
            key = os.getenv("OPENAI_API_KEY", "")
        return key
    
    @property
    def ai_provider(self):
        """获取AI提供商"""
        return self.get("ai.provider", "openai")
    
    @property
    def ai_model(self):
        """获取AI模型"""
        return self.get("ai.model", "gpt-4o-mini")


# 全局配置实例
config = Config()