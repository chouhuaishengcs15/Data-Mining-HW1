"""English version of P2's Figure 1 (QualityArea vs log1p(SalePrice)), training data only."""
import csv
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr

src, out = sys.argv[1], sys.argv[2]
rows = list(csv.DictReader(open(src, encoding="utf-8-sig")))
qual = np.array([float(r["整體品質1到10分"]) for r in rows])
area = np.array([float(r["地上居住面積平方英尺"]) for r in rows])
y = np.array([float(r["log總價"]) for r in rows])
x = qual * area

r, rho = pearsonr(x, y)[0], spearmanr(x, y)[0]
print(f"n={len(x)}  pearson={r:.3f}  spearman={rho:.3f}")

plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
                     "font.size": 9, "axes.linewidth": 0.6})
fig, ax = plt.subplots(figsize=(3.3, 1.75))
ax.scatter(x, y, s=8, color="#2E5C8A", alpha=0.45, linewidths=0, rasterized=True)
ax.set_xlabel("QualityArea (rating point × sq ft)")
ax.set_ylabel("log(1 + SalePrice in USD)")
ax.text(0.97, 0.05, f"Pearson r = {r:.3f}\nSpearman ρ = {rho:.3f}\nn = {len(x):,}",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=8, color="#333333")
ax.grid(True, color="#E3E3E3", linewidth=0.5)
ax.set_axisbelow(True)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
ax.tick_params(width=0.6, length=3, colors="#333333")
ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
fig.tight_layout(pad=0.3)
fig.savefig(out, dpi=300)
