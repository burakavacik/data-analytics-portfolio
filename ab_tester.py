#!/usr/bin/env python3
"""
ab_tester.py — Production-ready A/B test analyzer in a single file.

Features
- Cleans data, optional winsorization of the metric
- Welch's t-test (robust to unequal variances)
- Mann–Whitney U (non-parametric) as a cross-check
- Bootstrap confidence interval for lift
- CLI usage and Markdown report output

Usage:
    python ab_tester.py data.csv --group group --metric revenue --alpha 0.05 --winsor 0.01 --bootstrap 5000
"""
from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass
from typing import Dict, Tuple, Optional

import numpy as np
import pandas as pd
from scipy import stats as st


@dataclass
class ABResult:
    group_a_mean: float
    group_b_mean: float
    group_a_n: int
    group_b_n: int
    lift: float  # (B - A) / A
    welch_t: float
    welch_p: float
    mw_u: float
    mw_p: float
    ci_low: float
    ci_high: float
    alpha: float
    winsor: float
    metric: str
    group_col: str
    value_col: str


def winsorize_series(s: pd.Series, p: float) -> pd.Series:
    """Winsorize a numeric series by clipping tails at p and 1-p quantiles.
    If p == 0, returns s unchanged.
    """
    if p <= 0:
        return s
    lower = s.quantile(p)
    upper = s.quantile(1 - p)
    return s.clip(lower, upper)


def check_inputs(df: pd.DataFrame, group_col: str, value_col: str) -> Tuple[pd.Series, pd.Series]:
    if group_col not in df.columns or value_col not in df.columns:
        missing = {group_col, value_col} - set(df.columns)
        raise ValueError(f"Missing required columns: {missing}")
    df = df[[group_col, value_col]].dropna()
    if df.empty:
        raise ValueError("No data after dropping NA.")
    # Ensure numeric
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
    df = df.dropna(subset=[value_col])
    if df[group_col].nunique() != 2:
        raise ValueError(f"Expected exactly 2 groups in '{group_col}', found {df[group_col].nunique()}.")
    # Sort groups lexicographically and map to A/B for consistency
    groups = sorted(df[group_col].unique())
    a_label, b_label = groups[0], groups[1]
    a = df.loc[df[group_col] == a_label, value_col]
    b = df.loc[df[group_col] == b_label, value_col]
    return a.reset_index(drop=True), b.reset_index(drop=True)


def welch_t_test(a: pd.Series, b: pd.Series) -> Tuple[float, float]:
    t, p = st.ttest_ind(a, b, equal_var=False)
    return float(t), float(p)


def mann_whitney(a: pd.Series, b: pd.Series) -> Tuple[float, float]:
    u, p = st.mannwhitneyu(a, b, alternative="two-sided")
    return float(u), float(p)


def bootstrap_lift_ci(a: pd.Series, b: pd.Series, n_boot: int = 5000, alpha: float = 0.05, seed: Optional[int] = 42) -> Tuple[float, float]:
    rng = np.random.default_rng(seed)
    a_vals = a.to_numpy()
    b_vals = b.to_numpy()
    lifts = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        a_s = rng.choice(a_vals, size=a_vals.size, replace=True)
        b_s = rng.choice(b_vals, size=b_vals.size, replace=True)
        a_mean = a_s.mean()
        b_mean = b_s.mean()
        if a_mean == 0:
            lifts[i] = np.nan
        else:
            lifts[i] = (b_mean - a_mean) / a_mean
    lifts = lifts[~np.isnan(lifts)]
    low = np.quantile(lifts, alpha / 2)
    high = np.quantile(lifts, 1 - alpha / 2)
    return float(low), float(high)


def analyze_ab(
    df: pd.DataFrame,
    group_col: str,
    value_col: str,
    winsor: float = 0.0,
    alpha: float = 0.05,
    n_boot: int = 5000,
) -> ABResult:
    a, b = check_inputs(df, group_col, value_col)
    if winsor > 0:
        a = winsorize_series(a, winsor)
        b = winsorize_series(b, winsor)

    ga = float(a.mean())
    gb = float(b.mean())
    lift = (gb - ga) / ga if ga != 0 else math.nan

    t, tp = welch_t_test(a, b)
    u, up = mann_whitney(a, b)

    ci_low, ci_high = bootstrap_lift_ci(a, b, n_boot=n_boot, alpha=alpha)

    return ABResult(
        group_a_mean=ga,
        group_b_mean=gb,
        group_a_n=int(a.size),
        group_b_n=int(b.size),
        lift=lift,
        welch_t=t,
        welch_p=tp,
        mw_u=u,
        mw_p=up,
        ci_low=ci_low,
        ci_high=ci_high,
        alpha=alpha,
        winsor=winsor,
        metric=value_col,
        group_col=group_col,
        value_col=value_col,
    )


def format_report(res: ABResult) -> str:
    sig = "SIGNIFICANT ✅" if res.welch_p < res.alpha else "NOT SIGNIFICANT ❌"
    lift_pct = res.lift * 100
    ci_low_pct = res.ci_low * 100
    ci_high_pct = res.ci_high * 100
    return f"""# A/B Test Summary

**Metric:** `{res.metric}`  
**Groups:** `{res.group_col}` (A vs B)  
**Alpha:** {res.alpha:.2f} | **Winsor:** {res.winsor:.3f}

|            |   A (control) |   B (variant) |
|------------|----------------:|--------------:|
| n          | {res.group_a_n:>14d} | {res.group_b_n:>12d} |
| mean       | {res.group_a_mean:>14.4f} | {res.group_b_mean:>12.4f} |
| lift (B/A) |        —       | {lift_pct:>11.2f}% |

**Welch's t-test:** t = {res.welch_t:.3f}, p = {res.welch_p:.4f} → **{sig}**  
**Mann–Whitney U:** U = {res.mw_u:.0f}, p = {res.mw_p:.4f}  
**Bootstrap {int((1-res.alpha)*100)}% CI for lift:** [{ci_low_pct:.2f}%, {ci_high_pct:.2f}%]

> Interpretation: If the CI excludes 0% and p < α, the variant shows a statistically significant effect.
"""


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Single-file A/B Test Analyzer")
    p.add_argument("csv", help="Path to CSV with at least two columns: group and metric.")
    p.add_argument("--group", required=True, help="Name of the group column (must have 2 unique values).")
    p.add_argument("--metric", required=True, help="Name of the numeric metric column to test.")
    p.add_argument("--alpha", type=float, default=0.05, help="Significance level (default: 0.05).")
    p.add_argument("--winsor", type=float, default=0.0, help="Two-sided winsorization proportion (e.g., 0.01).")
    p.add_argument("--bootstrap", type=int, default=3000, help="Number of bootstrap resamples (default: 3000).")
    p.add_argument("--out", default="ab_summary.md", help="Where to write the Markdown report (default: ab_summary.md).")
    return p.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    df = pd.read_csv(args.csv)
    res = analyze_ab(df, args.group, args.metric, winsor=args.winsor, alpha=args.alpha, n_boot=args.bootstrap)
    md = format_report(res)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(md)
    print(md)
    print(f"\nSaved Markdown report → {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
