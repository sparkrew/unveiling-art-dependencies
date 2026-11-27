# RQ1

## `/data/`

The `data` folder includes:

The following list of files contain the results from the empirical anaylis for each dependency category separated in an individual file:

- `output_ai_ml.json`
- `output_data_sources_and_persistence_ast`
- `output_digital_assets_ast.json`
- `output_interactions_ast.json`
- `output_internet_access_requirement.json`
- `output_library_usage_statistics.json`
- `output_network_protocols_ast.json`
- `output_web_endpoints.json`

## `/scripts/`

The `scripts` folder includes:

- `plots_for_table_1_violin_and_bar.py`: Creates the 3 figures in Table 1.
- `RQ1_plot.py`: Code for Figure 6.
- `bar-plot-fig-7.py`: Code for Figure 7.

## Python dependencies

The Python scripts require Python 3 and the packages listed in `requirements.txt`.

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment on Linux/macOS:

```bash
source .venv/bin/activate
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install the required Python packages:

```bash
python -m pip install -r requirements.txt
```
