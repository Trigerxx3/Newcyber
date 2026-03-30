"""
Evaluate ContentClassifier on a labeled Telegram CSV dataset.

Expected CSV columns (default):
- text: message text
- label: 0 or 1 (0 = Non-Drug-Related, 1 = Drug-Related)

Outputs:
- Console metrics (accuracy, precision, recall, F1, classification report)
- Text report file
- Confusion matrix PNG
- Precision/Recall/F1 bar chart PNG
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Ensure parent folder is on path so "ml_models" imports work when run as script.
sys.path.insert(0, str(Path(__file__).parent.parent))

from ml_models.content_classifier import ContentClassifier


@dataclass
class DatasetRow:
    text: str
    label: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate trained classifier on Telegram labeled CSV and generate graphs."
    )
    parser.add_argument(
        "--csv-path",
        required=True,
        help="Path to labeled CSV file, e.g. telegram_labeled.csv",
    )
    parser.add_argument(
        "--text-column",
        default="text",
        help="Name of text column (default: text)",
    )
    parser.add_argument(
        "--label-column",
        default="label",
        help="Name of label column (default: label)",
    )
    parser.add_argument(
        "--output-dir",
        default=os.path.join("results", "telegram_evaluation"),
        help="Directory to save reports and graphs",
    )
    return parser.parse_args()


def _parse_label(raw: str) -> int:
    value = str(raw).strip().lower()
    if value in {"1", "drug", "drug-related", "drug_related", "true", "yes"}:
        return 1
    if value in {"0", "non-drug", "non-drug-related", "non_drug_related", "false", "no"}:
        return 0
    raise ValueError(f"Unsupported label value: {raw!r}")


def load_labeled_csv(csv_path: str, text_column: str, label_column: str) -> List[DatasetRow]:
    rows: List[DatasetRow] = []
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV appears to be empty or missing headers.")
        missing = [c for c in (text_column, label_column) if c not in reader.fieldnames]
        if missing:
            raise ValueError(
                f"Missing required columns: {missing}. Found columns: {reader.fieldnames}"
            )

        for i, row in enumerate(reader, start=2):  # header is line 1
            text = (row.get(text_column) or "").strip()
            label_raw = (row.get(label_column) or "").strip()
            if not text or not label_raw:
                continue
            try:
                label = _parse_label(label_raw)
            except ValueError as exc:
                raise ValueError(f"Invalid label at CSV line {i}: {exc}") from exc
            rows.append(DatasetRow(text=text, label=label))

    if not rows:
        raise ValueError(
            "No valid labeled rows found. Ensure text and label columns are filled."
        )
    return rows


def evaluate_model(classifier: ContentClassifier, data: List[DatasetRow]) -> Tuple[List[int], List[int]]:
    y_true = [r.label for r in data]
    processed = [classifier._preprocess_text(r.text) for r in data]
    y_pred = classifier.model.predict(processed).tolist()
    return y_true, y_pred


def generate_graphs_and_reports(
    y_true: List[int],
    y_pred: List[int],
    output_dir: str,
) -> None:
    os.makedirs(output_dir, exist_ok=True)

    label_order = [0, 1]
    label_names = {0: "Non-Drug-Related", 1: "Drug-Related"}
    class_names = [label_names[l] for l in label_order]

    accuracy = accuracy_score(y_true, y_pred)
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=label_order, zero_division=0
    )

    report = classification_report(
        y_true,
        y_pred,
        labels=label_order,
        target_names=class_names,
        digits=4,
        zero_division=0,
    )

    # Save text report
    report_txt_path = os.path.join(output_dir, "evaluation_report.txt")
    with open(report_txt_path, "w", encoding="utf-8") as f:
        f.write("Telegram Dataset Evaluation Report\n")
        f.write("=" * 40 + "\n")
        f.write(f"Total samples: {len(y_true)}\n")
        f.write(f"Accuracy: {accuracy:.4f}\n\n")
        f.write(report)

    # Save machine-readable metrics
    summary_json_path = os.path.join(output_dir, "metrics_summary.json")
    payload = {
        "total_samples": len(y_true),
        "accuracy": round(float(accuracy), 6),
        "classes": {
            class_names[i]: {
                "precision": round(float(precision[i]), 6),
                "recall": round(float(recall[i]), 6),
                "f1_score": round(float(f1[i]), 6),
                "support": int(support[i]),
            }
            for i in range(len(class_names))
        },
    }
    with open(summary_json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    # PRF1 bar chart
    idx = list(range(len(class_names)))
    width = 0.25
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar([i - width for i in idx], precision, width, label="Precision")
    ax.bar(idx, recall, width, label="Recall")
    ax.bar([i + width for i in idx], f1, width, label="F1-score")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Score")
    ax.set_xticks(idx)
    ax.set_xticklabels(class_names, rotation=12)
    ax.set_title("Precision / Recall / F1 by Class (Telegram Evaluation)")
    ax.legend()
    fig.tight_layout()
    prf1_chart_path = os.path.join(output_dir, "prf1_bar.png")
    fig.savefig(prf1_chart_path, dpi=220)
    plt.close(fig)

    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=label_order)
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_title("Confusion Matrix (Telegram Evaluation)")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_xticks(idx)
    ax.set_yticks(idx)
    ax.set_xticklabels(class_names, rotation=10)
    ax.set_yticklabels(class_names)

    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center", color="black")

    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    confusion_matrix_path = os.path.join(output_dir, "confusion_matrix.png")
    fig.savefig(confusion_matrix_path, dpi=220)
    plt.close(fig)

    # Console summary for quick copy/paste
    print("Evaluation completed.")
    print(f"Total samples: {len(y_true)}")
    print(f"Accuracy: {accuracy:.4f}")
    print("")
    print(report)
    print(f"Saved report: {report_txt_path}")
    print(f"Saved metrics JSON: {summary_json_path}")
    print(f"Saved graph: {prf1_chart_path}")
    print(f"Saved graph: {confusion_matrix_path}")


def main() -> None:
    args = parse_args()
    classifier = ContentClassifier()
    if not classifier.is_loaded or classifier.model is None:
        raise RuntimeError(
            "Trained model not found. Run: python ml_models/train_content_classifier.py"
        )

    data = load_labeled_csv(args.csv_path, args.text_column, args.label_column)
    y_true, y_pred = evaluate_model(classifier, data)
    generate_graphs_and_reports(y_true, y_pred, args.output_dir)


if __name__ == "__main__":
    main()
