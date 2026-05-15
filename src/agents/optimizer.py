"""优化建议智能体 - 生成针对性的优化建议"""

from typing import Any, Dict, Optional

from ..utils.api import DeepSeekClient


class OptimizerAgent:
    """优化建议智能体：根据瓶颈分析生成具体的优化方案和代码修改"""

    def __init__(self, client: Optional[DeepSeekClient] = None):
        self.client = client or DeepSeekClient()
        self.optimization_result: Optional[Dict[str, Any]] = None

    def optimize(
        self, code: str, analysis_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """根据瓶颈分析生成优化建议"""
        system_prompt = (
            "你是一个 Python 性能优化专家。"
            "请根据提供的代码和瓶颈分析结果，生成具体的优化建议和修改后的代码。"
            "请以以下格式返回:\n"
            "1. 优化建议列表（每条包含问题、建议、预期效果）\n"
            "2. 优化后的完整代码\n"
            "3. 优化说明\n"
            "用中文回答。确保优化后的代码可以直接运行。"
        )

        analysis_summary = self._build_analysis_summary(analysis_result)

        user_prompt = (
            f"请根据以下瓶颈分析结果，生成优化方案:\n\n"
            f"原始代码:\n```python\n{code[:3000]}\n```\n\n"
            f"瓶颈分析:\n{analysis_summary}\n\n"
            f"请给出具体的优化建议和优化后的代码。"
        )

        llm_response = self.client.chat(system_prompt, user_prompt, temperature=0.3)

        # 生成基于规则的快速优化建议
        quick_wins = self._quick_wins(code)

        result = {
            "llm_suggestions": llm_response,
            "quick_wins": quick_wins,
            "original_code": code,
        }

        self.optimization_result = result
        return result

    def _build_analysis_summary(self, analysis_result: Dict[str, Any]) -> str:
        """构建瓶颈分析摘要"""
        lines = []

        # LLM 分析
        if analysis_result.get("llm_analysis"):
            lines.append(f"AI 分析:\n{analysis_result['llm_analysis'][:1500]}")

        # 启发式瓶颈
        if analysis_result.get("heuristic_bottlenecks"):
            lines.append("\n检测到的瓶颈:")
            for b in analysis_result["heuristic_bottlenecks"]:
                lines.append(
                    f"  - [{b['severity']}] {b['category']}: {b['description']}"
                )

        # Top 函数
        if analysis_result.get("top_functions"):
            lines.append("\n耗时最高的函数:")
            for f in analysis_result["top_functions"][:5]:
                lines.append(
                    f"  - {f['function']}: cumtime={f['cumtime']}s"
                )

        return "\n".join(lines)

    def _quick_wins(self, code: str) -> list:
        """基于规则的快速优化建议"""
        suggestions = []

        if "for " in code and ".append(" in code:
            suggestions.append(
                {
                    "type": "列表构建优化",
                    "description": "考虑使用列表推导式替代循环中调用 append()",
                    "impact": "中",
                }
            )

        if "sorted(" not in code and ".sort(" not in code and "for " in code:
            if "+" in code and ("str" in code.lower() or '"' in code):
                suggestions.append(
                    {
                        "type": "字符串拼接优化",
                        "description": "考虑使用 join() 或 f-string 替代字符串拼接",
                        "impact": "中",
                    }
                )

        if "import " in code and ("dict()" in code or "{}" in code):
            suggestions.append(
                {
                    "type": "数据结构选择",
                    "description": "确认使用了最合适的数据结构（dict vs list vs set）",
                    "impact": "低",
                }
            )

        if code.count("def ") > 0 and "cache" not in code.lower():
            suggestions.append(
                {
                    "type": "缓存优化",
                    "description": "对于纯函数考虑使用 functools.lru_cache",
                    "impact": "高",
                }
            )

        return suggestions

    def run(self, code: str, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """运行完整的优化建议生成流程"""
        return self.optimize(code, analysis_result)
