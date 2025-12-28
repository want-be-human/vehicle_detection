#!/usr/bin/env python
"""
Vehicle Detection 测试运行器

功能:
- 运行pytest测试
- 生成覆盖率报告(终端、HTML、XML)
- 自动打开HTML覆盖率报告
- 支持多种运行模式

使用方法:
    python scripts/run_tests.py [options]

选项:
    --quick     快速模式，只生成终端覆盖率摘要
    --verbose   详细模式，显示完整测试输出
    --failed    只运行上次失败的测试
    --open      测试后自动打开HTML覆盖率报告
    --tests-dir 指定测试目录或文件
    --markers   显示所有可用的pytest标记
    --collect   只收集测试，不运行
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path
import webbrowser
import time
import xml.etree.ElementTree as ET


def write_txt_summary(project_root: Path) -> None:
    xml_path = project_root / "coverage.xml"
    out_path = project_root / "coverage_summary.txt"
    if not xml_path.exists():
        print("[WARN] 未找到 coverage.xml，跳过生成文本覆盖率摘要")
        return

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except Exception as exc:  # noqa: BLE001
        print("[WARN] 解析 coverage.xml 失败，跳过生成文本覆盖率摘要:", exc)
        return

    lines_total = float(root.attrib.get("lines-valid", 0) or 0)
    lines_covered = float(root.attrib.get("lines-covered", 0) or 0)
    branches_total = float(root.attrib.get("branches-valid", 0) or 0)
    branches_covered = float(root.attrib.get("branches-covered", 0) or 0)

    def pct(covered: float, total: float) -> float:
        if total == 0:
            return 100.0
        return round((covered / total) * 100, 2)

    total_line_pct = pct(lines_covered, lines_total)
    total_branch_pct = pct(branches_covered, branches_total)

    per_file = {}
    for cls in root.findall('.//class'):
        filename = cls.attrib.get('filename', '').replace('\\', '/')
        line_rate = float(cls.attrib.get('line-rate', 0)) * 100
        branch_rate = float(cls.attrib.get('branch-rate', 0)) * 100
        # 如果已有同名文件，取较低值保守体现未覆盖
        if filename in per_file:
            prev_line, prev_branch = per_file[filename]
            line_rate = min(line_rate, prev_line)
            branch_rate = min(branch_rate, prev_branch)
        per_file[filename] = (round(line_rate, 2), round(branch_rate, 2))

    lines = []
    lines.append("Coverage Summary (statements & branches)")
    lines.append(f"Total - statements: {total_line_pct:.2f}%, branches: {total_branch_pct:.2f}%")
    lines.append("")
    for fname in sorted(per_file):
        stmt_pct, branch_pct = per_file[fname]
        lines.append(f"{fname}: statements {stmt_pct:.2f}%, branches {branch_pct:.2f}%")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[INFO] 已生成覆盖率摘要: {out_path}")

def main():
    parser = argparse.ArgumentParser(description="Vehicle Detection 测试运行器")
    parser.add_argument("--quick", action="store_true", help="快速模式：只生成终端覆盖率摘要，不生成 HTML/XML")
    parser.add_argument("--verbose", action="store_true", help="pytest -vv --tb=long")
    parser.add_argument("--failed", action="store_true", help="只运行上次失败的测试 (--lf)")
    parser.add_argument("--open", action="store_true", help="测试后自动打开 HTML 覆盖率报告（默认在非 quick 模式且生成成功时生效）")
    parser.add_argument("--tests-dir", default="tests", help="指定测试目录或文件，默认 tests（相对于项目根目录）")
    parser.add_argument("--markers", action="store_true", help="显示所有可用的pytest标记")
    parser.add_argument("--collect", action="store_true", help="只收集测试，不运行")
    parser.add_argument("--pattern", "-k", default="", help="按模式匹配测试名称 (pytest -k)")
    parser.add_argument("--parallel", "-n", type=int, default=0, help="并行运行测试的进程数 (需要 pytest-xdist)")
    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent
    tests_dir = Path(args.tests_dir)
    if not tests_dir.is_absolute():
        tests_dir = (project_root / tests_dir).resolve()

    if not tests_dir.exists():
        print(f"[WARN] 指定的测试目录不存在: {tests_dir}，将回退到项目根目录")
        tests_dir = project_root

    # 显示标记后退出
    if args.markers:
        subprocess.run(["pytest", "--markers"], cwd=project_root)
        return

    # 只收集测试
    if args.collect:
        subprocess.run(["pytest", "--collect-only", str(tests_dir)], cwd=project_root)
        return

    # 默认收集语句和分支覆盖率
    pytest_cmd = [
        "pytest",
        "--cov=app",
        "--cov-branch",
        str(tests_dir),
    ]

    if args.quick:
        # 快速模式：只在终端显示覆盖率概要，跳过 HTML/XML
        pytest_cmd += ["--cov-report=term-missing", "--no-cov-on-fail"]
    else:
        # 完整模式：生成终端、HTML、XML 报告，便于查看和 CI 使用
        pytest_cmd += [
            "--cov-report=term-missing",
            "--cov-report=html",
            "--cov-report=xml",
        ]

    if args.failed:
        pytest_cmd.append("--lf")

    if args.verbose:
        pytest_cmd += ["-vv", "--tb=long"]

    # 按模式匹配测试
    if args.pattern:
        pytest_cmd += ["-k", args.pattern]

    # 并行运行测试
    if args.parallel > 0:
        pytest_cmd += ["-n", str(args.parallel)]

    print("========================================")
    print("  Vehicle Detection 测试运行器 (Python)")
    print("========================================")
    print(f"[INFO] 项目目录: {project_root}")
    print(f"[INFO] 测试目录: {tests_dir}")
    print(f"[INFO] 测试命令: {' '.join(pytest_cmd)}")
    print("----------------------------------------")

    env = os.environ.copy()
    # 防止外部设置的 PYTEST_ADDOPTS 把 --open 等传给 pytest 导致报错
    env.pop("PYTEST_ADDOPTS", None)

    start = time.time()
    result = subprocess.run(pytest_cmd, cwd=project_root, env=env)
    duration = time.time() - start

    print("========================================")
    print("  测试执行完成")
    print("========================================")
    print(f"[TIME] 总耗时: {duration:.2f} 秒")

    if result.returncode == 0:
        print("[RESULT] 所有测试通过 ✓")
    else:
        print("[RESULT] 存在失败的测试 ✗")
        print("[TIP] 可使用 --failed 只运行上次失败的测试")
        print("[TIP] 可使用 --verbose 查看详细错误信息")
        print("[TIP] 可使用 -k 'pattern' 只运行匹配的测试")

    # 自动打开 HTML 覆盖率报告（仅在生成了 HTML 且文件存在时）
    if not args.quick:
        if args.open:
            html = project_root / "htmlcov" / "index.html"
            if html.exists():
                print("[INFO] 正在打开 HTML 覆盖率报告...")
                webbrowser.open(html.as_uri())
            else:
                print("[WARN] 未找到 HTML 报告文件:", html)
        else:
            print("[INFO] 如需自动打开 HTML 报告，请添加 --open 参数")

    if not args.quick:
        write_txt_summary(project_root)

    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
