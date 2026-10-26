#!/usr/bin/env python3
"""
scripts/run_mutation_tests.py
Automated mutation testing for Noxen.

Introduces controlled faults into core validation & serialization logic and verifies
that the test suite immediately catches and kills each mutant.
"""

import sys
import shutil
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

def main() -> int:
    noxc_cmd = shutil.which("noxc") or "noxc"
    print("=== Noxen Automated Mutation Testing ===")
    print(f"Compiler binary: {noxc_cmd}")
    print(f"Total Mutants: {len(MUTATIONS)}\n")

    killed = 0
    survived = 0

    for i, m in enumerate(MUTATIONS, 1):
        name = m["name"]
        filepath = m["file"]
        testpath = m["test"]
        print(f"[{i}/{len(MUTATIONS)}] Applying {name}...")

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        if m["original"] not in content:
            print(f"[ERROR] Target mutation text not found in {filepath}: {m['original']}")
            return 1

        mutated_content = content.replace(m["original"], m["mutated"], 1)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(mutated_content)

            # Run target test to see if it catches the mutation
            res = subprocess.run([noxc_cmd, "run", testpath], capture_output=True, text=True)

            if res.returncode != 0:
                print(f"    [KILLED] Test '{testpath}' caught mutant (exit code {res.returncode})!")
                killed += 1
            else:
                print(f"    [SURVIVED] WARNING: Test '{testpath}' passed despite mutation!")
                survived += 1

        finally:
            # Always restore original file
            with open(filepath, "w", encoding="utf-8") as f:
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
    return 0

if __name__ == "__main__":
    sys.exit(main())
