# Recommended Upgrades & Bug Fixes

## Bugs Found

### 1. Broken sidebar navigation
**File:** `bienvenidos.py:107,283`
The sidebar references scripts via `./generacion/{script}` and `./distribucion/{script}` — these directories **don't exist**. The actual dashboard pages are in `pages/`.  
**Fix:** Remove the broken script-runner sidebar and replace it with proper navigation to `pages/` files, or remove it entirely if pages are accessed through Streamlit's native page navigation.

### 2. Failing test
**File:** `tests/tests_scripts.py:4-18`
Parametrized test checks existence of scripts in `generacion/` and `distribucion/` — those paths don't exist, so the test **always fails**.  
**Fix:** Update test paths to match actual file locations, or remove the test.

### 3. Wrong unit in sidebar metric
**File:** `pages/energia_por_generador.py:368`
Sidebar says `"Energía Total: {value} MWh"` but the entire page uses **kWh** as its unit.  
**Fix:** Change `MWh` to `kWh`.

### 4. Wrong y-axis label on system chart
**Files:** `pages/energia_por_distribuidor.py:233`, `pages/energia_por_generador.py:232`
The system bar chart y-axis says `"Potencia kW"` but the data is **energy** (MWh/kWh), not power.  
**Fix:** Change label to `"Energía MWh"` or `"Energía kWh"` respectively.

### 5. Incorrect relative path for data files
**Files:** `pages/precios_monomico_distribucion.py:16`, `pages/precio_energia_generacion.py:15`, `pages/precios_peaje_distribucion.py:16`
These pages construct the path as `current_dir / "data_distribuidor"` but `current_dir` is `pages/`. The data dir is at the repo root, one level up.  
**Fix:** Use `current_dir.parent / "data_distribuidor"`.

### 6. `__file__ in locals()` always evaluates to `False`
**Files:** `pages/precios_monomico_distribucion.py:15`, `pages/precio_energia_generacion.py:14`, `pages/precios_peaje_distribucion.py:15`
The expression `"__file__" in locals()` is used as a fallback check, but inside a function, `locals()` doesn't include `__file__` (it's in `globals()`). This means the fallback to `Path.cwd()` is **always** triggered.  
**Fix:** Use `globals()` instead, or simply reference `Path(__file__).parent` directly since `__file__` is always defined in Streamlit page scripts.

### 7. Inconsistent date filter UX
Some pages (`energia_por_distribuidor.py`, `energia_por_generador.py`) use a clean `st.slider` with `datetime` values and `format="YYYY-MM"`. Others (`precios_monomico_distribucion.py`, `precio_energia_generacion.py`, `precios_peaje_distribucion.py`) convert dates to Unix timestamps and use `datetime.fromtimestamp()` — worse UX and harder to read.  
**Fix:** Standardize all date filters to use the datetime-based slider pattern.

### 8. Silent column rename failure
**File:** `pages/potencia_por_tecnologia.py:376`
`stats.rename(columns={'TECNOLOGÍA': 'Tecnología'})` uses an accented `'TECNOLOGÍA'`, but the actual column name after normalization is `'TECNOLOGIA'` (unaccented). The rename silently does nothing.  
**Fix:** Use `'TECNOLOGIA'` (unaccented).

### 9. Glob patterns in exclusion lists don't work
**Files:** `dis_03_extract__energia_columns.py:16-19`, `gen_03_extract__energia_columns.py:16-19`
The `excluded_files` list contains glob patterns like `"ingresos_empresas_*.xlsx"`, but `os.listdir()` returns literal filenames — these patterns **never match**. Files matching these globs will be double-processed.  
**Fix:** Use `fnmatch` or `re` to match glob patterns, or list exact filenames.

### 10. Wrong entity column name in generation extraction
**File:** `gen_03_extract__energia_columns.py:36`
Column 0 is renamed to `"AGENTE"` but generation data uses `"CENTRAL"` as the entity identifier. Dashboard pages read `"CENTRAL"` from these files, creating a mismatch.  
**Fix:** Rename to `"CENTRAL"` instead.

