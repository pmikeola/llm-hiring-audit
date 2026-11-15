"""Audit an LLM resume screener's scores against recruiter decisions.

Usage:
    python audit.py results.csv

Expects a CSV with columns:
    recruiter_decision (Hire/Reject), overall_score (0-100),
    original_ai_score (0-100), confidence (0-1), flags (pipe-separated)

Standard library only.
"""
import csv
import statistics as st
import sys
from collections import Counter


def load(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def group_stats(rows, col):
    out = {}
    for label in ("Hire", "Reject"):
        vals = [float(r[col]) for r in rows if r["recruiter_decision"] == label]
        if vals:
            out[label] = (len(vals), st.mean(vals), min(vals), max(vals))
    return out


def best_threshold(rows, col):
    """Best accuracy achievable by a single cutoff on the score."""
    best = (0, 0)
    for t in range(101):
        correct = sum(
            (float(r[col]) >= t) == (r["recruiter_decision"] == "Hire") for r in rows
        )
        best = max(best, (correct, t))
    return best


def main(path):
    rows = load(path)
    n = len(rows)
    hires = sum(r["recruiter_decision"] == "Hire" for r in rows)

    print(f"Records: {n}  (Hire base rate: {hires / n:.0%})\n")
    print("| Score source | Hire mean | Reject mean | Gap | Best cutoff accuracy |")
    print("|---|---|---|---|---|")
    for col, name in (("overall_score", "LLM pipeline"), ("original_ai_score", "Original AI")):
        g = group_stats(rows, col)
        acc, t = best_threshold(rows, col)
        gap = g["Hire"][1] - g["Reject"][1] if "Reject" in g else float("nan")
        print(
            f"| {name} | {g['Hire'][1]:.1f} | {g.get('Reject', (0, float('nan')))[1]:.1f} "
            f"| {gap:.1f} | {acc}/{n} at >= {t} |"
        )
    print(f"\nNaive baseline (predict all Hire): {hires}/{n}")

    conf = [float(r["confidence"]) for r in rows]
    print(f"Mean model confidence: {st.mean(conf):.2f}")

    flags = Counter(f for r in rows for f in r["flags"].split("|") if f)
    print("\nFlags raised:")
    for flag, count in flags.most_common():
        print(f"  {flag}: {count}/{n}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
