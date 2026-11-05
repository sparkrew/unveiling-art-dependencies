import json
from pathlib import Path
from decimal import Decimal, ROUND_DOWN
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

# configuration
TOTAL_PROJECTS = 8780
MODE = 1

# colors
COLOR_TOTAL = "#020122"
COLOR_LOCAL = "#3EC300"
COLOR_REMOTE = "#337CA0"
COLOR_CATEGORY_TOTAL = "#FF0000"

# input files
MISSING_DIR = Path("data/missing_dependencies")
LIBRARIES_FILE = MISSING_DIR / "library_availability_projects.json"
DIGITAL_ASSETS_FILE = MISSING_DIR / "digital_assets_problem_projects.json"
API_ENDPOINTS_FILE = MISSING_DIR / "projects_with_inaccessible_web_endpoints.json"
DATA_SOURCES_FILE = MISSING_DIR / "projects_with_missing_data_sources.json"

# category data
categories = ["3PL", "DA", "API-E", "DS-P"]

total_counts = {
    "3PL": 483,
    "DA": 692,
    "API-E": 195,
    "DS-P": 44
}

local_counts = {
    "3PL": 458,
    "DA": 640,
    "API-E": 0,
    "DS-P": 22
}

remote_counts = {
    "3PL": 27,
    "DA": 60,
    "API-E": 195,
    "DS-P": 23
}

TOTAL_AFFECTED = 1258

# helpers
def load_json(filename):
    with filename.open("r", encoding="utf-8") as f:
        return json.load(f)

def percentage(value):
    raw_percentage = Decimal(value) / Decimal(TOTAL_PROJECTS) * Decimal("100")
    truncated_percentage = raw_percentage.quantize(Decimal("0.00"), rounding=ROUND_DOWN)
    return f"{truncated_percentage:.1f}"

# calculate unique local and remote totals
def calculate_unique_local_remote_totals():
    # third-party libraries
    libraries = load_json(LIBRARIES_FILE)
    library_local = set(libraries.get("local_only", [])) | set(libraries.get("both", []))
    library_remote = set(libraries.get("remote_only", [])) | set(libraries.get("both", []))

    # digital assets
    digital_assets = load_json(DIGITAL_ASSETS_FILE)
    digital_local = set(digital_assets.get("local_only", [])) | set(digital_assets.get("both", []))
    digital_remote = set(digital_assets.get("remote_only", [])) | set(digital_assets.get("both", []))

    # data sources
    data_sources = load_json(DATA_SOURCES_FILE)
    data_local = set(data_sources.get("local_only", [])) | set(data_sources.get("both", []))
    data_remote = set(data_sources.get("remote_only", [])) | set(data_sources.get("both", []))

    # api endpoints
    api_endpoints = load_json(API_ENDPOINTS_FILE)
    api_remote = set(api_endpoints.get("projects_with_at_least_one_inaccessible_endpoint", []))

    # unions
    all_local = library_local | digital_local | data_local
    all_remote = library_remote | digital_remote | data_remote | api_remote

    return all_local, all_remote

# get unique totals
all_local_projects, all_remote_projects = calculate_unique_local_remote_totals()
TOTAL_LOCAL = len(all_local_projects)
TOTAL_REMOTE = len(all_remote_projects)

print(f"Unique affected projects: {TOTAL_AFFECTED:,}")
print(f"Unique projects with local problems: {TOTAL_LOCAL:,}")
print(f"Unique projects with remote problems: {TOTAL_REMOTE:,}")

# categories
categories_sorted = categories.copy()

# uncomment to sort by total
# categories_sorted = sorted(categories, key=lambda category: total_counts[category], reverse=True)

# create figure
fig, ax = plt.subplots(figsize=(9, 3.4))

# mode 0: local and remote per category + one final total bar
if MODE == 0:
    y_positions = np.arange(len(categories_sorted))
    bar_height = 0.32

    local_values = [local_counts[category] for category in categories_sorted]
    remote_values = [remote_counts[category] for category in categories_sorted]

    local_bars = ax.barh(
        y_positions - bar_height / 2,
        local_values,
        height=bar_height,
        color=COLOR_LOCAL,
        label="Local"
    )

    remote_bars = ax.barh(
        y_positions + bar_height / 2,
        remote_values,
        height=bar_height,
        color=COLOR_REMOTE,
        label="Remote"
    )

    total_position = len(categories_sorted) + 0.5

    total_bar = ax.barh(
        total_position,
        TOTAL_AFFECTED,
        height=0.45,
        color=COLOR_TOTAL,
        label="Total"
    )

    tick_positions = list(y_positions) + [total_position]
    tick_labels = categories_sorted + ["Total"]

    ax.set_yticks(tick_positions)
    ax.set_yticklabels(tick_labels, fontsize=16)

    max_value = max(TOTAL_AFFECTED, max(local_values), max(remote_values))

    for bars, values in [(local_bars, local_values), (remote_bars, remote_values)]:
        for bar, value in zip(bars, values):
            if value == 0:
                continue
            ax.text(
                bar.get_width() + max_value * 0.012,
                bar.get_y() + bar.get_height() / 2,
                f"{value:,} ({percentage(value)}%)",
                va="center",
                fontsize=16
            )

    for bar in total_bar:
        ax.text(
            bar.get_width() + max_value * 0.012,
            bar.get_y() + bar.get_height() / 2,
            f"{TOTAL_AFFECTED:,} ({percentage(TOTAL_AFFECTED)}%)",
            va="center",
            fontsize=16
        )

