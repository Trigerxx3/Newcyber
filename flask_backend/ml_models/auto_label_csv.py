"""
Auto-prefill CSV `label` column (0/1) using keyword rules + drugs.json.

Use this instead of Excel formulas. Review and fix mistakes before evaluation.

Examples:
  python ml_models/auto_label_csv.py -i labeling_100_all_platforms.csv -o labeling_labeled.csv
  python ml_models/auto_label_csv.py -i in.csv -o out.csv --only-empty
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Iterable, List, Set

# Parent on path for imports if needed
sys.path.insert(0, str(Path(__file__).parent.parent))

# Extra high-signal phrases (not always in drugs.json)
DEFAULT_EXTRA_DRUG_PHRASES: List[str] = [
    "fentanyl",
    "percocet",
    "oxycodone",
    "xanax",
    "benzo",
    "pills",
    "tabs",
    "gram",
    "grams",
    "ounce",
    "zip",
    "plug",
    "trap",
]

DEFAULT_TRADE_PHRASES: List[str] = [
    "for sale",
    "on sale",
    "dm me",
    "dm for",
    "hit me up",
    "contact me",
    "whatsapp",
    "wtsapp",
    "telegram",
    "price",
    "prices",
    "cash only",
    "crypto",
    "bitcoin",
    "delivery",
    "shipping",
    "meet up",
    "pickup",
]


def load_keywords_from_drugs_json(path: Path) -> tuple[Set[str], Set[str], Set[str], Set[str]]:
    """Returns (drug_terms, selling_terms, buying_terms, auxiliary_terms)."""
    drug_terms: Set[str] = set()
    selling: Set[str] = set()
    buying: Set[str] = set()
    auxiliary: Set[str] = set()

    if not path.exists():
        return drug_terms, selling, buying, auxiliary

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    drugs = data.get("drugs") or {}
    for _cat, terms in drugs.items():
        if isinstance(terms, list):
            for t in terms:
                if isinstance(t, str) and t.strip():
                    drug_terms.add(t.strip().lower())

    intent = data.get("intent_keywords") or {}
    for t in intent.get("selling") or []:
        if isinstance(t, str) and t.strip():
            selling.add(t.strip().lower())
    for t in intent.get("buying") or []:
        if isinstance(t, str) and t.strip():
            buying.add(t.strip().lower())

    for key in ("payment_keywords", "location_keywords", "urgency_keywords"):
        for t in data.get(key) or []:
            if isinstance(t, str) and t.strip():
                auxiliary.add(t.strip().lower())

    return drug_terms, selling, buying, auxiliary


def _contains_phrase(text_lower: str, phrase: str) -> bool:
    p = phrase.lower().strip()
    if not p:
        return False
    if " " in p:
        return p in text_lower
    # single token: word boundary to reduce false positives
    return bool(re.search(rf"\b{re.escape(p)}\b", text_lower))


def any_phrase_match(text_lower: str, phrases: Iterable[str]) -> bool:
    return any(_contains_phrase(text_lower, p) for p in phrases)


def auto_label_text(
    text: str,
    drug_terms: Set[str],
    selling: Set[str],
    buying: Set[str],
    auxiliary: Set[str],
) -> int:
    if not text or not str(text).strip():
        return 0

    t = str(text).lower()

    # 1) Any drug keyword from drugs.json (+ extras)
    all_drugs = set(drug_terms)
    for p in DEFAULT_EXTRA_DRUG_PHRASES:
        all_drugs.add(p.lower())

    if any_phrase_match(t, all_drugs):
        return 1

    # 2) Strong trade / contact signals
    if any_phrase_match(t, DEFAULT_TRADE_PHRASES):
        # Require also some "intent" or auxiliary to reduce spam-only hits
        has_intent = any_phrase_match(t, selling) or any_phrase_match(t, buying)
        has_aux = any_phrase_match(t, auxiliary)
        if has_intent or has_aux:
            return 1

    # 3) Buying/selling language + payment/location/urgency (from JSON)
    if (any_phrase_match(t, selling) or any_phrase_match(t, buying)) and any_phrase_match(
        t, auxiliary
    ):
        return 1

    return 0


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Auto-prefill label column in CSV using keyword rules.")
    p.add_argument("-i", "--input", required=True, help="Input CSV path")
    p.add_argument("-o", "--output", required=True, help="Output CSV path")
    p.add_argument("--text-column", default="text", help="Text column name (default: text)")
    p.add_argument("--label-column", default="label", help="Label column name (default: label)")
    p.add_argument(
        "--only-empty",
        action="store_true",
        help="Only fill label where current label is blank",
    )
    p.add_argument(
        "--drugs-json",
        default="",
        help="Path to drugs.json (default: flask_backend/drugs.json next to project root)",
    )
    p.add_argument(
        "--add-auto-column",
        action="store_true",
        help="Also write column auto_label with model suggestion; still sets label unless --only-empty",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    in_path = Path(args.input)
    out_path = Path(args.output)

    drugs_path = Path(args.drugs_json) if args.drugs_json else Path(__file__).parent.parent / "drugs.json"
    drug_terms, selling, buying, auxiliary = load_keywords_from_drugs_json(drugs_path)

    with open(in_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise SystemExit("Input CSV has no header row.")
        fieldnames = list(reader.fieldnames)
        if args.text_column not in fieldnames:
            raise SystemExit(f"Missing text column {args.text_column!r}. Found: {fieldnames}")
        if args.label_column not in fieldnames:
            fieldnames.append(args.label_column)
        if args.add_auto_column and "auto_label" not in fieldnames:
            fieldnames.append("auto_label")

        rows_out: List[dict] = []
        filled = 0
        skipped = 0

        for row in reader:
            text = (row.get(args.text_column) or "").strip()
            suggested = auto_label_text(text, drug_terms, selling, buying, auxiliary)

            if args.add_auto_column:
                row["auto_label"] = str(suggested)

            current = (row.get(args.label_column) or "").strip()
            if args.only_empty:
                if not current:
                    row[args.label_column] = str(suggested)
                    filled += 1
                else:
                    skipped += 1
            else:
                row[args.label_column] = str(suggested)
                filled += 1

            rows_out.append(row)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows_out)

    print(f"Wrote: {out_path}")
    print(f"Rows: {len(rows_out)} | labels set: {filled}" + (f" | skipped (kept): {skipped}" if args.only_empty else ""))
    print("Review labels in Excel/editor, then run evaluate_telegram_dataset.py")


if __name__ == "__main__":
    main()
