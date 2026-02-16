#!/usr/bin/env python3
"""
AI agent模块 - 负责解析自然语言命令并生成可执行操作
"""
import json
import logging
import re
import time
from typing import Dict, Any, Optional, Tuple
import requests

from config import config


class AIAgent:
    """AI代理基类"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.system_prompt = config.get("ai.system_prompt", "")
        
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
    
    def parse_command(self, user_input: str) -> Dict[str, Any]:
        """
        解析用户输入的命令
        
        Args:
            user_input: 用户输入的自然语言命令
            
        Returns:
            解析后的结构化命令
        """
        raise NotImplementedError("子类必须实现此方法")
    
    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """
        从AI响应中提取JSON
        
        Args:
            response: AI返回的文本
            
        Returns:
            提取的JSON字典
        """
        # 尝试直接解析JSON
        try:
            return json.loads(response.strip())
        except json.JSONDecodeError:
            pass
        
        # 尝试提取代码块中的JSON
        json_pattern = r'```(?:json)?\s*(.*?)\s*```'
        matches = re.findall(json_pattern, response, re.DOTALL)
        
        for match in matches:
            try:
                return json.loads(match.strip())
            except json.JSONDecodeError:
                continue
        
        # 尝试提取大括号之间的JSON
        brace_pattern = r'\{.*?\}'
        matches = re.findall(brace_pattern, response, re.DOTALL)
        
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
        
        # 如果都没有，返回一个默认结构
        self.logger.warning(f"无法从响应中提取JSON: {response[:100]}...")
        return {
            "action": "unknown",
            "target": user_input if 'user_input' in locals() else response[:50],
            "parameters": {},
            "execution_command": "",
            "display_text": f"无法解析命令: {response[:50]}..."
        }


class OpenAIAgent(AIAgent):
    """OpenAI API代理"""
    
    def __init__(self):
        super().__init__()
        self.api_key = config.openai_api_key
        self.model = config.ai_model
        self.temperature = config.get("ai.temperature", 0.2)
        self.max_tokens = config.get("ai.max_tokens", 500)
        
        if not self.api_key:
            self.logger.warning("OpenAI API密钥未配置")
    
    def parse_command(self, user_input: str) -> Dict[str, Any]:
        """
        使用OpenAI API解析命令
        
        Args:
            user_input: 用户输入的自然语言命令
            
        Returns:
            解析后的结构化命令
        """
        if not self.api_key:
            return self._create_error_response("OpenAI API密钥未配置")
        
        try:
            # 构建消息
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_input}
            ]
            
            # 调用OpenAI API
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            response_text = response.choices[0].message.content
            
            # 提取JSON
            result = self._extract_json_from_response(response_text)
            
            # 添加原始输入
            result["original_input"] = user_input
            
            self.logger.info(f"OpenAI解析结果: {result}")
            return result
            
        except ImportError:
            self.logger.error("openai库未安装，请运行: pip install openai")
            return self._create_error_response("OpenAI库未安装")
        except openai.AuthenticationError:
            self.logger.error("OpenAI API认证失败")
            return self._create_error_response("OpenAI API认证失败")
        except openai.RateLimitError:
            self.logger.error("OpenAI API速率限制")
            return self._create_error_response("API调用过于频繁，请稍后再试")
        except Exception as e:
            self.logger.error(f"OpenAI API调用失败: {e}")
            return self._create_error_response(f"AI解析失败: {str(e)[:50]}")
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """创建错误响应"""
        return {
            "action": "error",
            "target": "",
            "parameters": {"error": error_message},
            "execution_command": "",
            "display_text": f"错误: {error_message}",
            "original_input": ""
        }


class DeepSeekAgent(AIAgent):
    """DeepSeek API代理"""
    
    def __init__(self):
        super().__init__()
        self.api_key = config.deepseek_api_key
        self.model = config.get("ai.deepseek_model", "deepseek-chat")
        self.temperature = config.get("ai.temperature", 0.2)
        self.max_tokens = config.get("ai.max_tokens", 500)
        
        if not self.api_key:
            self.logger.warning("DeepSeek API密钥未配置")
    
    def parse_command(self, user_input: str) -> Dict[str, Any]:
        """
        使用DeepSeek API解析命令
        
        Args:
            user_input: 用户输入的自然语言命令
            
        Returns:
            解析后的结构化命令
        """
        if not self.api_key:
            return self._create_error_response("DeepSeek API密钥未配置")
        
        try:
            # 构建消息
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_input}
            ]
            
            # 调用DeepSeek API（兼容OpenAI）
            import openai
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            response_text = response.choices[0].message.content
            
            # 提取JSON
            result = self._extract_json_from_response(response_text)
            
            # 添加原始输入
            result["original_input"] = user_input
            
            self.logger.info(f"DeepSeek解析结果: {result}")
            return result
            
        except ImportError:
            self.logger.error("openai库未安装，请运行: pip install openai")
            return self._create_error_response("OpenAI库未安装")
        except openai.AuthenticationError:
            self.logger.error("DeepSeek API认证失败")
            return self._create_error_response("DeepSeek API认证失败")
        except openai.RateLimitError:
            self.logger.error("DeepSeek API速率限制")
            return self._create_error_response("API调用过于频繁，请稍后再试")
        except Exception as e:
            self.logger.error(f"DeepSeek API调用失败: {e}")
            return self._create_error_response(f"AI解析失败: {str(e)[:50]}")
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """创建错误响应"""
        return {
            "action": "error",
            "target": "",
            "parameters": {"error": error_message},
            "execution_command": "",
            "display_text": f"错误: {error_message}",
            "original_input": ""
        }


class LocalAIAgent(AIAgent):
    """本地AI模型代理"""
    
    def __init__(self):
        super().__init__()
        self.model_path = config.get("ai.local_model.path", "models/llama-2-7b.Q4_K_M.gguf")
        self.context_size = config.get("ai.local_model.context_size", 2048)
        self.model = None
        
        # 延迟加载模型
        self._load_model()
    
    def _load_model(self):
        """加载本地模型"""
        try:
            from llama_cpp import Llama
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=self.context_size,
                verbose=False
            )
            self.logger.info(f"本地模型加载成功: {self.model_path}")
        except ImportError:
            self.logger.error("llama-cpp-python库未安装，请运行: pip install llama-cpp-python")
        except Exception as e:
            self.logger.error(f"加载本地模型失败: {e}")
    
    def parse_command(self, user_input: str) -> Dict[str, Any]:
        """
        使用本地模型解析命令
        
        Args:
            user_input: 用户输入的自然语言命令
            
        Returns:
            解析后的结构化命令
        """
        if self.model is None:
            return self._create_error_response("本地模型未加载")
        
        try:
            # 构建提示
            prompt = f"""你是一个macOS系统助手，负责解析用户命令并执行相应的系统操作。

