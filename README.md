# PerfFlow - 多智能体性能分析优化流水线

## 项目简介

PerfFlow 是一个基于多智能体 AI 的性能分析与优化流水线，由 DeepSeek API 驱动。它解决了手动性能分析耗时长、需要深厚专业知识的痛点。

## 核心架构

```
Profiler (性能剖析) -> Analyzer (瓶颈分析) -> Optimizer (优化建议) -> Validator (效果验证)
```

## 四大智能体

| 智能体 | 功能 | 输出 |
|--------|------|------|
| **Profiler** | 收集代码性能指标（CPU、内存、执行时间） | 性能剖析报告 |
| **Analyzer** | 分析性能瓶颈的根本原因 | 瓶颈分析报告 |
| **Optimizer** | 生成针对性的优化建议和代码修改 | 优化方案 |
| **Validator** | 验证优化效果，对比优化前后指标 | 验证报告 |

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入你的 DeepSeek API Key
```

### 3. 运行分析

```bash
# 分析示例应用
python -m src.main analyze demo/sample_app.py

# 分析指定函数
python -m src.main analyze demo/sample_app.py --function process_data

# 仅运行性能剖析
python -m src.main profile demo/sample_app.py

# 查看流水线状态
python -m src.main status
```

## 项目结构

```
perfflow/
├── src/
│   ├── main.py              # CLI 入口
│   ├── agents/
│   │   ├── profiler.py      # 性能剖析智能体
│   │   ├── analyzer.py      # 瓶颈分析智能体
│   │   ├── optimizer.py     # 优化建议智能体
│   │   └── validator.py     # 效果验证智能体
│   └── utils/
│       └── api.py           # DeepSeek API 封装
├── demo/
│   └── sample_app.py        # 示例应用（含性能问题）
├── tests/                   # 测试目录
├── requirements.txt
├── .env.example
└── APPLICATION.md           # 申请材料
```

## 示例

```bash
# 分析示例应用的性能问题
python -m src.main analyze demo/sample_app.py --function process_data

# 输出示例：
# [OK] Profiler: 性能剖析完成
#    - 函数平均执行时间: 2.35s
#    - 内存峰值: 156MB
# [OK] Analyzer: 瓶颈分析完成
#    - 主要瓶颈: 循环内重复计算、缺少缓存
# [OK] Optimizer: 优化建议生成完成
#    - 建议1: 使用 functools.lru_cache 缓存重复计算
#    - 建议2: 将列表推导替代循环追加
# [OK] Validator: 效果验证完成
#    - 优化后执行时间: 0.45s (提升 80.9%)
#    - 优化后内存: 89MB (降低 42.9%)
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | 必填 |
| `DEEPSEEK_BASE_URL` | API 基础地址 | `https://api.deepseek.com` |
| `PERFFLOW_MODEL` | 使用的模型 | `deepseek-chat` |

## License

MIT
