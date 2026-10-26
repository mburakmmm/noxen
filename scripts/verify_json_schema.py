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

    EXPECTED_SCENARIOS = {
        "valid_full",
        "valid_null_website",
        "valid_omit_website",
        "reject_null_username",
        "reject_missing_username",
        "reject_min_id",
        "reject_max_id",
        "reject_min_items",
        "reject_tax_id_pattern",
        "reject_nested_street_length",
        "reject_additional_property",
        "reject_role_choice",
        "reject_score_min",
        "reject_score_max",
    }

    if len(lines) < len(EXPECTED_SCENARIOS):
        print(f"FATAL ERROR: Expected at least {len(EXPECTED_SCENARIOS)} differential test scenarios, but found {len(lines)}")
        sys.exit(1)

    print(f"\n3. Running Differential Testing across {len(lines)} test scenarios...")
    print("   Comparing Noxen validation results against Python Draft202012Validator:")

    mismatch_count = 0
    executed_scenarios = set()
    for line_idx, line in enumerate(lines, 1):
        parts = line.split(":::")
        if len(parts) != 3:
            print(f"FATAL ERROR: Malformed differential test line #{line_idx}: '{line}' (expected exactly 3 ':::'-separated parts)")
            sys.exit(1)

        case_name, noxen_verdict, payload_str = parts

        # Validate case name uniqueness and expectation
        if case_name in executed_scenarios:
            print(f"FATAL ERROR: Duplicate differential scenario '{case_name}' encountered at line #{line_idx}")
            sys.exit(1)
        if case_name not in EXPECTED_SCENARIOS:
            print(f"FATAL ERROR: Unexpected differential scenario '{case_name}' encountered at line #{line_idx}")
            sys.exit(1)

        # Validate noxen_verdict syntax
        if noxen_verdict not in ("VALID", "REJECTED"):
            print(f"FATAL ERROR: Unknown noxen_verdict '{noxen_verdict}' in scenario '{case_name}' (expected 'VALID' or 'REJECTED')")
            sys.exit(1)

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
        executed_scenarios.add(case_name)

    missing_scenarios = EXPECTED_SCENARIOS - executed_scenarios
    if missing_scenarios:
        print(f"FATAL ERROR: Missing required differential scenario(s): {missing_scenarios}")
        sys.exit(1)

    if mismatch_count > 0:
        print(f"\nFAILED: {mismatch_count} differential testing mismatches found!")
        sys.exit(1)

    print(f"\nALL {len(executed_scenarios)} EXPECTED DIFFERENTIAL TEST SCENARIOS PASSED WITH 100% AGREEMENT!")
    print("Noxen runtime validation and emitted JSON Schema Draft 2020-12 agree 100% across all evaluated scenarios.")

if __name__ == "__main__":
    main()
