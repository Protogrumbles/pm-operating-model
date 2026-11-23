#!/usr/bin/env python3
"""Score project intake candidates and rank them for funding decisions.

Usage:
    python3 scorer.py [input.json] [--md out.md]

Input JSON:
    {
      "portfolio": "Portfolio name",
      "weights": {"strategic_fit": 0.35, "roi_estimate": 0.30,
                  "risk": 0.20, "effort": 0.15},
      "thresholds": {"fund": 3.5, "defer": 2.5},
      "projects": [
        {"name": "Unified asset pipeline", "strategic_fit": 5,
         "roi_estimate": 5, "risk": 2, "effort": 3}
      ]
    }

Scoring formula (all inputs on a 1-5 scale; weights must sum to 1):
    score = w_fit * fit + w_roi * roi
          + w_risk * (6 - risk) + w_effort * (6 - effort)

Risk and effort enter inverted (6 - value), so a riskier or heavier
project scores lower. The score stays on a 1-5 scale.

Recommendations (thresholds are inputs; defaults shown above):
    score >= fund  -> Fund
    score >= defer -> Defer
    otherwise      -> Reject

Rules enforced (exit code 2 with a clear error):
  - every score must be an integer 1-5; anything outside 1-5 is rejected
  - weights must be present, non-negative, and sum to 1 (within 0.001)
  - thresholds must satisfy fund > defer

With no --md flag, Markdown goes to stdout.
"""

import argparse
import json
import sys

DEFAULT_WEIGHTS = {
    "strategic_fit": 0.35,
    "roi_estimate": 0.30,
    "risk": 0.20,
    "effort": 0.15,
}
DEFAULT_THRESHOLDS = {"fund": 3.5, "defer": 2.5}
FIELDS = ("strategic_fit", "roi_estimate", "risk", "effort")


def load_input(path):
    if path:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return json.load(sys.stdin)


def validate(data):
    """Return a list of error strings; empty means the input is clean."""
    errors = []
    weights = data.get("weights", DEFAULT_WEIGHTS)
    for key in FIELDS:
        if key not in weights:
            errors.append(f"weights: missing weight for '{key}'.")
            continue
        w = weights[key]
        if not isinstance(w, (int, float)) or isinstance(w, bool) or w < 0:
            errors.append(f"weights: '{key}' must be a non-negative number, "
                          f"got {w!r}.")
    if not errors:
        total = sum(weights[k] for k in FIELDS)
        if abs(total - 1.0) > 0.001:
            errors.append(f"weights: must sum to 1, got {total:.3f}.")

    thresholds = data.get("thresholds", DEFAULT_THRESHOLDS)
    fund = thresholds.get("fund", DEFAULT_THRESHOLDS["fund"])
    defer = thresholds.get("defer", DEFAULT_THRESHOLDS["defer"])
    if not (isinstance(fund, (int, float)) and isinstance(defer, (int, float))):
        errors.append("thresholds: 'fund' and 'defer' must be numbers.")
    elif not fund > defer:
        errors.append(f"thresholds: 'fund' ({fund}) must be greater than "
                      f"'defer' ({defer}).")

    projects = data.get("projects", [])
    if not projects:
        errors.append("projects: at least one candidate project is required.")
    for p in projects:
        name = p.get("name", "?")
        for field in FIELDS:
            v = p.get(field)
            if v is None:
                errors.append(f"{name}: missing '{field}'.")
            elif isinstance(v, bool) or not isinstance(v, (int, float)) \
                    or int(v) != v or not 1 <= v <= 5:
                errors.append(
                    f"{name}: '{field}' must be a whole number from 1 to 5, "
                    f"got {v!r}."
                )
    return errors


def score_project(p, weights):
    return (
        weights["strategic_fit"] * p["strategic_fit"]
        + weights["roi_estimate"] * p["roi_estimate"]
        + weights["risk"] * (6 - p["risk"])
        + weights["effort"] * (6 - p["effort"])
    )


def recommend(score, thresholds):
    if score >= thresholds["fund"]:
        return "Fund"
    if score >= thresholds["defer"]:
        return "Defer"
    return "Reject"


def to_markdown(data, ranked, weights, thresholds):
    lines = [f"# Intake Scores — {data.get('portfolio', 'Untitled Portfolio')}", ""]
    lines.append("## Scoring formula")
    lines.append("")
    lines.append("All inputs are scored 1–5. Fit and ROI count positively; "
                 "risk and effort count negatively by entering inverted "
                 "(6 − value), so a riskier or heavier project scores lower:")
    lines.append("")
    lines.append("```")
    lines.append("score = w_fit × fit + w_roi × roi")
    lines.append("      + w_risk × (6 − risk) + w_effort × (6 − effort)")
    lines.append("```")
    lines.append("")
    lines.append("Weights: " + ", ".join(
        f"{k} {weights[k]:.2f}" for k in FIELDS) + f" (sum 1.00)")
    lines.append("")
    lines.append(f"Thresholds: Fund ≥ {thresholds['fund']:.1f} · "
                 f"Defer ≥ {thresholds['defer']:.1f} · "
                 f"below {thresholds['defer']:.1f} Reject")
    lines.append("")
    lines.append("| Rank | Project | Fit | ROI | Risk | Effort | Score | Recommendation |")
    lines.append("| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |")
    for i, (p, score, rec) in enumerate(ranked, 1):
        lines.append("| " + " | ".join([
            str(i), p["name"],
            str(p["strategic_fit"]), str(p["roi_estimate"]),
            str(p["risk"]), str(p["effort"]),
            f"{score:.2f}", f"**{rec}**",
        ]) + " |")
    lines.append("")
    counts = {"Fund": 0, "Defer": 0, "Reject": 0}
    for _, _, rec in ranked:
        counts[rec] += 1
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Candidates scored: {len(ranked)}")
    lines.append(f"- Fund: {counts['Fund']} · Defer: {counts['Defer']} · "
                 f"Reject: {counts['Reject']}")
    lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Score project intake candidates.")
    ap.add_argument("input", nargs="?", help="JSON input file (default: stdin)")
    ap.add_argument("--md", help="Write Markdown output to this file")
    args = ap.parse_args()

    try:
        data = load_input(args.input)
    except (OSError, json.JSONDecodeError) as e:
        print(f"error: could not read input: {e}", file=sys.stderr)
        return 2

    errors = validate(data)
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 2

    weights = data.get("weights", DEFAULT_WEIGHTS)
    thresholds = data.get("thresholds", DEFAULT_THRESHOLDS)
    ranked = sorted(
        ((p, score_project(p, weights),
          recommend(score_project(p, weights), thresholds))
         for p in data["projects"]),
        key=lambda t: t[1], reverse=True,
    )
    md = to_markdown(data, ranked, weights, thresholds)
    if args.md:
        with open(args.md, "w", encoding="utf-8") as f:
            f.write(md)
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
