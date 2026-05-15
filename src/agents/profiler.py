"""性能剖析智能体 - 收集代码性能指标"""

import cProfile
import io
import linecache
import pstats
import tracemalloc
from typing import Any, Dict, Optional

from ..utils.api import DeepSeekClient


class ProfilerAgent:
    """性能剖析智能体：收集 CPU、内存、执行时间等性能指标"""

    def __init__(self, client: Optional[DeepSeekClient] = None):
        self.client = client or DeepSeekClient()
        self.profile_result: Optional[Dict[str, Any]] = None

    def profile_code(self, code: str, func_name: Optional[str] = None) -> Dict[str, Any]:
        """对代码进行性能剖析，返回性能指标"""
        result = {
            "execution_time": 0.0,
            "memory_peak": 0,
            "memory_current": 0,
            "cpu_stats": {},
            "top_functions": [],
            "raw_output": "",
        }

        # 执行时间剖析
        pr = cProfile.Profile()
        tracemalloc.start()

        try:
            pr.enable()
            exec(code, {"__name__": "__profiler__"})
            pr.disable()
        except Exception as e:
            result["error"] = str(e)
            return result

        # 收集内存信息
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # 整理剖析结果
        stream = io.StringIO()
        ps = pstats.Stats(pr, stream=stream)
        ps.sort_stats("cumulative")
        ps.print_stats(20)
        result["raw_output"] = stream.getvalue()
        result["memory_peak"] = peak
        result["memory_current"] = current

        # 提取 top 函数
        func_stats = []
        for func_key, (cc, nc, tt, ct, callers) in ps.stats.items():
            filename, lineno, funcname = func_key
            func_stats.append(
                {
                    "function": funcname,
                    "file": filename,
                    "line": lineno,
                    "ncalls": nc,
                    "tottime": round(tt, 6),
                    "cumtime": round(ct, 6),
                }
            )
        func_stats.sort(key=lambda x: x["cumtime"], reverse=True)
        result["top_functions"] = func_stats[:10]

        return result

    def analyze_with_llm(self, code: str, profile_result: Dict[str, Any]) -> str:
        """使用 LLM 对性能数据进行初步解读"""
        system_prompt = (
            "你是一个 Python 性能剖析专家。"
            "请根据提供的性能剖析数据，总结关键的性能指标和初步观察。"
            "用中文回答，简洁明了。"
        )

        summary = f"代码长度: {len(code)} 字符\n\n"
        summary += f"内存峰值: {profile_result['memory_peak'] / 1024 / 1024:.2f} MB\n"
        summary += f"内存当前: {profile_result['memory_current'] / 1024 / 1024:.2f} MB\n\n"
        summary += "Top 10 函数耗时:\n"
        for i, func in enumerate(profile_result.get("top_functions", [])[:10], 1):
            summary += (
                f"  {i}. {func['function']} "
                f"(calls={func['ncalls']}, "
                f"cumtime={func['cumtime']}s)\n"
            )
        summary += f"\n详细输出:\n{profile_result.get('raw_output', 'N/A')}"

        user_prompt = f"请分析以下代码的性能剖析结果:\n\n代码:\n```python\n{code[:2000]}\n```\n\n性能数据:\n{summary}"

        return self.client.chat(system_prompt, user_prompt)

    def run(self, code: str, func_name: Optional[str] = None) -> Dict[str, Any]:
        """运行完整的性能剖析流程"""
        self.profile_result = self.profile_code(code, func_name)
        self.profile_result["llm_analysis"] = self.analyze_with_llm(code, self.profile_result)
        return self.profile_result
