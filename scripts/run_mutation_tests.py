#!/usr/bin/env python3
"""
scripts/run_mutation_tests.py
Automated mutation testing for Noxen with isolated temporary workspace and timeout guards.

Introduces controlled faults into core validation & serialization logic and verifies
that the test suite immediately catches and kills each mutant.

Security & Reliability Guarantees:
- Never modifies working tree files in-place: copies files to a temporary workspace
  (tempfile.TemporaryDirectory) so repository code is NEVER corrupted or dirtied.
- Enforces strict execution timeout (20s) to kill infinite loops and recursive cycle mutants.
- Distinguishes kill reasons (assertion failure vs timeout vs compilation error).
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
    print(f"Total Mutants: {len(MUTATIONS)}\n")

    killed = 0
    survived = 0

    with tempfile.TemporaryDirectory(prefix="noxen_mut_") as tmp_workspace:
        print(f"Created isolated temporary mutation workspace: {tmp_workspace}")
        copy_repo_to_workspace(repo_root, tmp_workspace)

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
                    output_combined = (res.stdout or "") + (res.stderr or "")
                    if "AssertionError" in output_combined or "assertion failed" in output_combined.lower() or "assert" in output_combined:
                        print(f"    [KILLED (Assertion Failure)] Test '{rel_test}' caught mutant (exit code {res.returncode})!")
                    else:
                        print(f"    [KILLED (Validation / Error Triggered)] Test '{rel_test}' caught mutant (exit code {res.returncode})!")
                    killed += 1
                else:
                    print(f"    [SURVIVED] WARNING: Test '{rel_test}' passed despite mutation!")
                    survived += 1

            except subprocess.TimeoutExpired:
                print(f"    [KILLED (Timeout / Infinite Loop Prevented)] Test '{rel_test}' timed out after 20s!")
                killed += 1

            finally:
                # Restore original file inside temp workspace for the next mutant
                with open(target_file, "w", encoding="utf-8") as f:
                    f.write(content)

    mutation_score = (killed / len(MUTATIONS)) * 100.0
    print(f"\nMutation Testing Results:")
    print(f"  Mutants Killed:   {killed}")
    print(f"  Mutants Survived: {survived}")
    print(f"  Mutation Score:   {mutation_score:.1f}%")

    if survived > 0:
        print("[FAIL] Some mutants survived. Strengthen test assertions!")
        return 1

    print("\nALL MUTANTS SUCCESSFULLY KILLED! Test suite has high fault-detection coverage.")
    print("Repository working tree remained 100% clean and untouched throughout execution.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
