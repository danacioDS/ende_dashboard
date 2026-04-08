
---

# Ende Dashboard

## Overview

**Ende Dashboard** is a Python-based **ETL pipeline and visualization tool** for electricity market data from the **CNDC (Comité Nacional de Despacho de Carga)**.

It features a **modular, reproducible pipeline** for:

* **Ingestion** — Download raw CNDC datasets
* **Conversion** — Normalize Excel, ZIP, and CSV files
* **Extraction** — Parse structured data
* **Processing** — Transform data for analytics
* **Visualization** — Explore insights through a **Streamlit dashboard**

This architecture supports **automated workflows, reproducibility, and CI/CD integration**.

---

## Key Features

* Automated CNDC data ingestion
* Modular ETL pipeline for distribution and generation workflows
* Interactive **Streamlit dashboard** with Plotly/Altair visualizations
* Docker-ready environment
* Reproducible and deterministic data processing

---

## Project Structure

```
ende_dashboard/
│
├── dis_01_import_cndc.py
├── dis_02_convert.py
├── dis_03_extract_*.py
│
├── gen_01_import_cndc.py
├── gen_02_convert.py
├── gen_03_extract_*.py
│
├── downloads_*/
├── data_*/
├── preprocess/
│
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## Requirements

**Python 3.12+** and the following dependencies:

* pandas, numpy, requests, openpyxl, pyarrow
* streamlit, plotly, matplotlib, altair

Install with:

```bash
pip install -r requirements.txt
```

---

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Usage

### Run Pipelines

**Distribution Pipeline:**

```bash
python dis_01_import_cndc.py
```

**Generation Pipeline:**

```bash
python gen_01_import_cndc.py
```

### Launch Dashboard

```bash
streamlit run app.py
```

Access the dashboard at:

```
http://localhost:8501
```

---

## Tests

```bash
pytest -v
```

---

## Docker

**Build Container:**

```bash
docker build -t ende_dashboard .
```

**Run Dashboard:**

```bash
docker run --rm -p 8501:8501 ende_dashboard
```

**Optional: Run Pipeline Scripts in Container:**

```bash
docker run -it ende_dashboard bash
python dis_01_import_cndc.py
```

---

## Data Pipeline Architecture

Pipeline stages:

1. Import CNDC data
2. Convert raw files
3. Extract structured datasets
4. Transform and aggregate
5. Generate analytics
6. Visualize via Streamlit

**Benefits:** deterministic processing, reproducible results, modular extensibility.

---

## Output Directories

| Directory   | Description                  |
| ----------- | ---------------------------- |
| downloads_* | Raw downloaded files         |
| data_*      | Processed datasets           |
| preprocess  | Intermediate transformations |

---

## Development

Create tests:

```bash
mkdir tests
pytest -v
```

---

## Environment Reproducibility

Docker ensures:

* Consistent Python environment
* Reproducible pipeline execution
* CI/CD compatibility
* Portable dashboard deployment

---

## Contributing

Contributions welcome in areas like:

* Performance optimization
* Pipeline reliability
* Data validation
* Documentation improvements

---

## Notes

* Requires internet for CNDC downloads
* Handles large datasets locally
* Designed for batch ETL processing

---

✔ Clean, professional, Docker-aligned, ETL-ready, dashboard-ready, and PR Writer-friendly

---

If you want, I can also **add a small visual diagram of the pipeline** to make this README even more professional and easy to understand. It’ll be Streamlit + ETL flow-ready. Do you want me to do that?
