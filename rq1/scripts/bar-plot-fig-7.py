import json
from pathlib import Path
from decimal import Decimal, ROUND_DOWN
import matplotlib.pyplot as plt

# Configuration
INPUT_FILE = Path("../data/projects_grouped_by_number_of_dependencies.json")
OUTPUT_FILE = Path("projects_per_number_of_dependency_categories_bar_plot.png")
TOTAL_PROJECTS = 8780

def percentage(value):
    raw_percentage = Decimal(value) / Decimal(TOTAL_PROJECTS) * Decimal("100")
    truncated_percentage = raw_percentage.quantize(Decimal("0.0"), rounding=ROUND_DOWN)
    if truncated_percentage == truncated_percentage.to_integral_value():
        return f"{int(truncated_percentage)}"
    return f"{truncated_percentage:.1f}"

# Load data
with INPUT_FILE.open("r", encoding="utf-8") as f:
    data = json.load(f)

distribution = data["projects_per_number_of_dependency_categories"]

x_values = list(range(0, 8))
counts = [distribution.get(str(number), 0) for number in x_values]
percentages = [percentage(count) for count in counts]

fig, ax = plt.subplots(figsize=(10, 4.0))
bars = ax.barh(x_values, counts, height=0.60, color="#FFFC31", edgecolor="#020122")

ax.set_xlabel("# p5 projects", fontsize=17)
ax.set_ylabel("# Dependency Categories", fontsize=17)
ax.set_yticks(x_values)
ax.tick_params(axis="both", labelsize=17)

ax.grid(axis="x", linestyle="--", alpha=0.25)
ax.set_axisbelow(True)

# removing borders
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

max_count = max(counts)

for bar, count, percentage_value in zip(bars, counts, percentages):
    if count == 0:
        continue
    ax.text(
        bar.get_width() + max_count * 0.012,
        bar.get_y() + bar.get_height() / 2,
        f"{count:,} ({percentage_value}%)",
        ha="left",
        va="center",
        fontsize=16
    )

ax.set_xlim(0, max_count * 1.20)
# Save
plt.tight_layout()
plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight")
plt.show()