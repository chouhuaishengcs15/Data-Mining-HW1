"""Forest plot of every numeric/ordinal predictor of the final Elastic Net (55 of 214 columns).

Input: model/results/tables/final_test/coefficients_ci_pvalue_vif.csv (P3).
The 159 one-hot columns (all VIF = inf) are summarized in the text instead.
Usage: python plot_coef_forest.py <coefficients csv> <output.pdf>
"""
import csv
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.transforms import blended_transform_factory

src, out = sys.argv[1], sys.argv[2]
rows = [r for r in csv.DictReader(open(src, encoding="utf-8-sig")) if r["VIF"] != "inf"]
assert len(rows) == 55, len(rows)
rows.sort(key=lambda r: float(r["beta_per_training_SD"]))  # largest at the top

plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
                     "font.size": 6.2, "axes.linewidth": 0.6, "pdf.fonttype": 42})
fig, ax = plt.subplots(figsize=(3.03, 4.95))
ink = "#222222"
for i, r in enumerate(rows):
    beta, lo, hi = (float(r[k]) for k in ("beta_per_training_SD", "CI95_low", "CI95_high"))
    excludes_zero = lo > 0 or hi < 0
    ax.plot([lo, hi], [i, i], color=ink, linewidth=0.8, solid_capstyle="butt")
    ax.plot(beta, i, "o", markersize=3, markeredgewidth=0.7, color=ink,
            markerfacecolor=ink if excludes_zero else "white")

ax.axvline(0, color="#999999", linewidth=0.6, zorder=0)
ax.set_yticks(range(len(rows)))
ax.set_yticklabels([r["feature"] for r in rows])
ax.set_ylim(-0.7, len(rows) - 0.3)
ax.set_xlim(-0.02, 0.104)
ax.set_xlabel("β: change in log(1 + price) per training SD")
ax.grid(True, axis="x", color="#E3E3E3", linewidth=0.5)
ax.set_axisbelow(True)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
ax.tick_params(width=0.6, length=2, colors="#333333", pad=1.5)

# p-value and VIF columns to the right of the plot area.
tr = blended_transform_factory(ax.transAxes, ax.transData)
top = len(rows) - 0.3
ax.text(1.13, top, "p", transform=tr, ha="right", va="bottom", style="italic")
ax.text(1.29, top, "VIF", transform=tr, ha="right", va="bottom")
for i, r in enumerate(rows):
    p, vif = float(r["bootstrap_centered_p_approx"]), float(r["VIF"])
    p_txt = "≤.001" if p <= 0.0011 else ("1" if p >= 0.9995 else f"{p:.3f}".lstrip("0"))
    ax.text(1.13, i, p_txt, transform=tr, ha="right", va="center")
    ax.text(1.29, i, f"{vif:.1f}", transform=tr, ha="right", va="center",
            fontweight="bold" if vif >= 10 else "normal")

fig.subplots_adjust(left=0.27, right=0.78, top=0.985, bottom=0.07)
fig.savefig(out)
print("saved", out)
