#!/usr/bin/env python3
"""
scripts/check_performance_regression.py
Automated performance regression checker for Noxen.

Runs benchmarks/run_benchmarks.nox and enforces throughput floors to prevent
latency and memory regressions across commits and CI runs.
"""

import re
import sys
import shutil
import subprocess

# Minimum acceptable throughput floors (ops/sec) to prevent performance regressions
PERFORMANCE_FLOORS = {
    "Flat Model Parsing": 250000,
    "Nested Model Parsing": 200000,
    "Invalid Payload Reject": 400000,
    "Full JSON Round-Trip": 250000,
    "Deep Hierarchy Parsing": 150000,
    "Fast Model Dump": 400000,
    "Validated Model Dump": 200000,
}

def main() -> int:
    noxc_cmd = shutil.which("noxc") or "noxc"
    print("=== Noxen Performance Regression Gate ===")
    print(f"Compiler binary: {noxc_cmd}")

    cmd = [noxc_cmd, "run", "benchmarks/run_benchmarks.nox"]
    res = subprocess.run(cmd, capture_output=True, text=True)

    if res.returncode != 0:
        print(f"[FAIL] Benchmark execution failed (exit code {res.returncode}):")
        print(res.stderr)
        return 1

    print("\nBenchmark Output:")
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

        floor = None
        for key, threshold in PERFORMANCE_FLOORS.items():
            if key in name:
                floor = threshold
                break

        if floor is not None:
            if ops < floor:
                regressions.append(f"{name}: {ops} ops/sec (BELOW FLOOR {floor} ops/sec, {ms} ms)")
                print(f"  [REGRESSION] {name}: {ops} ops/sec < floor {floor} ops/sec")
            else:
                margin = ((ops - floor) / floor) * 100.0
                print(f"  [PASS] {name}: {ops:,} ops/sec ({ms} ms, +{margin:.1f}% above floor {floor:,})")
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
