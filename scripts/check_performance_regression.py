#!/usr/bin/env python3
"""
scripts/check_performance_regression.py
Automated performance regression checker for Noxen with:
- Strict benchmark suite coverage verification (all 7 benchmarks required).
- Platform and backend-aware absolute throughput floors.
- Relative regression comparison against recorded baseline results.
- JSON output recording for historical tracking and CI artifacts.
"""

import os
import re
import sys
import json
import shutil
import argparse
import subprocess

EXPECTED_BENCHMARKS = [
    "Flat Model Parsing",
    "Nested Model Parsing",
    "Invalid Payload Reject",
    "Full JSON Round-Trip",
    "Deep Hierarchy Parsing",
    "Fast Model Dump",
    "Validated Model Dump",
]

# Standard baseline throughput floors (ops/sec) on native Linux/macOS
BASE_PERFORMANCE_FLOORS = {
    "Flat Model Parsing": 200000,
    "Nested Model Parsing": 150000,
    "Invalid Payload Reject": 250000,
    "Full JSON Round-Trip": 200000,
    "Deep Hierarchy Parsing": 100000,
    "Fast Model Dump": 250000,
    "Validated Model Dump": 150000,
}

def get_platform_factor() -> float:
    """Returns calibration multiplier for the current OS and CI environment."""
    # Windows GitHub Actions runners have coarse timer granularity (~15ms) and VM scheduling jitter
    if sys.platform == "win32" or os.environ.get("RUNNER_OS") == "Windows":
        return 0.5
    return 1.0

