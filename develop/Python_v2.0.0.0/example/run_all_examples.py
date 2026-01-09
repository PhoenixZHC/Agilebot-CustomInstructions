#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: 运行所有示例 / Run all examples
"""

import argparse
import locale
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class RunResult:
    path: Path
    returncode: int
    duration: float
    stdout: str
    stderr: str


def parse_args() -> argparse.Namespace:
    """[ZH] 定义示例执行的命令行参数。[EN] Define CLI switches for how examples run."""
    parser = argparse.ArgumentParser(description="Run every Python example and report pass/fail statistics.")
    parser.add_argument(
        "--python",
        default=sys.executable,
        help="Python interpreter to use for running the examples.",
    )
    parser.add_argument(
        "--include-init",
        action="store_true",
        help="Include __init__.py files when executing the examples.",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop after the first failure instead of running all scripts.",
    )
    return parser.parse_args()


def discover_repo_root(start: Path) -> Path:
    """[ZH] 查找仓库根目录以确保可导入 Agilebot。[EN] Locate repo root for imports."""
    for candidate in (start,) + tuple(start.parents):
        if (candidate / "Agilebot").is_dir():
            return candidate
    return start


def build_pythonpath_env(repo_root: Path) -> dict:
    """[ZH] 在环境变量中加入仓库路径。[EN] Prepend repo path to PYTHONPATH."""
    env = os.environ.copy()
    py_path = env.get("PYTHONPATH", "")
    repo_str = str(repo_root)
    parts = py_path.split(os.pathsep) if py_path else []
    if repo_str not in parts:
        parts.insert(0, repo_str)
    env["PYTHONPATH"] = os.pathsep.join(parts)
    return env


def collect_python_files(example_root: Path, include_init: bool, runner_path: Path) -> List[Path]:
    """[ZH] 枚举所有示例脚本，可选跳过 __init__。[EN] Collect scripts, optionally skip __init__."""
    files: List[Path] = []
    for path in example_root.rglob("*.py"):
        if path == runner_path:
            continue
        if not include_init and path.name == "__init__.py":
            continue
        files.append(path)
    files.sort(key=lambda p: p.relative_to(example_root).as_posix())
    return files


def run_file(python_exe: str, file_path: Path, env: dict) -> RunResult:
    """[ZH] 执行单个脚本并收集输出、退出码和耗时。[EN] Run a script and capture metadata."""
    start = time.perf_counter()
    proc = subprocess.run(
        [python_exe, str(file_path)],
        capture_output=True,
        text=True,
        encoding=locale.getpreferredencoding(False),
        errors="replace",
        cwd=file_path.parent,
        env=env,
    )
    duration = time.perf_counter() - start
    return RunResult(
        path=file_path,
        returncode=proc.returncode,
        duration=duration,
        stdout=proc.stdout,
        stderr=proc.stderr,
    )


def format_duration(seconds: float) -> str:
    return f"{seconds:.2f}s"


def print_failure_details(result: RunResult, rel_path: Path) -> None:
    """[ZH] 打印失败脚本的输出便于调试。[EN] Dump stdout/stderr for failures."""
    print(f"\n--- {rel_path.as_posix()} failed (exit {result.returncode}) ---")
    if result.stdout:
        print("stdout:")
        print(result.stdout.rstrip())
    else:
        print("stdout: <empty>")
    if result.stderr:
        print("stderr:")
        print(result.stderr.rstrip())
    else:
        print("stderr: <empty>")


def main() -> int:
    """[ZH] 顺序执行所有示例并统计结果。[EN] Run all examples and summarize outcomes."""
    args = parse_args()
    runner_path = Path(__file__).resolve()
    example_root = runner_path.parent
    repo_root = discover_repo_root(example_root)
    env = build_pythonpath_env(repo_root)
    files = collect_python_files(example_root, args.include_init, runner_path)

    if not files:
        print("No Python files were found to execute.")
        return 0

    results: List[RunResult] = []
    for file_path in files:
        rel_path = file_path.relative_to(example_root)
        print(f"Running {rel_path.as_posix()} ...", flush=True)
        result = run_file(args.python, file_path, env)
        results.append(result)
        status = "PASS" if result.returncode == 0 else f"FAIL ({result.returncode})"
        print(
            f"--> {status} in {format_duration(result.duration)}",
            flush=True,
        )
        if result.returncode != 0:
            print_failure_details(result, rel_path)
            if args.fail_fast:
                break

    total = len(results)
    failed = sum(1 for r in results if r.returncode != 0)
    passed = total - failed
    print("\nSummary")
    print("-------")
    for result in results:
        rel_path = result.path.relative_to(example_root)
        status = "PASS" if result.returncode == 0 else "FAIL"
        print(f"[{status}] {rel_path.as_posix()} ({format_duration(result.duration)})")
    print(f"\nTotal: {total}, Passed: {passed}, Failed: {failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
