<!-- mcp-name: io.github.zxyasfas/paper-format-agent -->

# Paper Format Agent

中文说明 | [English](README.md)

![CI](https://github.com/zxyasfas/paper_format_agent/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-3776AB)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

本地运行的 DOCX 论文自动排版工具，适用于毕业论文、学位论文的 Word 格式修改。

它按论文格式要求改字体字号、缩进、行距、标题和题注，不改论文内容。保存前会对比
排版前后正文和表格文字的指纹，文字变了就直接报错退出，不写出排版后的文件。

全程在本机运行，不上传任何文件。

## 内容校验

一次真实运行（`--engine python`）产出的报告字段：

```json
{
  "content_fingerprint_before": "793e6533fd670418141d11fdcf014be19750408129ecff8b1b78a2641a3786db",
  "content_fingerprint_after":  "793e6533fd670418141d11fdcf014be19750408129ecff8b1b78a2641a3786db",
  "content_changed": false,
  "content_guard_enforced": true
}
```

两个指纹应当一致。不一致时程序以 `content guard failed` 退出，不写出排版后
的 DOCX。

校验范围：正文段落和表格，对比前会归一化空白字符和残留的项目符号。页眉页脚
是排版本来就要改的，不在校验范围内。要让指纹覆盖最终保存的 DOCX，就用
`--engine python`；其他引擎会在指纹计算之后再跑一次本地后处理（比如刷新
目录）。

想看护栏拦截的样子，可以跑 `python tools/demo_content_guard.py`：先正常排版
一篇合成论文，再把排版步骤换成会顺手改动一句话的版本重跑，第二次运行会直接
中止，不写出 DOCX。

[docs/BENCHMARK.md](docs/BENCHMARK.md) 记录合成用例里各类文字经过一次排版后
的严格匹配结果，以及已知还没覆盖到的对象。

## 安装和运行

```bash
pip install -r requirements.txt

python -m paper_format_agent.cli \
  --format-file "format_guide.docx" \
  --paper-file "paper.docx" \
  --out-dir "./output" \
  --engine python
```

另有 GUI（`python run_gui.py`）、批量模式，以及中文学位论文、期刊、IEEE
会议三类 JSON 模板包，见 [docs/USAGE.md](docs/USAGE.md)。

## 局限

项目还早。普通段落、标题和表格的效果比公式、脚注、复杂版式好。开启
`--strict-required-sections` 时，报告里可能出现 `char_below_min`、
`blank_page_risk` 这类检查项。正式提交前别把它当唯一检查，留好原文件。

## 为什么做这个

我不想把没写完的论文传到排版网站上，也想有个办法确认排版没动过正文。所以
默认引擎在本地跑，文字变了就拒绝保存。

## agent 支持

仓库本身是可安装的 agent skill（[SKILL.md](SKILL.md)），也可以通过可选的
MCP server 调用（需要 Python 3.10+）：

```bash
pip install "paper-format-agent[mcp]"
paper-format-agent-mcp
```

工具：`format_paper`（排版）、`extract_format_rules`（从格式要求文档提取规则）、`score_paper`（格式检查评分）。客户端配置见
[docs/MCP.md](docs/MCP.md)。

## 参与

欢迎小 PR。最容易上手的是为某个学校或期刊的格式规则补一条合成测试：
[docs/CONTRIBUTOR_TASKS.md](docs/CONTRIBUTOR_TASKS.md)、
[CONTRIBUTING.md](CONTRIBUTING.md)。流水线说明在
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)。

不要提交真实论文、学校内部模板、审稿意见、API key 或生成的文档，测试一律
用合成样例。

## 许可

MIT，见 [LICENSE](LICENSE)。
