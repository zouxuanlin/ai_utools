# AI uTools - macOS智能启动器

一个类似uTools的macOS工具，通过快捷键打开，输入自然语言命令，由AI agent解析并执行系统操作。

## 功能特性

- **全局快捷键**: 默认 `Cmd+Shift+P` 打开/关闭启动器
- **智能命令解析**: 使用AI（OpenAI GPT、DeepSeek或本地模型）理解自然语言指令
- **系统操作执行**: 执行文件操作、打开应用、搜索、计算等
- **简洁UI**: 类似Alfred的浮动输入框
- **可扩展**: 支持插件系统

## 安装与运行

### 前置要求
- macOS 10.15+（推荐macOS 12+）
- Python 3.8+
- 可选API密钥：
  - OpenAI API密钥（如果使用OpenAI GPT）
  - DeepSeek API密钥（如果使用DeepSeek AI）
  - 如使用本地模型或规则引擎则不需要API密钥

### 安装步骤

1. 克隆仓库
```bash
git clone <repository>
cd ai_utools
```

2. 安装依赖（推荐使用虚拟环境）
```bash
# 创建虚拟环境（可选）
python3 -m venv venv
source venv/bin/activate

# 安装核心依赖
pip install -r requirements.txt

# 如果安装失败（特别是pynput或pyobjc），尝试降级版本：
# pip install 'pynput==1.7.3' 'pyobjc-core<9.0' 'pyobjc-framework-Cocoa<9.0' 'pyobjc-framework-Quartz<9.0'
```

3. 配置应用
```bash
# 运行配置向导（交互式）
python3 run_setup.py

# 或手动编辑配置文件
# 编辑 config.yaml 文件，设置API密钥等
# 使用环境变量设置API密钥（推荐）：
export DEEPSEEK_APIKEY="your_deepseek_api_key"
export OPENAI_API_KEY="your_openai_api_key"
```

4. 测试运行
```bash
# 测试基本功能（无UI）
python3 main.py --test

# 完整运行（需要GUI支持）
python3 main.py
```

5. 设置为开机启动（可选）
```bash
# 将应用添加到登录项
python3 main.py --install-autostart
# 或
python3 run_setup.py --install-autostart
```

### 故障排除

#### 1. pynput/pyobjc安装失败
如果在Python 3.8或旧版macOS上安装失败，使用降级版本：
```bash
pip uninstall pynput pyobjc-framework-Quartz pyobjc-framework-Cocoa pyobjc-core
pip install 'pynput==1.7.3' 'pyobjc-core<9.0' 'pyobjc-framework-Cocoa<9.0' 'pyobjc-framework-Quartz<9.0'
```

#### 2. 快捷键监听失败
如果全局快捷键无法工作，应用会自动切换到虚拟快捷键模式，仍可通过UI测试功能。

#### 3. 配置向导EOFError
如果在非交互式环境运行配置向导，使用环境变量或直接编辑`config.yaml`文件。

#### 4. DeepSeek API密钥配置
确保设置了环境变量：
```bash
export DEEPSEEK_APIKEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```
或在`config.yaml`中设置：
```yaml
ai:
  provider: "deepseek"
  deepseek_api_key: "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

## 配置

### 快捷键配置
在 `config.yaml` 中修改：
```yaml
hotkey:
  modifier: ["command", "shift"]
  key: "p"
```

### AI配置
```yaml
ai:
  provider: "deepseek"  # 可选: "openai", "deepseek", "local", "rule"
  openai_api_key: ""   # 留空则从环境变量OPENAI_API_KEY读取
  deepseek_api_key: ""   # 留空则从环境变量DEEPSEEK_APIKEY读取
  model: "gpt-4o-mini"  # OpenAI模型
  deepseek_model: "deepseek-chat"  # DeepSeek模型
  local_model:
    path: "models/llama-2-7b.Q4_K_M.gguf"
```

## 使用示例

1. 按下 `Cmd+Shift+P` 打开启动器
2. 输入自然语言命令：
   - "打开Safari浏览器"
   - "搜索关于机器学习的最新文章"
   - "计算15%的小费"
   - "清空废纸篓"
3. AI将解析命令并执行相应操作

## 开发

### 项目结构
```
ai_utools/
├── main.py              # 主程序入口
├── hotkey_manager.py    # 全局快捷键管理
├── launcher_ui.py       # UI启动器界面
├── ai_agent.py          # AI agent集成
├── system_executor.py   # 系统操作执行
├── config.py            # 配置管理
├── plugins/             # 插件目录
├── requirements.txt     # Python依赖
└── README.md           # 说明文档
```

### 添加新插件
在 `plugins/` 目录下创建Python文件，实现 `execute(command: str) -> str` 函数。

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request。
