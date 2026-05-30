from __future__ import annotations

from pathlib import Path
import fnmatch

import pandas as pd
from logging_config import setup_logger

logger = setup_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent
DOWNLOAD_FOLDER = BASE_DIR / "downloads_generacion"


def extract_columns_and_save(folder: str | Path) -> None:
    excluded_patterns = [
        "serie_*", "ingresos_empresas_*", "precios_empresas_*",
        "energia_empresas_*",
    ]

    folder_path = Path(folder)

    for file in folder_path.iterdir():
        if not file.name.endswith(".xlsx") or file.name.startswith("extracted_"):
            continue
        if any(fnmatch.fnmatch(file.name, p) for p in excluded_patterns):
            continue

        try:
            df = pd.read_excel(file)
            df = df.iloc[:, [0, 10, 12, 14, 16, 18]]
            df.columns = [
                "CENTRAL",
                "Peaje ENDE Trans. USD/MWh",
                "Peaje ISA USD/MWh",
                "Peaje ENDE USD/MWh",
                "Peaje TESA USD/MWh",
                "Peaje filiales ENDE US$/MWh",
            ]
            output_file = folder_path / f"extracted_peaje_{file.name}"
            df.to_excel(output_file, index=False)
            logger.info(f"Archivo {file.name} procesado y guardado como {output_file}.")
        except Exception as e:
            logger.error(f"Error al procesar {file.name}: {e}")


if __name__ == "__main__":
    extract_columns_and_save(DOWNLOAD_FOLDER)
