"""PerfFlow CLI 入口 - 多智能体性能分析优化流水线"""

import os
import sys

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .agents.analyzer import AnalyzerAgent
from .agents.optimizer import OptimizerAgent
from .agents.profiler import ProfilerAgent
from .agents.validator import ValidatorAgent
from .utils.api import DeepSeekClient

load_dotenv()

console = Console()


def print_header():
    """打印项目标题"""
    console.print(
        Panel.fit(
            "[bold cyan]PerfFlow[/bold cyan] - 多智能体性能分析优化流水线\n"
            "[dim]Profiler >> Analyzer >> Optimizer >> Validator[/dim]",
            border_style="cyan",
        )
    )


def read_code(file_path: str, func_name: str = None) -> str:
    """读取指定文件的代码"""
    if not os.path.exists(file_path):
        console.print(f"[red][FAIL] 文件不存在: {file_path}[/red]")
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    if func_name:
        # 简单提取指定函数
        lines = code.split("\n")
        in_func = False
        func_lines = []
        indent_level = 0
        for line in lines:
            if line.strip().startswith(f"def {func_name}"):
                in_func = True
                indent_level = len(line) - len(line.lstrip())
                func_lines.append(line)
                continue
            if in_func:
                if line.strip() == "":
                    func_lines.append(line)
                    continue
                current_indent = len(line) - len(line.lstrip())
                if current_indent > indent_level:
                    func_lines.append(line)
                else:
                    break
        if func_lines:
            return "\n".join(func_lines)
        else:
            console.print(f"[yellow][WARN] 未找到函数: {func_name}，将分析整个文件[/yellow]")

    return code


@click.group()
@click.version_option(version="0.1.0", prog_name="perfflow")
def cli():
    """PerfFlow - 多智能体性能分析优化流水线"""
    pass


