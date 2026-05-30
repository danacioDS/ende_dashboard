from __future__ import annotations

from pathlib import Path

import pyexcel as pe

from logging_config import setup_logger

logger = setup_logger(__name__)

FOLDER = "downloads_distribucion"


def convertir_todos_los_xls(carpeta: str | Path) -> None:
    for archivo in Path(carpeta).iterdir():
        if archivo.suffix == ".xls":
            ruta_xlsx = archivo.with_suffix(".xlsx")

            if ruta_xlsx.exists():
                logger.info(f"Ya existe: {ruta_xlsx}, saltado.")
                continue

            try:
                libro = pe.get_book(file_name=str(archivo))
                libro.save_as(str(ruta_xlsx))
                logger.info(f"Convertido exitosamente: {ruta_xlsx}")
            except Exception as e:
                logger.error(f"Error al convertir {archivo}: {e}")


if __name__ == "__main__":
    convertir_todos_los_xls(FOLDER)
