"""Summarize turning movement counts for a single intersection.

Reads a CSV with columns: approach,left,through,right
and prints volumes per movement, per approach, and for the whole intersection.

Missing or invalid volumes are NOT treated as zero. They are shown as "n/a",
reported as warnings, and any total that excludes them is marked with "*".

Usage:
    python volume_summary.py                      # uses samples/turning_counts.csv
    python volume_summary.py path/to/counts.csv
    python volume_summary.py --csv                # also save to output/<name>_summary.csv
"""

import argparse
import csv
import sys
from pathlib import Path

APPROACHES = ["NB", "SB", "EB", "WB"]
MOVEMENTS = [("L", "left"), ("T", "through"), ("R", "right")]
DEFAULT_INPUT = Path(__file__).parent / "samples" / "turning_counts.csv"
OUTPUT_DIR = Path(__file__).parent / "output"
MISSING = "n/a"
NOTE_MISSING = "missing"
NOTE_INCOMPLETE = "incomplete - excludes missing movements"


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


def write_csv(out_path, rows):
    """Save the summary. rows: (level, item, volume or None, note)."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # utf-8-sig so Excel opens it with the right encoding.
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["Level", "Item", "Volume", "Note"])
        for level, item, volume, note in rows:
            # Leave missing volumes blank so the column stays numeric in Excel.
            writer.writerow([level, item, "" if volume is None else volume, note])


def parse_args():
    parser = argparse.ArgumentParser(
        description="Summarize turning movement counts for one intersection."
    )
    parser.add_argument(
        "input",
        nargs="?",
        default=DEFAULT_INPUT,
        type=Path,
        help="counts CSV (default: samples/turning_counts.csv)",
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        help="also save the summary to output/<input name>_summary.csv",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    path = args.input
    if not path.exists():
        print(f"Input file not found: {path}", file=sys.stderr)
        sys.exit(1)

    counts, warnings = read_counts(path)
    csv_rows = []

    # Movement volumes: NBL, NBT, NBR, SBL, ... WBR
    movement_rows = []
    for approach in APPROACHES:
        for code, _ in MOVEMENTS:
            value = counts[approach][code]
            movement_rows.append((approach + code, fmt(value)))
            csv_rows.append(
                (
                    "Movement",
                    approach + code,
                    value,
                    "" if value is not None else NOTE_MISSING,
                )
            )

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
        csv_rows.append(
            ("Approach", approach, subtotal, "" if complete else NOTE_INCOMPLETE)
        )

    grand_total, complete = total(all_values)
    approach_rows.append(("Total", fmt(grand_total, complete)))
    csv_rows.append(
        ("Intersection", "Total", grand_total, "" if complete else NOTE_INCOMPLETE)
    )

    print(f"Intersection volume summary: {path.name}\n")
    print_table("Movement", movement_rows)
    print_table("Approach", approach_rows)

    if any_incomplete:
        print("* Incomplete: total excludes movements with missing volumes.")

    if args.csv:
        out_path = OUTPUT_DIR / f"{path.stem}_summary.csv"
        try:
            write_csv(out_path, csv_rows)
        except PermissionError:
            # Usually means the file is open in Excel, which locks it.
            print(
                f"\nCould not save {out_path.name}: close it in Excel and run again.",
                file=sys.stderr,
            )
            sys.exit(1)
        print(f"\nSaved summary to {out_path}")

    if warnings:
        print("\nWarnings:", file=sys.stderr)
        for w in warnings:
            print(f"  - {w}", file=sys.stderr)


if __name__ == "__main__":
    main()
