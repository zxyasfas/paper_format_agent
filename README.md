# Paper Format Agent

> 面向高校毕业论文格式修订的自动化引擎（规则引擎 + LLM 辅助）

`Paper Format Agent` 用于将学生提交的 `.docx` 论文自动修复为符合学校规范的版式，重点解决：
- 手工目录错位
- 标题层级混乱
- 页边距/行距/字体不一致
- 页码与编号元数据污染（黑方块）
- 评分与人工观感差异过大

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

## 快速开始

### 1) 安装

```bash
pip install -r requirements.txt
```

### 2) 运行（推荐 V3）

```bash
python -m paper_format_agent_v3.cli \
  --format-file "<school_format.docx>" \
  --paper-file "<student_paper.docx>" \
  --out-dir "./sample_output/run_v3" \
  --engine auto \
  --marker-dump
```

### 3) 严格评分（模板必需项）

```bash
python -m paper_format_agent_v3.cli \
  --format-file "<school_format.docx>" \
  --paper-file "<student_paper.docx>" \
  --out-dir "./sample_output/run_v3_strict" \
  --engine auto \
  --strict-required-sections
```

## 输出物

- `formatted_paper_v3.docx`：修复后的论文
- `format_report.json` / `format_report.html`：评分与特征报告
- `modify_log.json`：每一轮修复日志
- `marker_dump.json`：段落类型识别明细（启用时）

## 架构概览

```text
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
- [README_V3.md](README_V3.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## 设计原则

- 默认不改论文学术内容，仅改格式
- 先可控再智能：LLM 只做建议，最终由规则二次校验
- 所有评分项可追溯到具体 penalty

## 开源协作

- 贡献指南：[CONTRIBUTING.md](CONTRIBUTING.md)
- 安全策略：[SECURITY.md](SECURITY.md)
- 路线图：[ROADMAP.md](ROADMAP.md)
- 许可证：[LICENSE](LICENSE)

## 免责声明

本项目用于格式修订与教学辅助，不替代导师学术审查。请在提交前进行人工复核。
