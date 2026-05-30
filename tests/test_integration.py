"""Integration tests for the ETL pipeline."""
import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DATA_DIRS = [
    "data_generacion",
    "data_distribuidor",
    "downloads_generacion",
    "downloads_distribucion",
    "preprocess",
]

OUTPUT_FILES = {
    "data_distribuidor": [
        "serie_energia_dis.xlsx",
        "serie_ingresos.xlsx",
        "serie_peaje.xlsx",
        "serie_precios_dis.xlsx",
    ],
    "data_generacion": [
        "serie_energia_generacion.xlsx",
        "serie_potencia_generacion.xlsx",
        "serie_ingresos_generacion.xlsx",
        "serie_peaje.xlsx",
        "serie_precios_energia_generacion.xlsx",
        "serie_precios_potencia_generacion.xlsx",
    ],
}


class TestDataDirectories:
    @pytest.mark.parametrize("dir_name", DATA_DIRS)
    def test_data_dir_exists(self, dir_name):
        path = ROOT / dir_name
        assert path.is_dir(), f"Missing directory: {dir_name}"

class TestOutputDatasets:
    @pytest.mark.parametrize("subdir,files", OUTPUT_FILES.items())
    def test_output_files_exist(self, subdir, files):
        for f in files:
            path = ROOT / subdir / f
            assert path.exists(), f"Missing output file: {subdir}/{f}"
            assert path.stat().st_size > 0, f"Empty file: {subdir}/{f}"

    @pytest.mark.parametrize("subdir,files", OUTPUT_FILES.items())
    def test_output_files_readable(self, subdir, files):
        import pandas as pd
        for f in files:
            path = ROOT / subdir / f
            df = pd.read_excel(path)
            assert not df.empty, f"DataFrame empty for {subdir}/{f}"