# mode 1: one total bar per category + total, local and remote at end
elif MODE == 1:
    labels = list(categories_sorted)
    values = [total_counts[category] for category in categories_sorted]
    colors = [COLOR_CATEGORY_TOTAL for _ in labels]

    labels.extend(["Total", "Local", "Remote"])
    values.extend([TOTAL_AFFECTED, TOTAL_LOCAL, TOTAL_REMOTE])
    colors.extend([COLOR_TOTAL, COLOR_LOCAL, COLOR_REMOTE])

    y_positions = np.arange(len(labels)) * 0.50

    bars = ax.barh(
        y_positions,
        values,
        color=colors,
        edgecolor=colors,
        height=0.30
    )

    ax.set_yticks(y_positions)
    ax.set_yticklabels(labels, fontsize=16)

    max_value = max(values)

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_width() + max_value * 0.008,
            bar.get_y() + bar.get_height() / 2,
            f"{value:,} ({percentage(value)}%)",
            va="center",
            fontsize=16
        )

# mode 2: local and remote per category + total, local and remote at end
elif MODE == 2:
    y_positions = np.arange(len(categories_sorted))
    bar_height = 0.32

    local_values = [local_counts[category] for category in categories_sorted]
    remote_values = [remote_counts[category] for category in categories_sorted]

    local_bars = ax.barh(
        y_positions - bar_height / 2,
        local_values,
        height=bar_height,
        color=COLOR_LOCAL,
        label="Local"
    )

    remote_bars = ax.barh(
        y_positions + bar_height / 2,
        remote_values,
        height=bar_height,
        color=COLOR_REMOTE,
        label="Remote"
    )

    base_position = len(categories_sorted) + 0.5
    final_labels = ["Total", "Local", "Remote"]
    final_values = [TOTAL_AFFECTED, TOTAL_LOCAL, TOTAL_REMOTE]
    final_colors = [COLOR_TOTAL, COLOR_LOCAL, COLOR_REMOTE]
    final_positions = [base_position, base_position + 1, base_position + 2]

    final_bars = ax.barh(
        final_positions,
        final_values,
        height=0.5,
        color=final_colors
    )

    ax.set_yticks(list(y_positions) + final_positions)
    ax.set_yticklabels(categories_sorted + final_labels, fontsize=16)

    max_value = max(
        TOTAL_AFFECTED,
        TOTAL_LOCAL,
        TOTAL_REMOTE,
        max(local_values),
        max(remote_values)
    )

    for bars, values in [(local_bars, local_values), (remote_bars, remote_values)]:
        for bar, value in zip(bars, values):
            if value == 0:
                continue
            ax.text(
                bar.get_width() + max_value * 0.012,
                bar.get_y() + bar.get_height() / 2,
                f"{value:,} ({percentage(value)}%)",
                va="center",
                fontsize=16
            )

    for bar, value in zip(final_bars, final_values):
        ax.text(
            bar.get_width() + max_value * 0.012,
            bar.get_y() + bar.get_height() / 2,
            f"{value:,} ({percentage(value)}%)",
            va="center",
            fontsize=16
        )

else:
    raise ValueError("MODE must be 0, 1, or 2.")

# axes
ax.invert_yaxis()
ax.set_xlabel("# p5 projects", fontsize=16)
ax.tick_params(axis="x", labelsize=16)

# grid
ax.grid(axis="x", linestyle="--", alpha=0.25)
ax.set_axisbelow(True)

# remove borders
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# legend
if MODE in {0, 2}:
    legend_elements = [
        Patch(facecolor=COLOR_LOCAL, edgecolor=COLOR_LOCAL, label="Local"),
        Patch(facecolor=COLOR_REMOTE, edgecolor=COLOR_REMOTE, label="Remote")
    ]
    ax.legend(handles=legend_elements, fontsize=16, frameon=False)

# x limit
current_xlim = ax.get_xlim()
ax.set_xlim(0, current_xlim[1] * 1.18)

# save
plt.tight_layout(pad=0.4)
plt.savefig(
    f"projects_with_missing_dependencies_RQ2_mode_{MODE}.png",
    dpi=300,
    bbox_inches="tight",
    pad_inches=0.03
)
plt.show()