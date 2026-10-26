#!/usr/bin/env python3
"""
scripts/verify_json_schema.py
Independent standards-compliance validator & differential testing engine for Noxen.
Validates Noxen's generated schema against official Draft 2020-12 metaschema
and runs differential testing across a matrix of payloads to prove 100% agreement.
"""

import subprocess
import json
import sys
from jsonschema import Draft202012Validator

def main():
    print("1. Running scripts/dump_schemas.nox via noxc...")
    res = subprocess.run(
        ["noxc", "run", "scripts/dump_schemas.nox"],
        capture_output=True,
        text=True,
        check=True
    )

    output = res.stdout

    # Extract schema
    start_tag = "---SCHEMA_START---"
    end_tag = "---SCHEMA_END---"
    start_idx = output.find(start_tag)
    end_idx = output.find(end_tag)
    if start_idx == -1 or end_idx == -1:
        print("ERROR: Could not find schema tags in noxc output:")
        print(output)
        sys.exit(1)

    schema_text = output[start_idx + len(start_tag):end_idx].strip()
    schema = json.loads(schema_text)

    print("2. Validating Noxen schema against official JSON Schema Draft 2020-12 metaschema...")
    Draft202012Validator.check_schema(schema)
    print("   [OK] Noxen schema strictly conforms to Draft 2020-12 metaschema.")

    validator = Draft202012Validator(schema)

    # Extract differential test cases
    c_start_tag = "---CASES_START---"
    c_end_tag = "---CASES_END---"
    c_start_idx = output.find(c_start_tag)
    c_end_idx = output.find(c_end_tag)
    if c_start_idx == -1 or c_end_idx == -1:
        print("ERROR: Could not find cases tags in noxc output:")
        print(output)
        sys.exit(1)

    cases_block = output[c_start_idx + len(c_start_tag):c_end_idx].strip()
    lines = [line.strip() for line in cases_block.splitlines() if line.strip()]

    if len(lines) < 14:
        print(f"FATAL ERROR: Expected at least 14 differential test scenarios, but found {len(lines)}")
        sys.exit(1)

    print(f"\n3. Running Differential Testing across {len(lines)} test scenarios...")
    print("   Comparing Noxen validation results against Python Draft202012Validator:")

    mismatch_count = 0
    executed_count = 0
    for line_idx, line in enumerate(lines, 1):
        parts = line.split(":::")
        if len(parts) != 3:
            print(f"FATAL ERROR: Malformed differential test line #{line_idx}: '{line}' (expected exactly 3 ':::'-separated parts)")
            sys.exit(1)

        case_name, noxen_verdict, payload_str = parts
        try:
            payload = json.loads(payload_str)
        except json.JSONDecodeError as e:
            print(f"FATAL ERROR: Invalid JSON payload in scenario '{case_name}': {e}")
            sys.exit(1)

        py_is_valid = validator.is_valid(payload)
        py_verdict = "VALID" if py_is_valid else "REJECTED"

        if noxen_verdict != py_verdict:
            print(f"   [MISMATCH] Case '{case_name}': Noxen={noxen_verdict} vs Python={py_verdict}")
            mismatch_count += 1
        else:
            print(f"   [DIFFERENTIAL OK] Case '{case_name}': Both agreed on {py_verdict}")
        executed_count += 1

    if mismatch_count > 0:
        print(f"\nFAILED: {mismatch_count} differential testing mismatches found!")
        sys.exit(1)

    print(f"\nALL {executed_count} DIFFERENTIAL TEST SCENARIOS PASSED WITH 100% AGREEMENT!")
    print("Noxen runtime validation and emitted JSON Schema Draft 2020-12 agree 100% across all evaluated scenarios.")

if __name__ == "__main__":
    main()
