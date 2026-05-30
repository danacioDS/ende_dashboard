import os
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def path(rel):
    return os.path.join(ROOT, rel)


ETL_SCRIPTS = [
    "dis_01_import_cndc.py",
    "dis_02_convert.py",
    "dis_03_extract__energia_columns.py",
    "dis_03_extract__ingresos_columns.py",
    "dis_03_extract__peaje_columns.py",
    "dis_03_extract__precios_columns.py",
    "gen_01_import_cndc.py",
    "gen_02_convert.py",
    "gen_03_extract__energia_columns.py",
    "gen_03_extract__ingresos_columns.py",
    "gen_03_extract__peaje_columns.py",
    "gen_03_extract__precios_columns.py",
]

DASHBOARD_PAGES = [
    "bienvenidos.py",
    "pages/energia_por_distribuidor.py",
    "pages/energia_por_generador.py",
    "pages/energia_por_tecnologia.py",
    "pages/potencia_distribuidoras.py",
    "pages/potencia_por_generador.py",
    "pages/potencia_por_tecnologia.py",
    "pages/precio_energia_distribucion.py",
    "pages/precio_energia_generacion.py",
    "pages/precio_potencia_distribucion.py",
    "pages/precio_potencia_generacion.py",
    "pages/precios_monomico_distribucion.py",
    "pages/precios_monomicos_generacion.py",
    "pages/precios_peaje_distribucion.py",
    "pages/precios_peaje_generacion.py",
]

TRANSFORM_FILES = [
    "run_pipeline.py",
]

UTILITY_FILES = [
    "utils/__init__.py",
    "utils/data_loader.py",
    "utils/charts.py",
    "utils/filters.py",
    "utils/validation.py",
]


@pytest.mark.parametrize("rel_path", ETL_SCRIPTS + DASHBOARD_PAGES + TRANSFORM_FILES + UTILITY_FILES)
def test_file_exists(rel_path):
    assert os.path.exists(path(rel_path)), f"Archivo faltante: {rel_path}"


DATA_DIRS = [
    "data_generacion",
    "data_distribuidor",
    "downloads_generacion",
    "downloads_distribucion",
    "preprocess",
    "transform",
]


@pytest.mark.parametrize("data_dir", DATA_DIRS)
def test_data_dir_exists(data_dir):
    assert os.path.isdir(path(data_dir)), f"Directorio faltante: {data_dir}"


def test_etl_scripts_are_importable():
    for script in ETL_SCRIPTS:
        with open(path(script)) as f:
            code = f.read()
        assert "def " in code, f"{script} parece no tener funciones"
