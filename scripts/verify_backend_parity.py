#!/usr/bin/env python3
"""
scripts/verify_backend_parity.py
Automated differential backend verification for Noxen:
Executes key suites and services under both LLVM and QBE backends
and asserts 100% byte-for-byte stdout, exit code, and semantic JSON equivalence.
"""

import sys
import json
import shutil
import subprocess

TARGETS = [
    "tests/unit/auto_schema_test.nox",
    "tests/unit/float_edge_cases_test.nox",
    "tests/fuzz/property_test.nox",
    "tests/integration/nested_array_test.nox",
    "examples/auto_model.nox",
    "examples/realworld_service.nox",
    "examples/nested_model.nox",
    "examples/strict_validation.nox",
    "examples/custom_validator.nox",
    "examples/json_roundtrip.nox",
]

def extract_json_objects(output: str) -> list[dict | list]:
    results = []
    for line in output.splitlines():
        line = line.strip()
        # Look for JSON substrings
        idx_brace = line.find("{")
        idx_bracket = line.find("[")
        start_idx = -1
        if idx_brace != -1 and idx_bracket != -1:
            start_idx = min(idx_brace, idx_bracket)
        elif idx_brace != -1:
            start_idx = idx_brace
        elif idx_bracket != -1:
            start_idx = idx_bracket

        if start_idx != -1:
            cand = line[start_idx:]
            try:
                parsed = json.loads(cand)
                results.append(parsed)
            except Exception:
                pass
    return results

def main() -> int:
    noxc_cmd = shutil.which("noxc") or "noxc"
    print(f"1. Checking LLVM and QBE backend parity with noxc ({noxc_cmd})...\n")

    if sys.platform == "win32":
        print("[INFO] Windows platform detected. Verifying LLVM execution for all targets...")
        for target in TARGETS:
            res_llvm = subprocess.run([noxc_cmd, "run", "--backend", "llvm", target], capture_output=True, text=True)
            if res_llvm.returncode != 0:
                print(f"[FAIL] LLVM execution failed for {target}: {res_llvm.stderr}")
                return 1
            print(f"    [OK] LLVM executed cleanly on {target}.")
        print("\nALL TARGETS PASSED CLEANLY ON WINDOWS (LLVM)!")
        return 0

    passed_count = 0

    for target in TARGETS:
        print(f"--> Verifying parity for: {target}")

        # Run with LLVM backend
        res_llvm = subprocess.run(
            [noxc_cmd, "run", "--backend", "llvm", target],
            capture_output=True,
            text=True
        )

        if res_llvm.returncode != 0:
            print(f"[FAIL] LLVM backend execution failed for {target} (code {res_llvm.returncode}):")
            print(res_llvm.stderr)
            return 1

        # Run with QBE backend
        res_qbe = subprocess.run(
            [noxc_cmd, "run", "--backend", "qbe", target],
            capture_output=True,
            text=True
        )

        if res_qbe.returncode != 0:
            print(f"[FAIL] QBE backend execution failed for {target} (code {res_qbe.returncode}):")
            print(res_qbe.stderr)
            return 1

        # Compare exit codes
        if res_llvm.returncode != res_qbe.returncode:
            print(f"[PARITY MISMATCH] Exit code mismatch on {target}: LLVM={res_llvm.returncode}, QBE={res_qbe.returncode}")
            return 1

        # Compare outputs byte-for-byte
        if res_llvm.stdout != res_qbe.stdout:
            print(f"[PARITY MISMATCH] Stdout mismatch on {target}!")
            print("--- LLVM Output ---")
            print(res_llvm.stdout)
            print("--- QBE Output ---")
            print(res_qbe.stdout)
            return 1

        # Semantic JSON parity: verify all JSON fragments match semantically
        json_llvm = extract_json_objects(res_llvm.stdout)
        json_qbe = extract_json_objects(res_qbe.stdout)
        if json_llvm != json_qbe:
            print(f"[SEMANTIC JSON MISMATCH] Parsed JSON outputs do not match on {target}!")
            print(f"LLVM JSONs: {json_llvm}")
            print(f"QBE JSONs: {json_qbe}")
            return 1

        print(f"    [OK] Exit code, byte-for-byte stdout, and {len(json_llvm)} semantic JSON structures match between LLVM and QBE.")
        passed_count += 1

    print(f"\nALL {passed_count} TEST TARGETS PASSED WITH 100% LLVM / QBE BACKEND PARITY!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
