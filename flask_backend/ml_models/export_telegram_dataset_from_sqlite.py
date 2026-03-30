"""
Export Telegram messages from SQLite into a labeling-ready CSV.

Default output columns:
- id
- text
- source_handle
- platform
- created_at
- label (blank, for manual annotation)
"""
from __future__ import annotations

import argparse
import csv
import sqlite3
from pathlib import Path
from typing import List, Tuple


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export Telegram content from SQLite for labeling/evaluation."
    )
    parser.add_argument(
        "--db-path",
        default="",
        help="Path to SQLite DB file. If omitted, auto-detects common DB files.",
    )
    parser.add_argument(
        "--output-csv",
        default="telegram_for_labeling.csv",
        help="Output CSV path (default: telegram_for_labeling.csv)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=1000,
        help="Maximum rows to export (default: 1000)",
    )
    parser.add_argument(
        "--platform",
        default="telegram",
        help="Platform filter (e.g., telegram, instagram, unknown, or all). Default: telegram",
    )
    return parser.parse_args()


def _table_exists(cur: sqlite3.Cursor, table_name: str) -> bool:
    row = cur.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    ).fetchone()
    return row is not None


def _column_exists(cur: sqlite3.Cursor, table_name: str, column_name: str) -> bool:
    rows = cur.execute(f"PRAGMA table_info({table_name})").fetchall()
    return any(r[1] == column_name for r in rows)


def _resolve_db_path(input_db_path: str) -> str:
    if input_db_path:
        return input_db_path

    candidates = [
        "cyber_intel.db",
        "instance/local.db",
        "local.db",
        "temp.db",
    ]
    for candidate in candidates:
        p = Path(candidate)
        if p.exists() and p.is_file() and p.stat().st_size > 0:
            return str(p)
    raise FileNotFoundError(
        "Could not auto-detect SQLite DB. Pass --db-path explicitly."
    )


def export_rows(db_path: str, limit: int, platform: str) -> List[Tuple]:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    source_table = "sources" if _table_exists(cur, "sources") else "source"
    if not _table_exists(cur, "content"):
        conn.close()
        raise RuntimeError(f"'content' table not found in DB: {db_path}")
    if not _table_exists(cur, source_table):
        conn.close()
        raise RuntimeError(f"'{source_table}' table not found in DB: {db_path}")

    # Support schema variants:
    # - content.text vs content.content_text vs content.content
    text_expr = "COALESCE(c.text, '')"
    if _column_exists(cur, "content", "content_text"):
        text_expr = "COALESCE(c.content_text, c.text, '')"
    elif _column_exists(cur, "content", "content"):
        text_expr = "COALESCE(c.content, c.text, '')"

    platform = (platform or "telegram").strip().lower()
    where_platform = "1=1" if platform == "all" else "LOWER(COALESCE(s.platform, '')) = ?"

    query = f"""
    SELECT
        c.id,
        {text_expr} AS text,
        s.source_handle,
        LOWER(COALESCE(s.platform, 'unknown')) AS platform,
        c.created_at
    FROM content c
    LEFT JOIN {source_table} s ON c.source_id = s.id
    WHERE {where_platform}
      AND TRIM({text_expr}) <> ''
    ORDER BY c.created_at DESC
    LIMIT ?
    """
    params = (limit,) if platform == "all" else (platform, limit)
    rows = cur.execute(query, params).fetchall()
    conn.close()
    return rows


def save_csv(rows: List[Tuple], output_csv: str) -> None:
    with open(output_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "text", "source_handle", "platform", "created_at", "label"])
        for row in rows:
            writer.writerow([row[0], row[1], row[2], row[3], row[4], ""])


def main() -> None:
    args = parse_args()
    db_path = _resolve_db_path(args.db_path)
    rows = export_rows(db_path, args.limit, args.platform)
    save_csv(rows, args.output_csv)
    print(f"DB used: {db_path}")
    print(f"Platform filter: {args.platform}")
    print(f"Exported {len(rows)} rows to {args.output_csv}")
    print("Next step: fill the 'label' column with 0/1 and run evaluate_telegram_dataset.py")


if __name__ == "__main__":
    main()
