"""LLM 辅助功能模块（可选）"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class LLMConfig:
    """LLM 配置"""
    enabled: bool = False
    api_key: str | None = None
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-v4-pro"
    timeout_seconds: int = 90


def generate_suggestions(paper_path: str, format_text: str, config: LLMConfig) -> dict[str, Any]:
    """
    生成 LLM 建议（默认不启用）
    
    如果启用了 LLM，会调用 API 生成格式建议。
    默认情况下返回空建议，不修改论文内容。
    """
    if not config.enabled or not config.api_key:
        return {
            "used": False,
            "suggestions": [],
            "warnings": [],
            "message": "LLM 未启用（默认使用纯规则引擎）"
        }
    
    # 这里可以接入实际的 LLM API
    # 目前返回空建议，保持论文内容不变
    return {
        "used": True,
        "suggestions": [],
        "warnings": ["LLM 建议功能正在开发中，当前仅使用规则引擎"],
        "message": "LLM 已启用但未生成具体建议"
    }