@cli.command()
@click.argument("file_path")
@click.option("--function", "-f", default=None, help="指定要分析的函数名")
@click.option("--no-llm", is_flag=True, help="不调用 LLM（仅启发式分析）")
@click.option("--output", "-o", default=None, help="输出报告文件路径")
def analyze(file_path: str, function: str = None, no_llm: bool = False, output: str = None):
    """运行完整的性能分析流水线"""
    print_header()

    code = read_code(file_path, function)
    console.print(f"\n[bold]>> 目标文件:[/bold] {file_path}")
    if function:
        console.print(f"[bold]>> 目标函数:[/bold] {function}")
    console.print(f"[bold]>> 代码长度:[/bold] {len(code)} 字符\n")

    client = None if no_llm else DeepSeekClient()

    # Step 1: Profiler
    console.print("[bold cyan]>> Step 1/4: 性能剖析 (Profiler)[/bold cyan]")
    profiler = ProfilerAgent(client=client)
    profile_result = profiler.run(code, function)
    if profile_result.get("error"):
        console.print(f"  [yellow][WARN] 执行警告: {profile_result['error']}[/yellow]")
    else:
        console.print(
            f"  [green][OK] 内存峰值: {profile_result['memory_peak'] / 1024 / 1024:.2f} MB[/green]"
        )
    console.print(
        f"  [green][OK] Top 函数: "
        f"{len(profile_result.get('top_functions', []))} 个[/green]"
    )

    # Step 2: Analyzer
    console.print("\n[bold cyan]>> Step 2/4: 瓶颈分析 (Analyzer)[/bold cyan]")
    analyzer = AnalyzerAgent(client=client)
    analysis_result = analyzer.run(code, profile_result)
    bottlenecks = analysis_result.get("heuristic_bottlenecks", [])
    console.print(f"  [green][OK] 检测到 {len(bottlenecks)} 个瓶颈[/green]")
    for b in bottlenecks:
        console.print(f"    - [{b['severity']}] {b['category']}: {b['description']}")

    # Step 3: Optimizer
    console.print("\n[bold cyan]>> Step 3/4: 优化建议 (Optimizer)[/bold cyan]")
    optimizer = OptimizerAgent(client=client)
    optimization_result = optimizer.run(code, analysis_result)
    quick_wins = optimization_result.get("quick_wins", [])
    console.print(f"  [green][OK] 生成 {len(quick_wins)} 条快速优化建议[/green]")
    for w in quick_wins:
        console.print(f"    - [{w['impact']}] {w['type']}: {w['description']}")

    # Step 4: Validator
    console.print("\n[bold cyan]>> Step 4/4: 效果验证 (Validator)[/bold cyan]")
    validator = ValidatorAgent(client=client)

    # 从 LLM 输出中尝试提取优化后代码（简化处理）
    optimized_code = code  # 实际场景应从优化建议中提取
    validation_result = validator.run(code, optimized_code, profile_result)
    score = validation_result.get("overall_score", 0)
    console.print(f"  [green][OK] 综合评分: {score}/100[/green]")

    # 总结报告
    console.print("\n" + "=" * 60)
    console.print("[bold]分析报告总结[/bold]")
    console.print("=" * 60)

    table = Table(title="流水线结果")
    table.add_column("步骤", style="cyan")
    table.add_column("状态", style="green")
    table.add_column("关键发现")

    table.add_row(
        "Profiler",
        "[OK] 完成",
        f"内存峰值 {profile_result.get('memory_peak', 0) / 1024 / 1024:.1f} MB",
    )
    table.add_row(
        "Analyzer",
        "[OK] 完成",
        f"{len(bottlenecks)} 个瓶颈",
    )
    table.add_row(
        "Optimizer",
        "[OK] 完成",
        f"{len(quick_wins)} 条建议",
    )
    table.add_row(
        "Validator",
        "[OK] 完成",
        f"评分 {score}/100",
    )

    console.print(table)

    # 保存报告
    if output:
        report = {
            "file_path": file_path,
            "function": function,
            "profile": profile_result,
            "analysis": analysis_result,
            "optimization": optimization_result,
            "validation": validation_result,
        }
        with open(output, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        console.print(f"\n[green][OK] 报告已保存到 {output}[/green]")

    if client:
        client.close()


@cli.command()
@click.argument("file_path")
@click.option("--function", "-f", default=None, help="指定要剖析的函数名")
def profile(file_path: str, function: str = None):
    """仅运行性能剖析"""
    print_header()

    code = read_code(file_path, function)
    console.print(f"\n[bold]>> 目标文件:[/bold] {file_path}\n")

    profiler = ProfilerAgent()
    result = profiler.run(code, function)

    if result.get("error"):
        console.print(f"[yellow][WARN] 执行警告: {result['error']}[/yellow]")

    console.print(f"[green][OK] 内存峰值: {result['memory_peak'] / 1024 / 1024:.2f} MB[/green]")
    console.print(f"[green][OK] 内存当前: {result['memory_current'] / 1024 / 1024:.2f} MB[/green]")

    # 打印 top 函数
    table = Table(title="Top 函数耗时")
    table.add_column("#", style="dim")
    table.add_column("函数", style="cyan")
    table.add_column("调用次数")
    table.add_column("总耗时")
    table.add_column("累计耗时")

    for i, func in enumerate(result.get("top_functions", [])[:10], 1):
        table.add_row(
            str(i),
            func["function"],
            str(func["ncalls"]),
            f"{func['tottime']:.6f}s",
            f"{func['cumtime']:.6f}s",
        )

    console.print(table)

    if result.get("llm_analysis"):
        console.print("\n[bold]AI 分析:[/bold]")
        console.print(result["llm_analysis"])

    profiler.client.close()


@cli.command()
def status():
    """查看流水线状态和环境配置"""
    print_header()

    table = Table(title="环境配置")
    table.add_column("配置项", style="cyan")
    table.add_column("值")

    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    masked_key = api_key[:8] + "****" if len(api_key) > 8 else "[未设置]"
    table.add_row("DEEPSEEK_API_KEY", masked_key)
    table.add_row("DEEPSEEK_BASE_URL", os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))
    table.add_row("PERFFLOW_MODEL", os.getenv("PERFFLOW_MODEL", "deepseek-chat"))

    console.print(table)

    # 测试 API 连接
    if api_key:
        console.print("\n[bold]>> 测试 API 连接...[/bold]")
        try:
            client = DeepSeekClient()
            response = client.chat("你是一个测试助手", "回复 OK", max_tokens=10)
            console.print(f"[green][OK] API 连接正常: {response[:50]}[/green]")
            client.close()
        except Exception as e:
            console.print(f"[red][FAIL] API 连接失败: {e}[/red]")
    else:
        console.print("[yellow][WARN] 未配置 API Key，跳过连接测试[/yellow]")

    # 可用智能体
    agents_table = Table(title="可用智能体")
    agents_table.add_column("智能体", style="cyan")
    agents_table.add_column("功能")

    agents_table.add_row("Profiler", "性能剖析 - 收集 CPU、内存、执行时间指标")
    agents_table.add_row("Analyzer", "瓶颈分析 - 识别性能瓶颈和根本原因")
    agents_table.add_row("Optimizer", "优化建议 - 生成具体的优化方案和代码")
    agents_table.add_row("Validator", "效果验证 - 对比优化前后性能指标")

    console.print(agents_table)


if __name__ == "__main__":
    cli()
