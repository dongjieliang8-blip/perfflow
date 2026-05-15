"""瓶颈分析智能体 - 分析性能瓶颈的根本原因"""

from typing import Any, Dict, Optional

from ..utils.api import DeepSeekClient


class AnalyzerAgent:
    """瓶颈分析智能体：深入分析性能瓶颈的根本原因"""

    def __init__(self, client: Optional[DeepSeekClient] = None):
        self.client = client or DeepSeekClient()
        self.analysis_result: Optional[Dict[str, Any]] = None

    def analyze(
        self, code: str, profile_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """分析性能瓶颈，返回瓶颈列表和根因分析"""
        system_prompt = (
            "你是一个 Python 性能优化专家。"
            "请根据提供的代码和性能剖析数据，识别性能瓶颈并分析根本原因。"
            "请以 JSON 格式返回分析结果，包含以下字段:\n"
            "- bottlenecks: 瓶颈列表，每个包含 category, description, severity, impact\n"
            "- root_causes: 根本原因分析\n"
            "- priority: 优化优先级建议\n"
            "用中文回答。"
        )

        # 构建性能摘要
        perf_summary = self._build_perf_summary(profile_result)

        user_prompt = (
            f"请分析以下 Python 代码的性能瓶颈:\n\n"
            f"代码:\n```python\n{code[:3000]}\n```\n\n"
            f"性能剖析数据:\n{perf_summary}\n\n"
            f"请识别主要瓶颈并给出根因分析。"
        )

        llm_response = self.client.chat(system_prompt, user_prompt, temperature=0.2)

        # 启发式分析（不依赖 LLM 的基础分析）
        heuristic_bottlenecks = self._heuristic_analysis(code, profile_result)

        result = {
            "llm_analysis": llm_response,
            "heuristic_bottlenecks": heuristic_bottlenecks,
            "top_functions": profile_result.get("top_functions", []),
            "memory_peak_mb": profile_result.get("memory_peak", 0) / 1024 / 1024,
        }

        self.analysis_result = result
        return result

    def _build_perf_summary(self, profile_result: Dict[str, Any]) -> str:
        """构建性能数据摘要"""
        lines = []
        lines.append(
            f"内存峰值: {profile_result.get('memory_peak', 0) / 1024 / 1024:.2f} MB"
        )
        lines.append(
            f"内存当前: {profile_result.get('memory_current', 0) / 1024 / 1024:.2f} MB"
        )
        lines.append("\nTop 函数耗时:")
        for i, func in enumerate(profile_result.get("top_functions", [])[:10], 1):
            lines.append(
                f"  {i}. {func['function']} "
                f"(calls={func['ncalls']}, "
                f"tottime={func['tottime']}s, "
                f"cumtime={func['cumtime']}s)"
            )
        if profile_result.get("error"):
            lines.append(f"\n执行错误: {profile_result['error']}")
        return "\n".join(lines)

    def _heuristic_analysis(
        self, code: str, profile_result: Dict[str, Any]
    ) -> list:
        """基于规则的启发式瓶颈检测"""
        bottlenecks = []

        # 检测常见性能反模式
        patterns = [
            ("循环内重复计算", ["for ", "while "], "中"),
            ("全局变量频繁访问", ["global "], "低"),
            ("大量字符串拼接", ['+ "', "+ '"], "中"),
            ("列表追加模式", [".append("], "低"),
            ("嵌套循环", ["for ", "for "], "高"),
        ]

        for name, keywords, severity in patterns:
            for kw in keywords:
                if kw in code:
                    bottlenecks.append(
                        {
                            "category": name,
                            "severity": severity,
                            "description": f"检测到潜在的 {name} 模式",
                        }
                    )
                    break

        # 内存相关检测
        if profile_result.get("memory_peak", 0) > 100 * 1024 * 1024:
            bottlenecks.append(
                {
                    "category": "内存使用过高",
                    "severity": "高",
                    "description": "内存峰值超过 100MB，可能存在内存泄漏或大对象问题",
                }
            )

        return bottlenecks

    def run(self, code: str, profile_result: Dict[str, Any]) -> Dict[str, Any]:
        """运行完整的瓶颈分析流程"""
        return self.analyze(code, profile_result)
