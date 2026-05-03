# Contributing

感谢你帮助改进 Paper Format Agent。

## 提交前检查

1. 不提交真实学生论文与隐私数据
2. 不提交 API Key、Token、账号信息
3. 运行基础检查：

```bash
python -m compileall paper_format_agent_v3
```

## 分支与提交建议

- feat: 新功能
- fix: 缺陷修复
- docs: 文档更新
- refactor: 重构
- test: 测试

示例：
- `fix(v3): avoid reference section justify spacing`

## Pull Request 内容

- 背景问题
- 改动内容
- 风险与回滚方案
- 运行截图/报告（可脱敏）

## 代码风格

- 以可读性和可追溯性优先
- 避免大段魔法正则
- 评分规则必须可解释