def main() -> int:
    parser = argparse.ArgumentParser(description="Noxen Performance Regression Gate")
    parser.add_argument("--backend", choices=["llvm", "qbe"], default="llvm", help="Backend to evaluate")
    parser.add_argument("--factor", type=float, default=None, help="Explicit floor scaling factor")
    parser.add_argument("--update-baseline", action="store_true", help="Update recorded baseline results")
    args = parser.parse_args()

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    benchmarks_dir = os.path.join(repo_root, "benchmarks")
    baseline_file = os.path.join(benchmarks_dir, f"baseline_{args.backend}.json")
    latest_file = os.path.join(benchmarks_dir, f"latest_{args.backend}.json")

    platform_factor = args.factor if args.factor is not None else get_platform_factor()
    backend_factor = 0.8 if args.backend == "qbe" else 1.0
    combined_factor = platform_factor * backend_factor

    noxc_cmd = shutil.which("noxc") or "noxc"
    print("=== Noxen Performance Regression Gate ===")
    print(f"Compiler binary:    {noxc_cmd}")
    print(f"Target Backend:     {args.backend.upper()}")
    print(f"Platform:           {sys.platform} (factor: {platform_factor:.2f})")
    print(f"Effective factor:   {combined_factor:.2f}\n")

    cmd = [noxc_cmd, "run", "benchmarks/run_benchmarks.nox"]
    if args.backend == "qbe":
        cmd.extend(["--backend", "qbe"])

    res = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True)

    if res.returncode != 0:
        print(f"[FAIL] Benchmark execution failed (exit code {res.returncode}):")
        print(res.stderr)
        return 1

    print("Benchmark Output:")
    print(res.stdout)

    # Parse lines like: "1. Flat Model Parsing: 7 ms (median) | 714285 ops/sec"
    pattern = re.compile(r"\d+\.\s+([A-Za-z0-9\s\(\)\-]+?):\s+(\d+)\s+ms.*?\|\s+(\d+)\s+ops/sec")
    matches = pattern.findall(res.stdout)

    if not matches:
        print("[FAIL] Could not parse benchmark throughput metrics from output!")
        return 1

    # 1. Verify Benchmark Coverage: all 7 required benchmarks must be present
    missing_benchmarks = []
    current_metrics = {}
    for expected in EXPECTED_BENCHMARKS:
        matched_tuple = next((m for m in matches if expected in m[0]), None)
        if matched_tuple is None:
            missing_benchmarks.append(expected)
        else:
            name, ms_str, ops_str = matched_tuple
            current_metrics[expected] = {
                "name": name.strip(),
                "ms": int(ms_str),
                "ops_sec": int(ops_str),
            }

    if missing_benchmarks:
        print(f"\n[FAIL] Incomplete benchmark suite! Missing required benchmarks:")
        for mb in missing_benchmarks:
            print(f"  - {mb}")
        return 1

    print("Benchmark Coverage Check: All 7 required benchmarks present and accounted for.\n")

    # Save latest results JSON
    os.makedirs(benchmarks_dir, exist_ok=True)
    with open(latest_file, "w", encoding="utf-8") as f:
        json.dump(current_metrics, f, indent=2)

    # Load baseline results if available
    baseline_metrics = None
    if os.path.exists(baseline_file) and not args.update_baseline:
        try:
            with open(baseline_file, "r", encoding="utf-8") as f:
                baseline_metrics = json.load(f)
            print(f"Loaded recorded baseline for relative regression analysis from {os.path.basename(baseline_file)}")
        except Exception as e:
            print(f"Warning: could not read baseline file: {e}")

    regressions = []
    print("Performance Evaluation against Thresholds & Baseline:")

    for expected, data in current_metrics.items():
        name = data["name"]
        ops = data["ops_sec"]
        ms = data["ms"]

        # Absolute floor check
        base_floor = BASE_PERFORMANCE_FLOORS.get(expected, 100000)
        effective_floor = int(base_floor * combined_factor)

        if ops < effective_floor:
            regressions.append(f"{name}: {ops:,} ops/sec below absolute floor {effective_floor:,} ops/sec ({ms} ms)")
            print(f"  [REGRESSION (Floor)] {name}: {ops:,} ops/sec < floor {effective_floor:,} ops/sec")
        else:
            margin = ((ops - effective_floor) / effective_floor) * 100.0
            print(f"  [PASS (Floor)] {name}: {ops:,} ops/sec ({ms} ms, +{margin:.1f}% above floor {effective_floor:,})")

        # Relative baseline comparison (if baseline exists)
        if baseline_metrics and expected in baseline_metrics:
            base_ops = baseline_metrics[expected]["ops_sec"]
            base_ms = baseline_metrics[expected].get("ms", 0)
            diff_pct = ((ops - base_ops) / base_ops) * 100.0
            ms_diff = ms - base_ms

            # Flag relative regression if throughput drops by >45% or (>35% and latency increased by >4ms)
            if diff_pct < -45.0 or (diff_pct < -35.0 and ms_diff > 4):
                regressions.append(f"{name}: throughput dropped by {diff_pct:.1f}% vs baseline ({ops:,} vs {base_ops:,} ops/sec, +{ms_diff} ms)")
                print(f"    [REGRESSION (Relative)] {name}: {ops:,} ops/sec dropped by {diff_pct:.1f}% vs baseline {base_ops:,} ops/sec")
            else:
                status_str = f"+{diff_pct:.1f}%" if diff_pct >= 0 else f"{diff_pct:.1f}%"
                print(f"    [OK (Relative)] vs baseline {base_ops:,} ops/sec: {status_str}")

    # If updating baseline or baseline doesn't exist, record current metrics
    if args.update_baseline or not os.path.exists(baseline_file):
        with open(baseline_file, "w", encoding="utf-8") as f:
            json.dump(current_metrics, f, indent=2)
        print(f"\n[INFO] Updated baseline recorded in {os.path.basename(baseline_file)}")

    if regressions:
        print("\n[FAILED] Performance regressions detected:")
        for r in regressions:
            print(f"  - {r}")
        return 1

    print("\nALL PERFORMANCE BENCHMARKS WITHIN BOUNDS! ZERO REGRESSIONS DETECTED.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