### 11. Duplicate subheader
**Files:** `pages/energia_por_distribuidor.py:317-318`, `pages/energia_por_generador.py:316-317`
Two `st.subheader()` calls in a row print "Resumen de Energía por Empresa/Generador" followed immediately by "Resumen Estadístico".  
**Fix:** Remove the redundant subheader.

### 12. Dockerfile CMD references wrong filename case
**File:** `Dockerfile:40`
CMD runs `Bienvenidos.py` (capital B), but the actual file is `bienvenidos.py` (lowercase b). On case-sensitive Linux filesystems, this will **fail at runtime**.  
**Fix:** Change `Bienvenidos.py` to `bienvenidos.py`.

### 13. `stats` dataframe rendered outside `tab2`
**Files:** `pages/energia_por_distribuidor.py:361`, `pages/energia_por_generador.py:360`
The `st.dataframe(stats)` call is at the same indentation level as `with tab2:`, not inside it. It renders **below** the tab layout, always visible.  
**Fix:** Re-indent `st.dataframe(stats)` to be inside the `with tab2:` block.

---

## Upgrades

### 1. Eliminate massive code duplication
All 14 dashboard pages share ~80% identical code. Create shared utility modules:
- `utils/data_loader.py` — common `load_and_transform_data()` with configurable file paths and column names
- `utils/charts.py` — reusable chart functions (line, bar, horizontal bar, comparison)
- `utils/filters.py` — standardized sidebar filter controls

This would cut ~3000 lines of copy-paste across pages.

### 2. Convert Jupyter notebooks to Python scripts
Stage 4 of the ETL pipeline relies on 9 Jupyter notebooks that must be run manually. Convert them to parameterized Python scripts so the entire pipeline can run end-to-end with a single command (e.g., `make pipeline` or `python run_pipeline.py`).

### 3. Add configuration file
Move all hardcoded values into a YAML or TOML config file:
- File paths (data directories, downloaded files)
- Column names and indices for extraction
- Date ranges
- Entity naming conventions (AGENTE vs CENTRAL, etc.)
- Color schemes

### 4. Add proper logging
Replace `print()` and `st.error()` scattered through ETL scripts with Python's `logging` module. Add different log levels and file/console handlers.

### 5. Add CI/CD pipeline
Create a GitHub Actions workflow:
- Run `pytest` on every push
- Lint with `ruff`
- Type-check with `mypy`
- Build Docker image
- (Optional) Deploy to a server or container registry

### 6. Switch to a database
Excel files don't scale and break concurrent access. Migrate to SQLite (simple, zero-config) or PostgreSQL for:
- Proper data integrity
- Concurrent access
- Incremental updates (don't re-process all months)
- Querying instead of loading entire DataFrames

### 7. Add type hints
The entire codebase has no type annotations. Add them for better maintainability and IDE support. Use `mypy` in CI.

### 8. Optimize Dockerfile
Use multi-stage build to reduce image size:
```dockerfile
# Stage 1: build
FROM python:3.11-slim AS builder
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Stage 2: runtime
FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
COPY . .
CMD [...]
```

### 9. Add Docker Compose
For local development with a database:
```yaml
services:
  dashboard:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
```

### 10. Add data refresh automation
Create a script that:
1. Checks CNDC website for new monthly files
2. Downloads new files only (incremental)
3. Runs the full ETL pipeline
4. Rebuilds dashboard datasets

Could be scheduled via cron or GitHub Actions (if data is public).

### 11. Add loading/error states
- Show `st.spinner()` during data loading in dashboard pages
- Add `st.cache_data` TTL configuration for periodic refresh
- Surface ETL pipeline errors to the dashboard

### 12. Add Sentry / error monitoring
For production deployment, integrate [Sentry](https://sentry.io) to capture and alert on both frontend and backend errors.

### 13. Add comprehensive tests
- Unit tests for data transformation functions
- Integration tests for the full ETL pipeline (download -> extract -> transform)
- Snapshot tests for dashboard page outputs
- Test data fixtures (small synthetic Excel files)

### 14. Internationalization (i18n)
All UI text is in Spanish. Extract strings to a locale file for potential English/Portuguese support.

### 15. Use `pathlib` consistently in ETL scripts
ETL scripts (`dis_*`, `gen_*`) use `os.path` while dashboard pages use `pathlib`. Standardize on `pathlib` throughout.
