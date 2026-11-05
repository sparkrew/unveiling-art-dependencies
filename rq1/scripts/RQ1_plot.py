import matplotlib.pyplot as plt
import numpy as np
from decimal import Decimal, ROUND_DOWN

# Configuration
TOTAL_PROJECTS = 8780
ADD_TOTAL_BAR = True
TOTAL_WITH_AT_LEAST_ONE_DEPENDENCY = 8074

# Data
categories = [
    "Int",     # Interactions
    "DA",      # Digital Assets
    "API-E",   # API Endpoints
    "NP",      # Network Protocols
    "AI-ML",   # AI and ML Models
    "DS-P",    # Data Sources and Persistence
    "IAR",     # Internet Access Requirement
    "3PL"      # Third-Party Libraries
]
project_counts = [6201, 4051, 322, 2269, 18, 331, 2176, 6555]

def percentage(value):
    raw_percentage = Decimal(value) / Decimal(TOTAL_PROJECTS) * Decimal("100")
    truncated_percentage = raw_percentage.quantize(Decimal("0.0"), rounding=ROUND_DOWN)
    if truncated_percentage == Decimal("91.9"):
        return "92"
    if truncated_percentage == truncated_percentage.to_integral_value():
        return f"{int(truncated_percentage)}"
    return f"{truncated_percentage:.1f}"

plot_data = sorted(zip(categories, project_counts), key=lambda x: x[1], reverse=True)
categories_sorted = [item[0] for item in plot_data]
counts_sorted = [item[1] for item in plot_data]

if ADD_TOTAL_BAR:
    categories_sorted.append("Total")
    counts_sorted.append(TOTAL_WITH_AT_LEAST_ONE_DEPENDENCY)

percentages = [percentage(value) for value in counts_sorted]
# plot
fig, ax = plt.subplots(figsize=(9, 3.4))
colors = ["#020122" if category == "Total" else "#3EC300" for category in categories_sorted]

# Custom y positions to reduce spacing
y_positions = np.arange(len(categories_sorted)) * 0.50
bars = ax.barh(y_positions, counts_sorted, height=0.30, color=colors, edgecolor=colors)
ax.set_yticks(y_positions)
ax.set_yticklabels(categories_sorted)

# Largest category at the top
ax.invert_yaxis()

# ax.set_xlabel("Number of p5-projects", fontsize=16)
ax.tick_params(axis="x", labelsize=16)
ax.tick_params(axis="y", labelsize=16)

# Reduce vertical empty space
ax.margins(y=0.0105)
ax.grid(axis="x", linestyle="--", alpha=0.4)
ax.set_axisbelow(True)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

max_value = max(counts_sorted)
for bar, value, percentage_value in zip(bars, counts_sorted, percentages):
    ax.text(
        bar.get_width() + max_value * 0.008,
        bar.get_y() + bar.get_height() / 2,
        f"{value:,} ({percentage_value}%)",
        va="center",
        fontsize=16
    )

# Less empty horizontal space
ax.set_xlim(0, max_value * 1.17)
# save
plt.tight_layout(pad=0.4)
plt.savefig("projects_per_category_RQ1.png", dpi=300, bbox_inches="tight", pad_inches=0.03)
plt.show()