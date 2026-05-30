# Repo Analysis: Ende Dashboard

## Overview

**Ende Dashboard** is a Python-based ETL pipeline and interactive Streamlit dashboard for visualizing Bolivian electricity market data from the **CNDC** (Comite Nacional de Despacho de Carga). Author: Daniel Canedo.

## Tech Stack

- **Language:** Python 3.12+
- **Core:** pandas, numpy, openpyxl, pyexcel, requests
- **Dashboard:** Streamlit, Plotly, Altair
- **Testing:** pytest
- **Infrastructure:** Docker (python:3.11-slim)
- **Data Storage:** Flat Excel files (no database)

## Project Structure

```
ende_dashboard/
├── bienvenidos.py              # Main Streamlit app (dashboard launcher)
├── dis_*/gen_*                 # ETL pipeline scripts (6 stages)
├── pages/                      # 14 Streamlit dashboard pages
├── tests/                      # 3 test files (15 tests total)
├── downloads_distribucion/     # 183 raw CNDC files (distribution)
├── downloads_generacion/       # 161 raw CNDC files (generation)
├── data_distribuidor/          # 5 final processed datasets
├── data_generacion/            # 7 final processed datasets
├── preprocess/                 # 20 intermediate analytical files
├── Dockerfile
├── requirements.txt
├── setup.py
└── .gitignore
```

## Architecture / Data Flow

```
CNDC (cndc.bo)  -->  downloads/  -->  convert .xls->.xlsx  -->  extract columns
    -->  Jupyter notebooks (merge + reshape)  -->  data_distribuidor|generacion/
    -->  Streamlit Dashboard (bienvenidos.py + pages/)
```

Two parallel pipelines feed the dashboard:
- **Distribution** (`dis_*`): data from distribution companies
- **Generation** (`gen_*`): data from power generation companies

Both follow the same 6-stage ETL: Import → Convert → Extract → Process (notebooks) → Store → Visualize.

## Dashboard Pages (14 total)

| Category | Distribution | Generation |
|----------|-------------|------------|
| Energy | energia_por_distribuidor | energia_por_generador, energia_por_tecnologia |
| Power | potencia_distribuidoras | potencia_por_generador, potencia_por_tecnologia |
| Energy Prices | precio_energia_distribucion | precio_energia_generacion |
| Power Prices | precio_potencia_distribucion | precio_potencia_generacion |
| Monomic Prices | precios_monomico_distribucion | precios_monomicos_generacion |
| Peaje (Tolls) | precios_peaje_distribucion | precios_peaje_generacion |

All pages follow an identical pattern: cached data loading, sidebar filters, tabs (detailed + averages), Plotly charts, summary metrics.

## Key Findings

1. **High code duplication** — All 14 dashboard pages share ~80% identical code (copy-pasted with minor variations: entity names, file paths, color schemes). Major refactoring opportunity.

2. **Broken navigation** — `bienvenidos.py` sidebar references scripts in `generacion/` and `distribucion/` directories that **do not exist**. The actual pages are in `pages/`. The app likely has a non-functional sidebar.

3. **Minimal test coverage** — 15 tests total across 3 files. `tests/tests_scripts.py` is parametrized to check existence of those same non-existent script paths, so it **will fail** if run.

4. **Incomplete processing layer** — Jupyter notebook outputs reference a `pre_data/` directory that is not in the repo. The notebooks appear to have been run manually and their outputs committed, but the pipeline is not fully automated end-to-end.

5. **File-based storage** — All data is in Excel files. No database. This works for the scale but means the preprocessing scripts must be re-run to refresh data.

6. **Docker-ready** — Fully containerized deployment via Dockerfile (port 8501, healthcheck configured).

## Recommendations

1. **Refactor dashboard pages** into a shared base class or utility functions to eliminate copy-paste.
2. **Fix sidebar navigation** in `bienvenidos.py` to point to actual `pages/` files, or remove the broken sidebar.
3. **Fix or remove** the failing test in `tests/tests_scripts.py`.
4. **Automate the notebook stage** (stage 4) as Python scripts instead of manual Jupyter execution for true end-to-end automation.
5. **Increase test coverage** — especially for the extraction and transformation logic.
