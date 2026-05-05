# Paper Format Agent

> 面向高校毕业论文格式修订的自动化引擎（规则引擎 + LLM 辅助）

`Paper Format Agent` 用于将学生提交的 `.docx` 论文自动修复为符合学校规范的版式，重点解决：
- 手工目录错位
- 标题层级混乱
- 页边距/行距/字体不一致
- 页码与编号元数据污染（黑方块）
- 评分与人工观感差异过大

## ✨ 全新交互界面

现已支持精美的图形界面，操作更简单直观！

![GUI Preview](docs/gui_preview.png)

## 核心能力

- `V3 type-tag pipeline`：先识别段落类型，再应用样式，最后清理标记
- `Hybrid strategy`：
  - 规则引擎：可验证格式（页边距、字体、行距、标题、编号元数据）
  - LLM：弱结构识别建议（可选，默认不改正文内容）
- `Strict / Loose scoring`：
  - 严格模式：按模板必需项打分
  - 宽松模式：按原文基线打分（原文没有的项不强制扣分）
- `Engine fallback`：`word-com -> libreoffice -> python`

## 适用场景

- 学生毕业论文格式统一修订
- 学院批量初审格式质检
- 指导老师版式问题快速定位

## 🚀 快速开始

### 方式一：图形界面（推荐）

```bash
# 安装依赖
pip install -r requirements.txt

# 启动 GUI
python run_gui.py

# 或者
python -m paper_format_agent
```

**GUI 特色功能：**
- 🎯 拖拽上传文件支持
- 📊 实时进度显示
- 🎨 现代化 Material Design 界面
- 📁 一键查看报告和输出目录
- ✅ 智能状态提示

### 方式二：命令行

```bash
# 安装
pip install -r requirements.txt

# 基础运行
python -m paper_format_agent.cli \
  --format-file "格式规范.docx" \
  --paper-file "论文.docx" \
  --out-dir "./output" \
  --engine auto

# 严格模式
python -m paper_format_agent.cli \
  --format-file "格式规范.docx" \
  --paper-file "论文.docx" \
  --out-dir "./output" \
  --engine auto \
  --strict-required-sections
```

## 📋 命令行参数

| 参数 | 说明 | 必填 |
|------|------|------|
| `--format-file` | 格式规范文件（.doc/.docx/.txt） | ✅ |
| `--paper-file` | 论文文件（.docx） | ✅ |
| `--out-dir` | 输出目录 | ✅ |
| `--engine` | 引擎选择：auto/word-com/libreoffice/python | 可选 |
| `--strict-required-sections` | 严格模式 | 可选 |
| `--marker-dump` | 输出段落类型识别明细 | 可选 |

## 📦 输出文件

| 文件名 | 说明 |
|--------|------|
| `formatted_paper.docx` | 📄 排版后的论文 |
| `format_report.html` | 📊 可视化检测报告 |
| `format_report.json` | 📋 详细检测数据 |
| `format_rules.json` | 📐 提取的格式规则 |
| `modify_log.json` | 📝 修改日志 |
| `marker_dump.json` | 🏷️ 段落类型识别明细（可选）|

## 🏗️ 架构概览

```
Input docx
  -> Classifier (type tags)
  -> Reorder (when confident)
  -> Style applier
  -> Numbering cleanup
  -> Optional engine postprocess
  -> Scorer (strict/loose)
  -> Reports
```

详见：
- [README_V3.md](README_V3.md) - V3 版本详细说明
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - 架构文档
- [SDD.md](SDD.md) - 软件设计文档

## ⚠️ 注意事项

1. **LibreOffice（可选）**
   - 用于 `.doc` 转 `.docx`
   - 用于自动更新目录和页码
   - 如果没有安装，程序会自动降级使用 Python 引擎

2. **文件格式**
   - 输入论文必须是 `.docx` 格式
   - 格式规范支持 `.doc`、`.docx`、`.txt`

3. **Windows 路径**
   - 路径包含空格时请使用引号包裹

## 🛠️ 开发

```bash
# 克隆项目
git clone https://github.com/zxyasfas/paper_format_agent.git
cd paper_format_agent

# 安装开发依赖
pip install -r requirements.txt

# 运行测试
python -m paper_format_agent.cli --help
```

## 🤝 开源协作

- 贡献指南：[CONTRIBUTING.md](CONTRIBUTING.md)
- 安全策略：[SECURITY.md](SECURITY.md)
- 路线图：[ROADMAP.md](ROADMAP.md)
- 许可证：[LICENSE](LICENSE)

## 📝 免责声明

本项目用于格式修订与教学辅助，不替代导师学术审查。请在提交前进行人工复核。

---

Made with ❤️ for better academic writing
