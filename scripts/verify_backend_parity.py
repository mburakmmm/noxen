#!/usr/bin/env python3
"""
scripts/verify_backend_parity.py
Automated differential backend verification for Noxen across LLVM and QBE.

Supports two explicit verification modes:
  1. --mode semantic: Validates semantic JSON equivalence and structured NOXEN_RESULT_JSON verdicts,
                      ignoring non-semantic formatting/key-ordering variances.
  2. --mode strict:   Enforces byte-for-byte identical stdout and exit code equivalence.
  3. --mode all:      (Default) Runs both semantic structured validation and byte-for-byte parity.
"""

import sys
import json
import shutil
import argparse
import subprocess

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(line_buffering=True)

TARGETS = [
    {
        "path": "tests/unit/auto_schema_test.nox",
        "expected_markers": 1,
    },
    {
        "path": "tests/unit/float_edge_cases_test.nox",
        "expected_markers": 1,
    },
    {
        "path": "tests/unit/auto_model_test.nox",
        "expected_markers": 1,
    },
    {
        "path": "tests/unit/api_compatibility_test.nox",
        "expected_markers": 1,
    },
    {
        "path": "tests/fuzz/property_test.nox",
        "expected_markers": 1,
    },
    {
        "path": "tests/integration/nested_array_test.nox",
        "expected_markers": 1,
    },
    {
        "path": "examples/auto_model.nox",
        "expected_markers": 1,
    },
    {
        "path": "examples/realworld_service.nox",
        "expected_markers": 1,
    },
    {
        "path": "examples/nested_model.nox",
        "expected_markers": 1,
    },
    {
        "path": "examples/strict_validation.nox",
        "expected_markers": 1,
    },
    {
        "path": "examples/custom_validator.nox",
        "expected_markers": 1,
    },
    {
        "path": "examples/json_roundtrip.nox",
        "expected_markers": 1,
    },
    {
        "path": "examples/framework_adapter.nox",
        "expected_markers": 1,
    },
    {
        "path": "tests/unit/validate_data_parity_test.nox",
        "expected_markers": 1,
    },
]

MARKER = "NOXEN_RESULT_JSON:"

def extract_structured_json(output: str, path: str) -> list[dict]:
    results = []
    for line_num, line in enumerate(output.splitlines(), 1):
        idx = line.find(MARKER)
        if idx != -1:
            json_str = line[idx + len(MARKER):].strip()
            try:
                parsed = json.loads(json_str)
                results.append(parsed)
            except Exception as e:
                print(f"[FATAL ERROR] Malformed NOXEN_RESULT_JSON marker at line {line_num} in {path}: {json_str}")
                print(f"JSON Parse Error: {e}")
                sys.exit(1)
    return results

def main() -> int:
    parser = argparse.ArgumentParser(description="Verify LLVM and QBE Backend Parity for Noxen")
    parser.add_argument(
        "--mode",
        choices=["strict", "semantic", "all"],
        default="all",
        help="Parity mode: 'semantic' (JSON verdicts), 'strict' (byte-for-byte stdout), or 'all' (both)"
    )
    args = parser.parse_args()

    noxc_cmd = shutil.which("noxc") or "noxc"
    print(f"=== Noxen Dual-Backend Parity Verification (Mode: {args.mode.upper()}) ===")
    print(f"Compiler binary: {noxc_cmd}\n")

    if sys.platform == "win32":
        print("[INFO] Windows platform detected. Verifying LLVM execution and structured markers for all targets...")
        for target in TARGETS:
            path = target["path"]
            expected = target.get("expected_markers", 1)
            res_llvm = subprocess.run([noxc_cmd, "run", "--backend", "llvm", path], capture_output=True, text=True)
            if res_llvm.returncode != 0:
                print(f"[FAIL] LLVM execution failed for {path}: {res_llvm.stderr}")
                return 1
            if args.mode in ["semantic", "all"]:
                json_llvm = extract_structured_json(res_llvm.stdout, f"{path} [Windows LLVM]")
                if len(json_llvm) != expected:
                    print(f"[ERROR] Target {path} [Windows LLVM] produced {len(json_llvm)} markers, expected {expected}!")
                    return 1
            print(f"    [OK] LLVM executed cleanly on {path} with {expected} verified structured marker(s).")
        print("\nALL TARGETS PASSED CLEANLY ON WINDOWS (LLVM)!")
        return 0

    passed_count = 0

    for target in TARGETS:
        path = target["path"]
        expected = target.get("expected_markers", 1)
        print(f"--> Target: {path}")

        # Run with LLVM backend
        res_llvm = subprocess.run(
            [noxc_cmd, "run", "--backend", "llvm", path],
            capture_output=True,
            text=True
        )
        if res_llvm.returncode != 0:
            print(f"[FAIL] LLVM backend execution failed for {path} (exit code {res_llvm.returncode}):")
            print(res_llvm.stderr)
            return 1

        # Run with QBE backend
        res_qbe = subprocess.run(
            [noxc_cmd, "run", "--backend", "qbe", path],
            capture_output=True,
            text=True
        )
        if res_qbe.returncode != 0:
            print(f"[FAIL] QBE backend execution failed for {path} (exit code {res_qbe.returncode}):")
            print(res_qbe.stderr)
            return 1

        # 1. Exit code equivalence (always enforced)
        if res_llvm.returncode != res_qbe.returncode:
            print(f"[PARITY MISMATCH] Exit code mismatch on {path}: LLVM={res_llvm.returncode}, QBE={res_qbe.returncode}")
            return 1

        # 2. Semantic structured verification (if mode is semantic or all)
        if args.mode in ["semantic", "all"]:
            json_llvm = extract_structured_json(res_llvm.stdout, f"{path} [LLVM]")
            json_qbe = extract_structured_json(res_qbe.stdout, f"{path} [QBE]")

            if len(json_llvm) != expected:
                print(f"[ERROR] Target {path} [LLVM] produced {len(json_llvm)} markers, expected {expected}!")
                return 1
            if len(json_qbe) != expected:
                print(f"[ERROR] Target {path} [QBE] produced {len(json_qbe)} markers, expected {expected}!")
                return 1

            if json_llvm != json_qbe:
                print(f"[SEMANTIC PARITY MISMATCH] Structured JSON verdicts differ on {path}!")
                print(f"LLVM JSON: {json_llvm}")
                print(f"QBE JSON:  {json_qbe}")
                return 1
            print(f"    [SEMANTIC OK] Verified {len(json_llvm)} structured JSON verdict(s) between LLVM and QBE (expected {expected}).")

        # 3. Strict byte-for-byte verification (if mode is strict or all)
        if args.mode in ["strict", "all"]:
            if res_llvm.stdout != res_qbe.stdout:
                print(f"[STRICT PARITY MISMATCH] Byte-for-byte stdout mismatch on {path}!")
                print("--- LLVM Output ---")
                print(res_llvm.stdout)
                print("--- QBE Output ---")
                print(res_qbe.stdout)
                return 1
            print(f"    [STRICT OK] Byte-for-byte identical stdout and exit code between LLVM and QBE.")

        passed_count += 1

    print(f"\nALL {passed_count} TARGETS PASSED WITH 100% LLVM / QBE PARITY (Mode: {args.mode.upper()})!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
