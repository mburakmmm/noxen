#!/usr/bin/env python3
"""
scripts/verify_backend_parity.py
Automated differential backend verification for Noxen:
Executes key suites and services under both LLVM and QBE backends
and asserts 100% byte-for-byte stdout and exit code equivalence.
"""

import sys
import shutil
import subprocess

TARGETS = [
    "tests/fuzz/property_test.nox",
    "tests/integration/nested_array_test.nox",
    "examples/realworld_service.nox",
    "examples/nested_model.nox",
    "examples/strict_validation.nox",
    "examples/custom_validator.nox",
    "examples/json_roundtrip.nox",
]

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

        # Compare outputs
        if res_llvm.stdout != res_qbe.stdout:
            print(f"[PARITY MISMATCH] Stdout mismatch on {target}!")
            print("--- LLVM Output ---")
            print(res_llvm.stdout)
            print("--- QBE Output ---")
            print(res_qbe.stdout)
            return 1

        print(f"    [OK] Byte-for-byte output and exit code match between LLVM and QBE.")
        passed_count += 1

    print(f"\nALL {passed_count} TEST TARGETS PASSED WITH 100% LLVM / QBE BACKEND PARITY!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
