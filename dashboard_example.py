#!/usr/bin/env python3
# dashboard_example.py
# Basit KPI + Bar Chart dashboard'u: data.csv -> dashboard.png

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

CSV_PATH = "data.csv"
OUT_PATH = "dashboard.png"

def main():
    # Veri oku
    df = pd.read_csv(CSV_PATH)
    if not {"group", "revenue"}.issubset(df.columns):
        raise ValueError("data.csv dosyasında 'group' ve 'revenue' sütunları olmalı.")

    # Temizlik
    df = df.dropna(subset=["group", "revenue"]).copy()
    df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")
    df = df.dropna(subset=["revenue"])

    # Basit metrikler
    total_users = len(df)
    total_rev = df["revenue"].sum()
    mean_by_group = df.groupby("group")["revenue"].mean().sort_index()
    n_by_group = df["group"].value_counts().sort_index()

    # A/B varsa lift hesapla (B/A - 1)
    lift_text = "—"
    if set(mean_by_group.index) >= set(list("AB")):
        a = mean_by_group.get("A", float("nan"))
        b = mean_by_group.get("B", float("nan"))
        if pd.notna(a) and a != 0 and pd.notna(b):
            lift = (b - a) / a * 100
            lift_text = f"{lift:,.2f}%"

    # Şekil
    plt.figure(figsize=(10, 6), dpi=150)
    plt.suptitle("Sample Analytics Dashboard", fontsize=16, fontweight="bold")

    # Sol: bar chart (ortalama revenue)
    ax1 = plt.subplot(1, 2, 1)
    mean_by_group.plot(kind="bar", ax=ax1)
    ax1.set_title("Average Revenue by Group")
    ax1.set_xlabel("Group")
    ax1.set_ylabel("Average Revenue")
    ax1.grid(axis="y", alpha=0.3)

    # Sağ: KPI metinleri
    ax2 = plt.subplot(1, 2, 2)
    ax2.axis("off")
    lines = [
        "Key Metrics",
        "-----------",
        f"Total Rows: {total_users}",
        f"Total Revenue: {total_rev:,.2f}",
        "",
        "Per-Group",
        "---------",
        *[f"{grp}: n={int(n_by_group.get(grp, 0))}, mean={mean_by_group.get(grp, float('nan')):,.2f}"
          for grp in mean_by_group.index],
    ]
    # Lift varsa ekle
    if lift_text != "—":
        lines += ["", f"Lift (B vs A): {lift_text}"]

    text = "\n".join(lines)
    ax2.text(0.0, 0.95, text, va="top", ha="left", fontsize=11, family="monospace")

    # Kaydet
    Path(OUT_PATH).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(OUT_PATH)
    print(f"Saved dashboard → {OUT_PATH}")

if __name__ == "__main__":
    main()
