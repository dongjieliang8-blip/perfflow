"""示例应用 - 包含常见性能问题的 Python 代码用于 PerfFlow 分析演示"""

import math
import random
import time


def process_data():
    """模拟数据处理 - 包含多种性能问题"""
    # 性能问题1: 循环内重复计算
    results = []
    data = [random.randint(1, 1000) for _ in range(10000)]

    for item in data:
        # 每次循环都重新计算平方根（应该是重复计算）
        result = math.sqrt(item) + math.sqrt(item) + math.sqrt(item * 2)
        results.append(result)

    # 性能问题2: 列表追加模式（应使用列表推导式）
    filtered = []
    for r in results:
        if r > 10:
            filtered.append(r * 2)
        else:
            filtered.append(r)

    # 性能问题3: 字符串拼接
    output = ""
    for i, val in enumerate(filtered[:100]):
        output += f"Item {i}: {val:.2f}\n"

    # 性能问题4: 嵌套循环
    matrix = []
    for i in range(100):
        row = []
        for j in range(100):
            row.append(math.sin(i) * math.cos(j))
        matrix.append(row)

    return len(filtered), len(output), len(matrix)


def fibonacci_naive(n):
    """朴素递归斐波那契 - 指数时间复杂度"""
    if n <= 1:
        return n
    return fibonacci_naive(n - 1) + fibonacci_naive(n - 2)


def find_duplicates():
    """查找重复元素 - 使用低效的嵌套循环"""
    data = [random.randint(1, 500) for _ in range(5000)]
    duplicates = []

    # 性能问题: O(n^2) 的重复检测，应该用 set
    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            if data[i] == data[j] and data[i] not in duplicates:
                duplicates.append(data[i])

    return duplicates


def sort_and_search():
    """排序和搜索 - 使用低效算法"""
    data = [random.randint(1, 10000) for _ in range(5000)]

    # 使用冒泡排序（应该用内置 sorted()）
    arr = data.copy()
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]

    # 线性搜索（应该用二分搜索）
    targets = [random.choice(arr) for _ in range(100)]
    found = 0
    for t in targets:
        for x in arr:
            if x == t:
                found += 1
                break

    return found


def main():
    """运行所有示例"""
    print("PerfFlow 示例应用")
    print("=" * 40)

    start = time.perf_counter()

    print("\n>> 运行 process_data...")
    count, str_len, matrix_size = process_data()
    print(f"  结果: {count} 条数据, {str_len} 字符, {matrix_size}x{matrix_size} 矩阵")

    print("\n>> 运行 fibonacci_naive(30)...")
    fib_result = fibonacci_naive(30)
    print(f"  结果: fibonacci(30) = {fib_result}")

    print("\n>> 运行 find_duplicates...")
    dups = find_duplicates()
    print(f"  结果: 找到 {len(dups)} 个重复元素")

    print("\n>> 运行 sort_and_search...")
    found = sort_and_search()
    print(f"  结果: 找到 {found} 个目标")

    elapsed = time.perf_counter() - start
    print(f"\n总耗时: {elapsed:.2f}s")


if __name__ == "__main__":
    main()
