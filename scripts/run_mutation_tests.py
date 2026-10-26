#!/usr/bin/env python3
"""
scripts/run_mutation_tests.py
Automated mutation testing for Noxen with baseline pre-checks, isolated temporary workspace,
and granular outcome classification (Assertion, Timeout, Compilation, Runtime).

Security & Reliability Guarantees:
- Pre-mutation baseline verification: verifies all target test suites pass cleanly on unmutated code
  to guarantee zero false positives.
- Never modifies working tree files in-place: copies files to a temporary workspace
  (tempfile.TemporaryDirectory) so repository code is NEVER corrupted or dirtied.
- Enforces strict execution timeout (20s) to kill infinite loops and recursive cycle mutants.
- Granular outcome classification: KILLED_ASSERTION, KILLED_TIMEOUT, COMPILE_ERROR, RUNTIME_ERROR, SURVIVED.
"""

import os
import sys
import shutil
import tempfile
import subprocess

MUTATIONS = [
    {
        "name": "Mutant 1: Invert string min_length condition in schema.nox",
        "file": "schema.nox",
        "original": "if field.has_min_len and len(sv) < field.min_len:",
        "mutated": "if False and field.has_min_len and len(sv) < field.min_len:",
        "test": "tests/unit/validators_test.nox",
    },
    {
        "name": "Mutant 2: Disable non-finite float check in serialization.nox",
        "file": "serialization.nox",
        "original": "if not is_finite_float(v):",
        "mutated": "if False and not is_finite_float(v):",
        "test": "tests/unit/serializer_strict_test.nox",
    },
    {
        "name": "Mutant 3: Invert POLICY_FORBID unexpected field check in schema.nox",
        "file": "schema.nox",
        "original": "if self.policy == POLICY_FORBID:",
        "mutated": "if False and self.policy == POLICY_FORBID:",
        "test": "tests/unit/unknown_fields_test.nox",
    },
    {
        "name": "Mutant 4: Disable cycle detection in derive_from_class_internal",
        "file": "schema.nox",
        "original": "if _is_in_derivation_stack(stack, class_name):",
        "mutated": "if False and _is_in_derivation_stack(stack, class_name):",
        "test": "tests/unit/auto_schema_test.nox",
    },
    {
        "name": "Mutant 5: Disable duplicate key detection in Serializer._record_key",
        "file": "serialization.nox",
        "original": "if self._strict_keys and (k in self._written_map):",
        "mutated": "if False and self._strict_keys and (k in self._written_map):",
        "test": "tests/unit/serializer_strict_test.nox",
    },
    {
        "name": "Mutant 6: Disable in-memory POLICY_FORBID check in validate_data_at",
        "file": "schema.nox",
        "original": "if self.policy == POLICY_FORBID:\n            t_keys: list[str] = data.top_level_keys()",
        "mutated": "if False and self.policy == POLICY_FORBID:\n            t_keys: list[str] = data.top_level_keys()",
        "test": "tests/unit/validate_data_parity_test.nox",
    },
]

