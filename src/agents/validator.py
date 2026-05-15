"""效果验证智能体 - 验证优化效果"""

import time
from typing import Any, Dict, Optional

from ..utils.api import DeepSeekClient


class ValidatorAgent:
    """效果验证智能体：对比优化前后的性能指标，验证优化效果"""

    def __init__(self, client: Optional[DeepSeekClient] = None):
        self.client = client or DeepSeekClient()
        self.validation_result: Optional[Dict[str, Any]] = None

    def validate(
        self,
        original_code: str,
        optimized_code: str,
        original_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        """验证优化效果，对比前后性能"""
        result = {
            "original_metrics": {},
            "optimized_metrics": {},
            "improvements": {},
            "llm_assessment": "",
            "overall_score": 0,
        }

        # 测量原始代码性能
        result["original_metrics"] = self._measure_performance(original_code)

        # 测量优化后代码性能
        result["optimized_metrics"] = self._measure_performance(optimized_code)

        # 计算改进幅度
        result["improvements"] = self._calculate_improvements(
            result["original_metrics"], result["optimized_metrics"]
        )

        # LLM 评估
        result["llm_assessment"] = self._llm_assessment(
            original_code, optimized_code, result
        )

        # 计算综合评分
        result["overall_score"] = self._compute_score(result["improvements"])

        self.validation_result = result
        return result

    def _measure_performance(self, code: str) -> Dict[str, Any]:
        """测量代码执行性能"""
        metrics = {
            "execution_time": 0.0,
            "success": False,
            "error": None,
        }

        start_time = time.perf_counter()
        try:
            exec(code, {"__name__": "__validator__"})
            metrics["success"] = True
        except Exception as e:
            metrics["error"] = str(e)
        end_time = time.perf_counter()

        metrics["execution_time"] = round(end_time - start_time, 4)
        return metrics

    def _calculate_improvements(
        self, original: Dict[str, Any], optimized: Dict[str, Any]
    ) -> Dict[str, Any]:
        """计算性能改进幅度"""
        improvements = {}

        orig_time = original.get("execution_time", 0)
        opt_time = optimized.get("execution_time", 0)

        if orig_time > 0:
            time_change = ((orig_time - opt_time) / orig_time) * 100
            improvements["time_improvement_pct"] = round(time_change, 2)
            improvements["time_before"] = orig_time
            improvements["time_after"] = opt_time
        else:
            improvements["time_improvement_pct"] = 0

        improvements["original_success"] = original.get("success", False)
        improvements["optimized_success"] = optimized.get("success", False)

        return improvements

    def _llm_assessment(
        self,
        original_code: str,
        optimized_code: str,
        result: Dict[str, Any],
    ) -> str:
        """使用 LLM 评估优化质量"""
        system_prompt = (
            "你是一个 Python 代码优化评审专家。"
            "请评估优化后的代码质量，包括：\n"
            "1. 优化是否有效\n"
            "2. 代码可读性是否保持\n"
            "3. 是否引入了新的问题\n"
            "4. 是否还有进一步优化的空间\n"
            "用中文回答。"
        )

        improvements = result.get("improvements", {})
        user_prompt = (
            f"请评估以下代码优化效果:\n\n"
            f"原始代码:\n```python\n{original_code[:1500]}\n```\n\n"
            f"优化后代码:\n```python\n{optimized_code[:1500]}\n```\n\n"
            f"性能对比:\n"
            f"  执行时间: {improvements.get('time_before', 0)}s -> "
            f"{improvements.get('time_after', 0)}s "
            f"(提升 {improvements.get('time_improvement_pct', 0)}%)\n"
            f"  原始代码执行: {'成功' if improvements.get('original_success') else '失败'}\n"
            f"  优化后执行: {'成功' if improvements.get('optimized_success') else '失败'}\n"
        )

        try:
            return self.client.chat(system_prompt, user_prompt, temperature=0.3)
        except Exception as e:
            return f"LLM 评估失败: {e}"

    def _compute_score(self, improvements: Dict[str, Any]) -> float:
        """计算综合评分 (0-100)"""
        score = 50.0  # 基础分

        time_pct = improvements.get("time_improvement_pct", 0)
        if time_pct > 0:
            score += min(time_pct * 0.4, 30)
        elif time_pct < 0:
            score += max(time_pct * 0.3, -20)

        if improvements.get("optimized_success"):
            score += 10
        else:
            score -= 30

        if improvements.get("original_success") and not improvements.get(
            "optimized_success"
        ):
            score -= 20

        return max(0, min(100, round(score, 1)))

    def run(
        self,
        original_code: str,
        optimized_code: str,
        original_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        """运行完整的效果验证流程"""
        return self.validate(original_code, optimized_code, original_profile)
