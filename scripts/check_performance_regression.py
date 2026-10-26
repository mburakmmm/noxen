#!/usr/bin/env python3
"""
scripts/check_performance_regression.py
Automated performance regression checker for Noxen with platform & backend-aware thresholds.

Runs benchmarks/run_benchmarks.nox and enforces throughput floors to prevent
latency and memory regressions across commits and CI runs.

Platform & Backend Awareness:
- Accounts for virtualization overhead and timer resolution differences across OS runners
  (Linux, macOS, Windows).
- Provides distinct calibration factors for Windows CI VMs to prevent false alarms
  while strictly guarding against real performance regressions.
"""

import os
import re
import sys
import shutil
import argparse
import subprocess

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
    args = parser.parse_args()

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

    res = subprocess.run(cmd, capture_output=True, text=True)

    if res.returncode != 0:
        print(f"[FAIL] Benchmark execution failed (exit code {res.returncode}):")
        print(res.stderr)
        return 1

    print("Benchmark Output:")
    print(res.stdout)

    # Parse lines like: "1. Flat Model Parsing: 7 ms (median) | 714285 ops/sec"
    pattern = re.compile(r"\d+\.\s+([A-Za-z0-9\s\(\)]+?):\s+(\d+)\s+ms.*?\|\s+(\d+)\s+ops/sec")
    matches = pattern.findall(res.stdout)

    if not matches:
        print("[FAIL] Could not parse benchmark throughput metrics from output!")
        return 1

    regressions = []
    print("Performance Evaluation against Thresholds:")

    for name_raw, ms_str, ops_str in matches:
        name = name_raw.strip()
        ops = int(ops_str)
        ms = int(ms_str)

        base_floor = None
        for key, threshold in BASE_PERFORMANCE_FLOORS.items():
            if key in name:
                base_floor = threshold
                break

        if base_floor is not None:
            effective_floor = int(base_floor * combined_factor)
            if ops < effective_floor:
                regressions.append(f"{name}: {ops:,} ops/sec (BELOW FLOOR {effective_floor:,} ops/sec, {ms} ms)")
                print(f"  [REGRESSION] {name}: {ops:,} ops/sec < floor {effective_floor:,} ops/sec")
            else:
                margin = ((ops - effective_floor) / effective_floor) * 100.0
                print(f"  [PASS] {name}: {ops:,} ops/sec ({ms} ms, +{margin:.1f}% above calibrated floor {effective_floor:,})")
        else:
            print(f"  [INFO] {name}: {ops:,} ops/sec ({ms} ms)")

    if regressions:
        print("\n[FAILED] Performance regressions detected:")
        for r in regressions:
            print(f"  - {r}")
        return 1

    print("\nALL PERFORMANCE BENCHMARKS WITHIN BOUNDS! ZERO REGRESSIONS DETECTED.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
