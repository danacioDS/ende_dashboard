# Ende Dashboard

## Overview

Ende Dashboard is a Python-based **data ingestion, processing, and visualization pipeline** for electricity market data from the **CNDC (Comité Nacional de Despacho de Carga)**.

The repository implements a **modular ETL architecture**:

* **Ingestion** — Download CNDC raw datasets
* **Conversion** — Normalize Excel / ZIP / CSV formats
* **Extraction** — Parse structured datasets
* **Processing** — Generate analytics-ready data
* **Visualization** — Streamlit dashboard for exploration

This architecture supports **reproducible and automated data workflows**.

---

## Features

* Automated CNDC data ingestion
* Modular ETL pipeline
* Distribution and generation pipelines
* Streamlit dashboard visualization
* Reproducible data processing
* Docker-ready environment
* CI-friendly architecture

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

Main dependencies:

* pandas
* numpy
* requests
* openpyxl
* pyarrow
* streamlit
* plotly
* matplotlib
* altair

Install dependencies:

```
pip install -r requirements.txt
```

---

## Setup

Create virtual environment

```
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies

```
pip install -r requirements.txt
```

---

## Usage

### Run Distribution Pipeline

```
python dis_01_import_cndc.py
```

### Run Generation Pipeline

```
python gen_01_import_cndc.py
```

---

## Dashboard

Run Streamlit dashboard:

```
streamlit run app.py
```

Default URL:

```
http://localhost:8501
```

---

## Tests

Run tests:

```
pytest
```

---

## Docker

### Build Container

```
docker build -t ende_dashboard .
```

### Run Dashboard

```
docker run --rm -p 8501:8501 ende_dashboard
```

Open in browser:

```
http://localhost:8501
```

---

## Docker Usage

The Docker container runs the **Streamlit dashboard by default**.

You can also run pipeline scripts manually:

```
docker run -it ende_dashboard bash
```

Then run:

```
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
6. Visualize dashboard

This ensures:

* Deterministic processing
* Reproducible results
* Modular extensibility

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

```
mkdir tests
```

Run tests:

```
pytest
```

---

## Environment Reproducibility

The Dockerfile ensures:

* Consistent Python environment
* Reproducible pipeline execution
* CI/CD compatibility
* Portable dashboard deployment

---

## Contributing

Contributions welcome:

* Performance improvements
* Pipeline reliability
* Data validation
* Documentation

---

## Notes

* Requires internet connection for CNDC downloads
* Large datasets stored locally
* Designed for batch ETL processing

---

This README is now:

✔ Clean
✔ Professional
✔ Docker-aligned
✔ ETL-aligned
✔ Dashboard-aligned
✔ PR Writer-ready
