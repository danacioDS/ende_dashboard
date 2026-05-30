# Transcript 04 — Pipeline CLI, bug fixes, validation hardening

## Files Created

### `run_pipeline.py` — CLI Pipeline Orchestrator
- Entry point for the entire ETL pipeline
- `--step all|import|convert|extract|transform|validate` — run a specific stage or all
- `--distribucion` / `--generacion` — mutually exclusive selectors (default: both)
- Orchestrates: `dis_01_import_cndc` → `dis_02_convert` → `dis_03_extract__*` → `transform/dis_04_transform__*` (and `gen_*` equivalent)
- Validation step checks all 12 output datasets using `utils/validation.py`

### `notebooks_archive/` — directory for the 9 archived `.ipynb` files
- Moved: `dis_04_notebook_energia.ipynb`, `dis_04_notebook_ingresos.ipynb`, `dis_04_notebook_peaje.ipynb`, `dis_04_notebook_precios.ipynb`, `gen_04_notebook_energia.ipynb`, `gen_04_notebook_ingresos.ipynb`, `gen_04_notebook_monomico.ipynb`, `gen_04_notebook_peaje.ipynb`, `gen_04_notebook_precios.ipynb`

---

## Files Modified

### `utils/validation.py` — 3 cosmetic line-wrapping fixes + 1 logic fix
- **`validate_numeric_columns`**: Was silently passing non-numeric strings (`"abc"`) through `pd.to_numeric(errors='coerce')`. Now strips thousands separators then uses `errors='raise'`, raising `ValidationError` on truly non-numeric values. Fixes the pre-existing test failure in `test_validation.py::test_non_numeric`.
- Line-wrapped `validate_required_columns`, `validate_no_missing_critical`, `validate_output_dataset` signatures to comply with 100-char line limit.

### `dis_02_convert.py` — 1 guard fix
- Moved `convertir_todos_los_xls(FOLDER)` call inside `if __name__ == "__main__"` so importing the module doesn't auto-run conversion.

### `gen_02_convert.py` — 1 guard fix
- Same fix as `dis_02_convert.py` for generación pipeline.

### `transform/dis_04_transform__energia.py` — glob bug fix
- `combine_with_empresa_mapping` used `Path().parent.glob(absolute_pattern)` which raises `NotImplementedError` on absolute paths. Fixed to resolve glob against pattern's parent directory.

### `transform/dis_04_transform__ingresos.py` — glob bug fix
- Same glob fix in `combine_with_empresa_mapping`.

### `transform/dis_04_transform__peaje.py` — glob bug fix
- Same glob fix in `combine_with_empresa_mapping`.

### `transform/dis_04_transform__precios.py` — glob bug fix
- Same glob fix in `combine_with_empresa_mapping`.

### `transform/gen_04_transform__energia.py` — glob bug fix
- Same glob fix in `combine_with_centrales_mapping`.

### `transform/gen_04_transform__ingresos.py` — glob bug fix
- Same glob fix in `combine_with_centrales_mapping`.

### `transform/gen_04_transform__peaje.py` — glob bug fix
- Same glob fix in `combine_with_centrales_mapping`.

### `transform/gen_04_transform__precios.py` — glob bug fix
- Same glob fix in `combine_with_centrales_mapping`.

---

## End-to-End Verification

| Check | Result |
|---|---|
| `ruff check` on all modified files | 0 errors |
| `python run_pipeline.py --help` | CLI displays correctly |
| `python run_pipeline.py --step extract --distribucion` | All 4 extraction scripts run, 30+ files each |
| `python run_pipeline.py --step extract --generacion` | All 4 extraction scripts run |
| `python run_pipeline.py --step transform` (both) | All 9 transform scripts complete, no errors |
| `python run_pipeline.py --step validate` | 11/12 datasets OK, 1 SKIP (pre-existing missing TECNOLOGIA values in source) |
| `python -m pytest tests/ -v` | 68/68 passed |

---

## What was NOT changed
- `pyproject.toml` — `argparse` is stdlib, no new dependencies required
- `Dockerfile`, `docker-compose.yml` — already completed in prior sessions
- `logging_config.py` — no changes needed
- `dis_01_import_cndc.py`, `gen_01_import_cndc.py` — already had `if __name__` guards
- `dis_03_extract__*`, `gen_03_extract__*` — extraction scripts unchanged (already fixed in prior session)
