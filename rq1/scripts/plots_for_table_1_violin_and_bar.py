import json
from pathlib import Path
from collections import Counter
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# Configuration
METADATA_FILE = Path("../../p5_dependencies.json")
DATASET_DIR = Path("FINAL_DATASET")
PLOTS_DIR = Path("plots_dataset_distribution")
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

# Load data
with open(METADATA_FILE, "r", encoding="utf-8") as f:
    projects = json.load(f)

print(f"Projects loaded: {len(projects):,}")

def get_project_creation_year(project):
    """Returns the repository creation year."""
    repository_data = project.get("repository_github_data") or {}
    date_string = repository_data.get("repository_created_at")
    if not date_string:
        return None
    try:
        return datetime.fromisoformat(date_string.replace("Z", "+00:00")).year
    except (ValueError, TypeError):
        return None

def get_project_folder(project):
    """Converts project_path into the folder convention used in FINAL_DATASET."""
    project_path = project.get("project_path")
    if not project_path:
        return None
    parts = project_path.split("/", 2)
    if len(parts) >= 2:
        base_folder = parts[0] + "__" + parts[1]
        if len(parts) == 3:
            return DATASET_DIR / base_folder / parts[2]
        return DATASET_DIR / base_folder
    return None

def get_directory_size(path):
    """Returns the total size of all files contained in a directory, in bytes."""
    if path is None or not path.exists():
        return None
    total_size = 0
    try:
        for file_path in path.rglob("*"):
            if file_path.is_file():
                try:
                    total_size += file_path.stat().st_size
                except OSError:
                    pass
    except OSError:
        return None
    return total_size

years = []
loc_values = []
project_sizes_bytes = []
missing_year = 0
missing_loc = 0
missing_project_size = 0

for project in projects:
    # Creation year
    year = get_project_creation_year(project)
    if year is not None:
        years.append(year)
    else:
        missing_year += 1

    # LOC
    loc = project.get("totalCodeLines")
    if isinstance(loc, (int, float)) and loc > 0:
        loc_values.append(loc)
    else:
        missing_loc += 1

    # Full project size
    project_folder = get_project_folder(project)
    project_size = get_directory_size(project_folder)
    if project_size is not None and project_size > 0:
        project_sizes_bytes.append(project_size)
    else:
        missing_project_size += 1

# Convert size to KB
project_sizes_kb = [value / 1000 for value in project_sizes_bytes]

# Summary
print()
print("Valid temporal values:", f"{len(years):,}")
print("Missing temporal values:", f"{missing_year:,}")
print()
print("Valid LOC values:", f"{len(loc_values):,}")
print("Missing LOC values:", f"{missing_loc:,}")
print()
print("Valid full-project sizes:", f"{len(project_sizes_kb):,}")
print("Missing full-project sizes:", f"{missing_project_size:,}")

# Statistics
def print_statistics(name, values):
    values = np.array(values, dtype=float)
    print()
    print(name)
    print(f"  N:      {len(values):,}")
    print(f"  Min:    {np.min(values):,.2f}")
    print(f"  Q1:     {np.percentile(values, 25):,.2f}")
    print(f"  Median: {np.median(values):,.2f}")
    print(f"  Mean:   {np.mean(values):,.2f}")
    print(f"  Q3:     {np.percentile(values, 75):,.2f}")
    print(f"  Max:    {np.max(values):,.2f}")

print_statistics("LOC", loc_values)
print_statistics("Full project size (KB)", project_sizes_kb)

# 1. Temporal distribution
year_counts = Counter(years)
min_year = min(year_counts)
max_year = max(year_counts)
all_years = list(range(min_year, max_year + 1))
year_values = [year_counts.get(year, 0) for year in all_years]

plt.figure(figsize=(8, 3))
plt.bar(all_years, year_values, color="#020122")
# plt.xlabel("Project creation year", fontsize=14)
# plt.ylabel("Number of p5-projects", fontsize=14)
plt.xticks(all_years, rotation=50, fontsize=20)
plt.yticks(fontsize=20)
plt.tight_layout()
plt.savefig(PLOTS_DIR / "temporal_distribution.pdf", bbox_inches="tight")
plt.savefig(PLOTS_DIR / "temporal_distribution.png", dpi=300, bbox_inches="tight")
plt.close()

# Horizontal violin plot
def create_violin_plot(values, xlabel, output_name, color):
    values = np.array(values, dtype=float)

    # Keep only valid positive values
    values = values[np.isfinite(values) & (values > 0)]

    # Log transformation
    log_values = np.log10(values)

    # Statistics
    q1 = np.percentile(values, 25)
    median = np.median(values)
    q3 = np.percentile(values, 75)
    log_q1 = np.log10(q1)
    log_median = np.log10(median)
    log_q3 = np.log10(q3)

    # Figure
    fig, ax = plt.subplots(figsize=(6, 2.2))

    # Violin
    violin = ax.violinplot(
        log_values,
        vert=False,
        showmeans=False,
        showmedians=False,
        showextrema=False,
        widths=0.75
    )

    for body in violin["bodies"]:
        body.set_facecolor(color)
        body.set_edgecolor(color)
        body.set_linewidth(1.5)
        body.set_alpha(0.45)

    # Inner box: Q1 --- Q3
    ax.plot(
        [log_q1, log_q3],
        [1, 1],
        color="black",
        linewidth=8,
        solid_capstyle="butt",
        zorder=3
    )

    # Median
    ax.scatter(
        log_median,
        1,
        color="white",
        edgecolor="black",
        s=45,
        linewidth=0.8,
        zorder=4
    )

    # Axis
    ax.set_yticks([])

    def log_tick_formatter(x, pos):
        value = 10 ** x
        if value >= 1_000_000:
            return f"{value / 1_000_000:g}M"
        if value >= 1_000:
            return f"{value / 1_000:g}k"
        if value >= 1:
            return f"{value:g}"
        return f"{value:.1f}"

    ax.xaxis.set_major_formatter(FuncFormatter(log_tick_formatter))
    ax.tick_params(axis="x", labelsize=16)
    # ax.set_xlabel(xlabel, fontsize=16)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    plt.tight_layout()
    plt.savefig(PLOTS_DIR / f"{output_name}.pdf", bbox_inches="tight")
    plt.savefig(PLOTS_DIR / f"{output_name}.png", dpi=300, bbox_inches="tight")
    plt.close()

# 2. LOC distribution
create_violin_plot(loc_values, "Lines of code", "loc_distribution", "#337CA0")

# 3. Full project size distribution
create_violin_plot(project_sizes_kb, "p5-project size (KB)", "project_size_distribution", "#3EC300")

print()
print(f"Plots saved in: {PLOTS_DIR}")