用户命令: {user_input}

请以JSON格式回复，包含以下字段:
{{
  "action": "open_app|file_operation|search|calculate|system_control|query",
  "target": "具体目标",
  "parameters": {{ }},
  "execution_command": "实际执行的shell命令（如需要）",
  "display_text": "给用户的友好提示"
}}

只返回JSON，不要有其他文本。"""
            
            # 生成响应
            response = self.model(
                prompt,
                max_tokens=500,
                temperature=0.2,
                stop=["\n\n"]
            )
            
            response_text = response["choices"][0]["text"]
            
            # 提取JSON
            result = self._extract_json_from_response(response_text)
            
            # 添加原始输入
            result["original_input"] = user_input
            
            self.logger.info(f"本地模型解析结果: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"本地模型解析失败: {e}")
            return self._create_error_response(f"本地模型解析失败: {str(e)[:50]}")
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """创建错误响应"""
        return {
            "action": "error",
            "target": "",
            "parameters": {"error": error_message},
            "execution_command": "",
            "display_text": f"错误: {error_message}",
            "original_input": ""
        }


class SimpleRuleBasedAgent(AIAgent):
    """基于简单规则的代理（无AI依赖）"""
    
    def __init__(self):
        super().__init__()
        # 预定义命令模式
        self.command_patterns = {
            r'打开\s*(.+)': self._parse_open_app,
            r'启动\s*(.+)': self._parse_open_app,
            r'运行\s*(.+)': self._parse_open_app,
            r'搜索\s*(.+)': self._parse_search,
            r'谷歌\s*(.+)': self._parse_search,
            r'查找\s*(.+)': self._parse_search,
            r'计算\s*(.+)': self._parse_calculate,
            r'清空\s*废纸篓': self._parse_empty_trash,
            r'清空\s*垃圾桶': self._parse_empty_trash,
            r'显示\s*隐藏文件': self._parse_show_hidden,
            r'隐藏\s*隐藏文件': self._parse_hide_hidden,
            r'当前\s*时间': self._parse_current_time,
            r'现在\s*几点': self._parse_current_time,
        }
    
    def parse_command(self, user_input: str) -> Dict[str, Any]:
        """
        使用规则解析命令
        
        Args:
            user_input: 用户输入的自然语言命令
            
        Returns:
            解析后的结构化命令
        """
        self.logger.info(f"规则解析输入: {user_input}")
        
        # 尝试匹配预定义模式
        for pattern, parser in self.command_patterns.items():
            match = re.match(pattern, user_input, re.IGNORECASE)
            if match:
                result = parser(match, user_input)
                result["original_input"] = user_input
                self.logger.info(f"规则匹配结果: {result}")
                return result
        
        # 默认处理
        return self._parse_unknown(user_input)
    
    def _parse_open_app(self, match: re.Match, user_input: str) -> Dict[str, Any]:
        """解析打开应用命令"""
        app_name = match.group(1).strip()
        
        # 常见应用映射
        app_mapping = {
            "safari": "Safari",
            "浏览器": "Safari",
            "chrome": "Google Chrome",
            "谷歌浏览器": "Google Chrome",
            "firefox": "Firefox",
            "终端": "Terminal",
            "iterm": "iTerm",
            "finder": "Finder",
            "访达": "Finder",
            "vscode": "Visual Studio Code",
            "代码": "Visual Studio Code",
            "notes": "Notes",
            "备忘录": "Notes",
            "calendar": "Calendar",
            "日历": "Calendar",
            "mail": "Mail",
            "邮件": "Mail",
        }
        
        target_app = app_mapping.get(app_name.lower(), app_name)
        
        return {
            "action": "open_app",
            "target": target_app,
            "parameters": {"app_name": target_app},
            "execution_command": f"open -a '{target_app}'",
            "display_text": f"正在打开 {target_app}..."
        }
    
    def _parse_search(self, match: re.Match, user_input: str) -> Dict[str, Any]:
        """解析搜索命令"""
        query = match.group(1).strip()
        
        return {
            "action": "search",
            "target": query,
            "parameters": {"query": query, "engine": "google"},
            "execution_command": f"open 'https://www.google.com/search?q={query}'",
            "display_text": f"正在搜索: {query}"
        }
    
    def _parse_calculate(self, match: re.Match, user_input: str) -> Dict[str, Any]:
        """解析计算命令"""
        expression = match.group(1).strip()
        
        # 简单的表达式计算（注意安全）
        try:
            # 只允许安全字符
            safe_chars = set('0123456789+-*/(). ')
            if all(c in safe_chars for c in expression):
                result = eval(expression)  # 注意：在实际生产环境中应该使用更安全的计算方法
                return {
                    "action": "calculate",
                    "target": expression,
                    "parameters": {"expression": expression, "result": result},
                    "execution_command": "",
                    "display_text": f"{expression} = {result}"
                }
        except:
            pass
        
        return {
            "action": "calculate",
            "target": expression,
            "parameters": {"expression": expression},
            "execution_command": "",
            "display_text": f"计算: {expression}（使用计算器）"
        }
    
    def _parse_empty_trash(self, match: re.Match, user_input: str) -> Dict[str, Any]:
        """解析清空废纸篓命令"""
        return {
            "action": "system_control",
            "target": "empty_trash",
            "parameters": {},
            "execution_command": "osascript -e 'tell application \"Finder\" to empty trash'",
            "display_text": "正在清空废纸篓..."
        }
    
    def _parse_show_hidden(self, match: re.Match, user_input: str) -> Dict[str, Any]:
        """解析显示隐藏文件命令"""
        return {
            "action": "system_control",
            "target": "show_hidden_files",
            "parameters": {},
            "execution_command": "defaults write com.apple.finder AppleShowAllFiles YES && killall Finder",
            "display_text": "正在显示隐藏文件..."
        }
    
    def _parse_hide_hidden(self, match: re.Match, user_input: str) -> Dict[str, Any]:
        """解析隐藏隐藏文件命令"""
        return {
            "action": "system_control",
            "target": "hide_hidden_files",
            "parameters": {},
            "execution_command": "defaults write com.apple.finder AppleShowAllFiles NO && killall Finder",
            "display_text": "正在隐藏隐藏文件..."
        }
    
    def _parse_current_time(self, match: re.Match, user_input: str) -> Dict[str, Any]:
        """解析当前时间命令"""
        import datetime
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "action": "query",
            "target": "current_time",
            "parameters": {"time": current_time},
            "execution_command": "",
            "display_text": f"当前时间: {current_time}"
        }
    
    def _parse_unknown(self, user_input: str) -> Dict[str, Any]:
        """解析未知命令"""
        return {
            "action": "unknown",
            "target": user_input,
            "parameters": {},
            "execution_command": "",
            "display_text": f"无法理解命令: {user_input}",
            "original_input": user_input
        }


def create_ai_agent() -> AIAgent:
    """
    创建AI代理实例
    
    Returns:
        AI代理实例
    """
    provider = config.ai_provider.lower()
    
    if provider == "openai":
        agent = OpenAIAgent()
        # 检查API密钥
        if not agent.api_key:
            logging.warning("OpenAI API密钥未配置，回退到规则引擎")
            agent = SimpleRuleBasedAgent()
    elif provider == "deepseek":
        agent = DeepSeekAgent()
        # 检查API密钥
        if not agent.api_key:
            logging.warning("DeepSeek API密钥未配置，回退到规则引擎")
            agent = SimpleRuleBasedAgent()
    elif provider == "local":
        agent = LocalAIAgent()
        # 检查模型是否加载成功
        if agent.model is None:
            logging.warning("本地模型加载失败，回退到规则引擎")
            agent = SimpleRuleBasedAgent()
    else:
        # 默认使用规则引擎
        agent = SimpleRuleBasedAgent()
    
    logging.info(f"使用AI代理: {agent.__class__.__name__}")
    return agent


if __name__ == "__main__":
    # 测试代码
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # 测试不同代理
    test_inputs = [
        "打开Safari",
        "搜索机器学习",
        "计算15+23",
        "清空废纸篓",
        "当前时间",
    ]
    
    # 创建规则代理
    agent = SimpleRuleBasedAgent()
    
    for test_input in test_inputs:
        print(f"\n输入: {test_input}")
        result = agent.parse_command(test_input)
        print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 测试OpenAI代理（如果有API密钥）
    if config.openai_api_key or os.getenv("OPENAI_API_KEY"):
        print("\n\n测试OpenAI代理...")
        openai_agent = OpenAIAgent()
        result = openai_agent.parse_command("打开终端并搜索Python教程")
        print(f"OpenAI结果: {json.dumps(result, ensure_ascii=False, indent=2)}")