from __future__ import annotations

from pathlib import Path
import zipfile
from datetime import datetime, timedelta

import requests
from logging_config import setup_logger

logger = setup_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent
DOWNLOAD_FOLDER = BASE_DIR / "downloads_distribucion"

DOWNLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


def generate_urls(start_date: datetime, end_date: datetime) -> list[str]:
    base_url = "https://www.cndc.bo/media/archivos/estadistica_mensual/c_ret_"
    urls: list[str] = []
    current_date = start_date

    while current_date <= end_date:
        month_year = current_date.strftime("%m%y")
        urls.append(f"{base_url}{month_year}.zip")
        urls.append(f"{base_url}{month_year}.xlsx")
        current_date += timedelta(days=31)
        current_date = current_date.replace(day=1)

    return urls


def download_file(url: str) -> Path | None:
    filename = url.split("/")[-1]
    filepath = DOWNLOAD_FOLDER / filename

    try:
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            with open(filepath, "wb") as file:
                file.write(response.content)
            logger.info(f"Descargado: {filename}")
            return filepath
        else:
            logger.warning(f"Archivo no encontrado: {filename} (Código: {response.status_code})")
            return None
    except Exception as e:
        logger.error(f"Error al descargar {filename}: {str(e)}")
        return None


def process_file(filepath: Path | None) -> None:
    if not filepath:
        return

    if filepath.suffix == ".zip":
        try:
            with zipfile.ZipFile(filepath, "r") as zip_ref:
                zip_ref.extractall(DOWNLOAD_FOLDER)
                logger.info(f"Extraído: {filepath.name}")
                logger.info(f"Archivos extraídos: {zip_ref.namelist()}")
            filepath.unlink()
        except Exception as e:
            logger.error(f"Error al extraer {filepath}: {str(e)}")
    elif filepath.suffix == ".xlsx":
        logger.info(f"Archivo Excel descargado: {filepath.name}")


if __name__ == "__main__":
    start_date = datetime(2023, 1, 1)
    end_date = datetime.today()

    urls = generate_urls(start_date, end_date)

    for url in urls:
        filepath = download_file(url)
        if filepath:
            process_file(filepath)
