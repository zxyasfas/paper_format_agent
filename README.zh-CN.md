# Paper Format Agent 中文说明

[English](README.md) | 中文

![本地优先](https://img.shields.io/badge/本地优先-DOCX-blue)
![内容保护](https://img.shields.io/badge/内容保护-默认开启-green)
![Python](https://img.shields.io/badge/python-3.9%2B-3776AB)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

Paper Format Agent 是一个本地优先的论文格式修改工具，面向毕业论文、课程论文、期刊投稿和会议论文的 DOCX 格式整理场景。它会从格式说明中抽取规则，自动修复论文排版，并生成机器可读与人工可读的检查报告。

核心原则很简单：只改格式，不改学术内容。

## 一屏了解

| 能力 | 说明 |
| --- | --- |
| 格式规则抽取 | 从 `.docx`、`.doc`、`.txt` 格式说明中提取页边距、字体、字号、行距、标题、摘要、关键词等规则 |
| DOCX 自动修复 | 修复正文、标题、目录、摘要、关键词、图表标题、参考文献、页眉页脚和页码等常见排版问题 |
| 内容保护 | 默认启用内容指纹检查，防止格式化过程误改正文内容 |
| 评分报告 | 输出 `format_report.json` 和 `format_report.html`，展示分数、扣分项、证据和修复建议 |
| 批量处理 | 支持对一个目录中的多篇论文批量格式化，并生成 `batch_summary.json` |
| 本地运行 | 默认不上传论文、模板或审稿意见，适合处理隐私敏感的学术文档 |
| Agent Skill | 内置 `SKILL.md` 和 `agents/openai.yaml`，可作为智能体工作流技能使用 |

## 适合谁

- 学生：毕业论文、课程论文、开题报告、期刊投稿前的格式自查。
- 导师或助教：批量检查学生论文格式，快速定位共性问题。
- 学术服务团队：搭建本地化、可审计的论文格式处理流程。
- 开源贡献者：添加学校、期刊、会议模板规则和回归测试。

## 当前成熟度

当前项目适合开源展示、内部试用、简历项目和小规模真实样本验证。它还不能直接承诺为完全商用级产品。

要达到更稳妥的商用状态，建议继续补齐：

- 更大的合成回归样本集，覆盖不同学校、期刊和会议模板。
- 表格、图片、公式、脚注、页眉、页脚、参考文献的更细粒度评分。
- PDF 渲染后的视觉比对能力。
- 版本化模板包和更完整的用户错误提示。
- 更严格的发布流程和真实环境灰度测试。

## 快速开始

安装依赖：

```bash
pip install -r requirements.txt
```

格式化单篇论文：

```bash
python -m paper_format_agent.cli \
  --format-file "format_guide.docx" \
  --paper-file "paper.docx" \
  --out-dir "./output" \
  --engine auto \
  --strict-required-sections
```

启动可选 GUI：

```bash
python run_gui.py
```

## 批量处理

对一个目录内的多篇论文统一处理：

```bash
python -m paper_format_agent.cli \
  --format-file "format_guide.docx" \
  --paper-dir "./papers" \
  --out-dir "./batch_output" \
  --engine python \
  --strict-required-sections
```

批量模式会为每篇论文创建独立输出目录，并额外生成：

```text
batch_summary.json
```

其中包含：

- 总论文数、通过数、失败数、通过率。
- 平均格式化前分数、平均格式化后分数、平均提升。
- 内容是否被意外改变。
- 每篇论文的输出目录和报告路径。

## 输出文件

| 文件 | 用途 |
| --- | --- |
| `formatted_paper_v3.docx` | 格式修复后的 DOCX 文件 |
| `format_rules.json` | 从格式说明中提取出的结构化规则 |
| `format_report.json` | 机器可读的评分、扣分项、诊断信息 |
| `format_report.html` | 适合人工阅读的格式检查报告 |
| `modify_log.json` | 格式修改操作日志 |
| `engine_report.json` | Word COM、LibreOffice 或 Python 后处理结果 |
| `marker_dump.json` | 可选的段落分类调试信息 |
| `batch_summary.json` | 批量处理汇总报告 |

## 安全模型

项目默认启用内容保护。报告中会包含：

- `content_changed`
- `content_guard_enforced`
- `content_fingerprint_before`
- `content_fingerprint_after`
- `diagnostics`

正常格式化场景下，`content_changed` 应该为 `false`。如果它变成 `true`，说明格式化过程可能改变了正文内容，需要人工复核。

## 质量验证

提交代码或发布前建议运行：

```bash
python tools/validate_skill.py
python -m unittest discover -s tests -p "test_*.py"
python tools/compile_check.py
python tools/release_audit.py
```

`tools/release_audit.py` 会检查是否误提交了本地输出、缓存、临时文件、密钥或真实 DOCX/PDF 文档，降低开源发布风险。

## 架构概览

```text
格式说明 + 原始论文 DOCX
  -> 规则抽取
  -> 段落类型识别
  -> 样式和版式修复
  -> 编号与页眉页脚处理
  -> 可选后处理引擎
  -> 评分与报告输出
```

更多设计文档：

- [架构说明](docs/ARCHITECTURE.md)
- [商用成熟度标准](docs/PRODUCTION_STANDARD.md)
- [用户痛点分析](docs/USER_PAIN_ANALYSIS.md)
- [路线图](ROADMAP.md)

## 隐私约束

不要提交真实论文、学校私有模板、审稿意见、API Key、生成的 DOCX/PDF 或本地输出目录。测试应优先使用合成样本和短规则片段。

## 贡献方向

适合贡献的小任务：

- 添加某个学校、期刊或会议模板的合成测试。
- 改进规则抽取逻辑。
- 增加表格、图题、表题、公式、脚注、参考文献的评分覆盖。
- 改进 `format_report.html` 的可读性。
- 增加 GitHub Actions、MCP、本地批处理等集成能力。

## License

MIT. See [LICENSE](LICENSE).
