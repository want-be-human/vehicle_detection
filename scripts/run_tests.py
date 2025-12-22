#!/usr/bin/env python
import argparse
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
    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent
    # 默认收集语句和分支覆盖率
    pytest_cmd = [
        "pytest",
        "--cov=app",
        "--cov-branch",
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

    print("========================================")
    print("  Vehicle Detection 测试运行器 (Python)")
    print("========================================")
    print(f"[INFO] 项目目录: {project_root}")

    start = time.time()
    result = subprocess.run(pytest_cmd, cwd=project_root)
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

    # 自动打开 HTML 覆盖率报告（仅在生成了 HTML 且文件存在时）
    if (not args.quick) and args.open:
        html = project_root / "htmlcov" / "index.html"
        if html.exists():
            print("[INFO] 正在打开 HTML 覆盖率报告...")
            webbrowser.open(html.as_uri())
        else:
            print("[WARN] 未找到 HTML 报告文件:", html)

    if not args.quick:
        write_txt_summary(project_root)

    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