def copy_repo_to_workspace(src_dir: str, dst_dir: str) -> None:
    """Copies required source and test files to an isolated workspace directory."""
    ignore_patterns = shutil.ignore_patterns(
        ".git", "build", "__pycache__", ".pytest_cache", ".gemini", ".system_generated"
    )
    for item in os.listdir(src_dir):
        if item in [".git", "build", "__pycache__", ".pytest_cache", ".gemini", ".system_generated"]:
            continue
        s = os.path.join(src_dir, item)
        d = os.path.join(dst_dir, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, ignore=ignore_patterns, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

def main() -> int:
    noxc_cmd = shutil.which("noxc") or "noxc"
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    print("=== Noxen Automated Mutation Testing (Isolated Workspace) ===")
    print(f"Compiler binary: {noxc_cmd}")
    print(f"Repository root: {repo_root}")
    print(f"Total Mutants:   {len(MUTATIONS)}\n")

    killed_assertion = 0
    killed_timeout = 0
    compile_errors = 0
    runtime_errors = 0
    survived = 0

    with tempfile.TemporaryDirectory(prefix="noxen_mut_") as tmp_workspace:
        print(f"Created isolated temporary mutation workspace: {tmp_workspace}")
        copy_repo_to_workspace(repo_root, tmp_workspace)

        # Baseline Pre-check: Ensure all target test suites pass cleanly on unmutated code
        print("\n--- Baseline Pre-Check: Verifying unmutated test suites pass ---")
        tests_to_check = sorted(list(set(m["test"] for m in MUTATIONS)))
        for t in tests_to_check:
            res_base = subprocess.run(
                [noxc_cmd, "run", t],
                cwd=tmp_workspace,
                capture_output=True,
                text=True,
                timeout=20,
            )
            if res_base.returncode != 0:
                print(f"[FAIL] Baseline test '{t}' failed before mutation! (exit code {res_base.returncode})")
                print(res_base.stdout)
                print(res_base.stderr)
                return 1
            print(f"  [BASELINE OK] {t} passed cleanly")
        print("Baseline pre-check complete. All target suites verified healthy.\n")

        # Apply and evaluate each mutant
        for i, m in enumerate(MUTATIONS, 1):
            name = m["name"]
            rel_file = m["file"]
            rel_test = m["test"]
            print(f"[{i}/{len(MUTATIONS)}] Applying {name}...")

            target_file = os.path.join(tmp_workspace, rel_file)
            with open(target_file, "r", encoding="utf-8") as f:
                content = f.read()

            if m["original"] not in content:
                print(f"[ERROR] Target mutation text not found in {target_file}: {m['original']}")
                return 1

            mutated_content = content.replace(m["original"], m["mutated"], 1)

            try:
                # Apply mutation ONLY in temporary workspace
                with open(target_file, "w", encoding="utf-8") as f:
                    f.write(mutated_content)

                # Run target test with strict 20s timeout in temporary workspace
                res = subprocess.run(
                    [noxc_cmd, "run", rel_test],
                    cwd=tmp_workspace,
                    capture_output=True,
                    text=True,
                    timeout=20,
                )

                if res.returncode != 0:
                    output_combined = ((res.stdout or "") + (res.stderr or "")).lower()
                    if "syntax error:" in output_combined or "type error:" in output_combined or "codegen:" in output_combined:
                        compile_errors += 1
                        print(f"    [COMPILE_ERROR] Test '{rel_test}' failed with compiler error (exit code {res.returncode})")
                    elif "assertionerror" in output_combined or "assert" in output_combined or "failed" in output_combined or res.returncode == 1:
                        killed_assertion += 1
                        print(f"    [KILLED_ASSERTION] Test '{rel_test}' caught mutant via assertion failure (exit code {res.returncode})!")
                    else:
                        runtime_errors += 1
                        print(f"    [RUNTIME_ERROR] Test '{rel_test}' caught mutant via runtime error (exit code {res.returncode})!")
                else:
                    print(f"    [SURVIVED] WARNING: Test '{rel_test}' passed despite mutation!")
                    survived += 1

            except subprocess.TimeoutExpired:
                killed_timeout += 1
                print(f"    [KILLED_TIMEOUT] Test '{rel_test}' timed out after 20s (infinite loop prevented)!")

            finally:
                # Restore original file inside temp workspace for the next mutant
                with open(target_file, "w", encoding="utf-8") as f:
                    f.write(content)

    total_killed = killed_assertion + killed_timeout + runtime_errors
    mutation_score = (total_killed / len(MUTATIONS)) * 100.0

    print(f"\nMutation Testing Summary:")
    print(f"  Killed by Assertion: {killed_assertion}")
    print(f"  Killed by Timeout:   {killed_timeout}")
    print(f"  Compiler Errors:     {compile_errors}")
    print(f"  Runtime Errors:      {runtime_errors}")
    print(f"  Mutants Survived:    {survived}")
    print(f"  Total Mutants:       {len(MUTATIONS)}")
    print(f"  Mutation Score:      {mutation_score:.1f}%")

    if survived > 0 or compile_errors > 0:
        if survived > 0:
            print("\n[FAIL] Some mutants survived. Strengthen test assertions!")
        if compile_errors > 0:
            print("\n[FAIL] Some mutants produced compiler errors. Fix mutation constructs!")
        return 1

    print("\nALL MUTANTS SUCCESSFULLY KILLED! Test suite has high fault-detection coverage.")
    print("Pre-mutation baseline verified and repository working tree remained 100% clean.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
