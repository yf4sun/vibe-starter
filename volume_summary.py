"""Summarize turning movement counts for a single intersection.

Reads a CSV with columns: approach,left,through,right
and prints volumes per movement, per approach, and for the whole intersection.

Missing or invalid volumes are NOT treated as zero. They are shown as "n/a",
reported as warnings, and any total that excludes them is marked with "*".

Usage:
    python volume_summary.py                      # uses samples/turning_counts.csv
    python volume_summary.py path/to/counts.csv
"""

import csv
import sys
from pathlib import Path

APPROACHES = ["NB", "SB", "EB", "WB"]
MOVEMENTS = [("L", "left"), ("T", "through"), ("R", "right")]
DEFAULT_INPUT = Path(__file__).parent / "samples" / "turning_counts.csv"
MISSING = "n/a"


def read_counts(path):
    """Return ({approach: {movement_code: int | None}}, [warnings])."""
    counts = {a: {code: None for code, _ in MOVEMENTS} for a in APPROACHES}
    seen = set()
    warnings = []

    # utf-8-sig strips the hidden BOM that Excel adds when saving CSVs.
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for line_no, row in enumerate(reader, start=2):
            approach = (row.get("approach") or "").strip().upper()
            if approach not in counts:
                warnings.append(
                    f"Line {line_no}: unknown approach '{approach}', row skipped."
                )
                continue
            if approach in seen:
                warnings.append(
                    f"Line {line_no}: duplicate {approach} row; later values used."
                )
            seen.add(approach)

            for code, column in MOVEMENTS:
                movement = approach + code
                # Short rows give None for trailing columns, blank cells give "".
                raw = (row.get(column) or "").strip()
                if raw == "":
                    warnings.append(f"{movement}: no volume given.")
                    continue
                try:
                    value = int(raw)
                except ValueError:
                    warnings.append(f"{movement}: '{raw}' is not a whole number.")
                    continue
                if value < 0:
                    warnings.append(f"{movement}: negative volume ({value}) ignored.")
                    continue
                counts[approach][code] = value

    for approach in APPROACHES:
        if approach not in seen:
            warnings.append(f"{approach}: no row found in the file.")

    return counts, warnings


def total(values):
    """Sum the known values. Return (sum, is_complete)."""
    known = [v for v in values if v is not None]
    return sum(known), len(known) == len(values)


def fmt(value, complete=True):
    """Format a volume, adding '*' when it excludes missing data."""
    if value is None:
        return MISSING
    return f"{value}" if complete else f"{value}*"


def print_table(header, rows):
    print(f"{header:<10}{'Volume':>8}")
    print(f"{'-' * 10}{'-' * 8:>8}")
    for label, value in rows:
        print(f"{label:<10}{value:>8}")
    print()


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    if not path.exists():
        print(f"Input file not found: {path}", file=sys.stderr)
        sys.exit(1)

    counts, warnings = read_counts(path)

    # Movement volumes: NBL, NBT, NBR, SBL, ... WBR
    movement_rows = [
        (approach + code, fmt(counts[approach][code]))
        for approach in APPROACHES
        for code, _ in MOVEMENTS
    ]

    # Approach and intersection totals
    approach_rows = []
    all_values = []
    any_incomplete = False
    for approach in APPROACHES:
        values = list(counts[approach].values())
        all_values.extend(values)
        subtotal, complete = total(values)
        any_incomplete |= not complete
        approach_rows.append((approach, fmt(subtotal, complete)))

    grand_total, complete = total(all_values)
    approach_rows.append(("Total", fmt(grand_total, complete)))

    print(f"Intersection volume summary: {path.name}\n")
    print_table("Movement", movement_rows)
    print_table("Approach", approach_rows)

    if any_incomplete:
        print("* Incomplete: total excludes movements with missing volumes.")

    if warnings:
        print("\nWarnings:", file=sys.stderr)
        for w in warnings:
            print(f"  - {w}", file=sys.stderr)


if __name__ == "__main__":
    main()
