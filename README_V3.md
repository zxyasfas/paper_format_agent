# Paper Format Agent V3

## 核心改动
- 先识别类型再排版：`classify -> 写入类型标记 -> 应用样式 -> 删除标记样式`
- 新增“前置手工目录块”识别与重排，避免把目录误当正文标题
- 强制清理段落编号元数据（`w:numPr`）与常见黑方块项目符号前缀
- 引擎可切换：`auto | python | word-com | libreoffice`
- 评分支持校准：可用人工打分样本拟合线性校准参数，目标 MAE <= 5

## 运行（格式修复）
```bash
python -m paper_format_agent_v3.cli ^
  --format-file "E:\tem\国际商学院本科毕业论文排版格式的文字说明及排版范例(1).docx" ^
  --paper-file "E:\tem\22200076李佳洁.docx" ^
  --out-dir "D:\code\paper_format_agent_mvp\sample_output\run_v3" ^
  --engine auto ^
  --marker-dump
```

默认评分模式：只校验“原文本来存在”的章节项（例如原文没有英文摘要，就不会因为缺英文摘要扣分）。  
如需严格按模板强制扣分，加参数：`--strict-required-sections`。

## 引擎说明
- `auto`：依次尝试 `word-com -> libreoffice -> python`
- `word-com`：需要本机可用 Word COM
- `libreoffice`：需要 `soffice/libreoffice` 在 PATH
- `python`：纯 python-docx 后处理

## 评分校准（对齐人工评分）
1. 准备 `labels.json`：
```json
[
  {"docx":"E:/tem/a.docx","human_score":86},
  {"docx":"E:/tem/b.docx","human_score":92}
]
```
2. 运行校准：
```bash
python -m paper_format_agent_v3.cli ^
  --format-file "E:\tem\国际商学院本科毕业论文排版格式的文字说明及排版范例(1).docx" ^
  --out-dir "D:\code\paper_format_agent_mvp\sample_output\calib" ^
  --calibrate-labels "D:\code\paper_format_agent_mvp\labels.json"
```
3. 正式评分时加载校准参数：
```bash
python -m paper_format_agent_v3.cli ... --calibration-file "...\scoring_calibration.json"
```
