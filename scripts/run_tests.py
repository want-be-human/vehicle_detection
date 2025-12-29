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


def parse_pytest_output(output: str) -> list:
    """解析pytest输出，提取失败的测试用例信息"""
    failed_tests = []
    test_to_error = {}
    lines = output.split('\n')
    
    # 第一步：从 FAILURES 区域提取详细错误信息
    i = 0
    while i < len(lines):
        line = lines[i]
        # 查找失败测试的分隔线
        if line.startswith('_____') and i + 1 < len(lines) and not 'FAILURES' in lines[i]:
            # 提取测试名称（在下划线包围的行中）
            test_name = line.strip('_').strip()
            if test_name and '::' in test_name:
                # 查找 E   开头的错误行
                j = i + 1
                error_lines = []
                while j < len(lines) and not lines[j].startswith('_____') and not lines[j].startswith('===='):
                    if lines[j].startswith('E   '):
                        error_lines.append(lines[j][4:].strip())
                    j += 1
                
                if error_lines:
                    test_to_error[test_name] = error_lines[0]  # 取第一个错误行
                i = j
                continue
        i += 1
    
    # 第二步：从 short test summary 获取测试列表
    in_summary = False
    for line in lines:
        if 'short test summary' in line.lower():
            in_summary = True
            continue
        if in_summary and line.startswith('FAILED '):
            test_path = line[7:].split(' - ')[0].strip()
            # 优先使用从 FAILURES 区域提取的详细错误，用完整路径或测试方法名匹配
            error_msg = test_to_error.get(test_path, "")
            if not error_msg:
                # 尝试只用测试方法名匹配
                for key, value in test_to_error.items():
                    if key in test_path:
                        error_msg = value
                        break
            
            # 如果没有找到，尝试从当前行提取
            if not error_msg and ' - ' in line:
                error_msg = line.split(' - ', 1)[1].strip()
            
            if not error_msg:
                error_msg = "Test failed"
            
            failed_tests.append({
                'test': test_path,
                'error': error_msg
            })
        elif in_summary and line.startswith('='):
            break
    
    return failed_tests


def write_txt_summary(project_root: Path, failed_tests: list = None) -> None:
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
    
    # 添加失败测试信息
    if failed_tests:
        lines.append("")
        lines.append("=" * 80)
        lines.append("Failed Tests Summary")
        lines.append("=" * 80)
        lines.append(f"Total Failed: {len(failed_tests)}")
        lines.append("")
        
        for idx, test in enumerate(failed_tests, 1):
            lines.append(f"{idx}. {test['test']}")
            lines.append(f"   Error: {test['error']}")
            lines.append("")

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
    # 捕获 pytest 输出以解析失败信息
    result = subprocess.run(
        pytest_cmd, 
        cwd=project_root, 
        env=env,
        capture_output=True,
        text=True
    )
    duration = time.time() - start
    
    # 显示输出
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    # 解析失败的测试
    failed_tests = []
    if result.returncode != 0:
        failed_tests = parse_pytest_output(result.stdout)

    print("========================================")
    print("  测试执行完成")
    print("========================================")
    print(f"[TIME] 总耗时: {duration:.2f} 秒")

    if result.returncode == 0:
        print("[RESULT] 所有测试通过 ✓")
    else:
        print("[RESULT] 存在失败的测试 ✗")
        if failed_tests:
            print(f"[INFO] 发现 {len(failed_tests)} 个失败的测试用例")
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
        write_txt_summary(project_root, failed_tests)

    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
