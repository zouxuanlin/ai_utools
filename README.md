# AI uTools - macOS智能启动器

一个类似uTools的macOS工具，通过快捷键打开，输入自然语言命令，由AI agent解析并执行系统操作。

## 功能特性

- **全局快捷键**: 默认 `Cmd+Shift+P` 打开/关闭启动器
- **智能命令解析**: 使用AI（OpenAI GPT或本地模型）理解自然语言指令
- **系统操作执行**: 执行文件操作、打开应用、搜索、计算等
- **简洁UI**: 类似Alfred的浮动输入框
- **可扩展**: 支持插件系统

## 安装与运行

### 前置要求
- macOS 10.15+
- Python 3.8+
- OpenAI API密钥（可选，如使用本地模型则不需要）

### 安装步骤

1. 克隆仓库
```bash
git clone <repository>
cd ai_utools
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置API密钥
```bash
cp config.example.yaml config.yaml
# 编辑config.yaml，填入OpenAI API密钥
```

4. 运行
```bash
python main.py
```

5. 设置为开机启动（可选）
```bash
# 将应用添加到登录项
python setup.py --install-autostart
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
  provider: "openai"  # 或 "local"
  openai_api_key: "your-api-key"
  model: "gpt-4o-mini"
  local_model_path: "models/llama-2-7b.Q4_K_M.gguf"
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
