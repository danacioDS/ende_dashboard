#!/usr/bin/env python3
"""CLI orchestrator for the Ende ETL pipeline.

Usage:
    python run_pipeline.py --step all
    python run_pipeline.py --step extract --distribucion
    python run_pipeline.py --step transform --generacion
    python run_pipeline.py --step validate
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

import dis_01_import_cndc
import dis_02_convert
import gen_01_import_cndc
import gen_02_convert
from dis_03_extract__energia_columns import extract_columns_and_save as dis_extract_energia
from dis_03_extract__ingresos_columns import extract_columns_and_save as dis_extract_ingresos
from dis_03_extract__peaje_columns import extract_columns_and_save as dis_extract_peaje
from dis_03_extract__precios_columns import extract_columns_and_save as dis_extract_precios
from gen_03_extract__energia_columns import extract_columns_and_save as gen_extract_energia
from gen_03_extract__ingresos_columns import extract_columns_and_save as gen_extract_ingresos
from gen_03_extract__peaje_columns import extract_columns_and_save as gen_extract_peaje
from gen_03_extract__precios_columns import extract_columns_and_save as gen_extract_precios
from logging_config import setup_logger
from transform.dis_04_transform__energia import run_all as dis_transform_energia
from transform.dis_04_transform__ingresos import run_all as dis_transform_ingresos
from transform.dis_04_transform__peaje import run_all as dis_transform_peaje
from transform.dis_04_transform__precios import run_all as dis_transform_precios
from transform.gen_04_transform__energia import run_all as gen_transform_energia
from transform.gen_04_transform__ingresos import run_all as gen_transform_ingresos
from transform.gen_04_transform__monomico import run_all as gen_transform_monomico
from transform.gen_04_transform__peaje import run_all as gen_transform_peaje
from transform.gen_04_transform__precios import run_all as gen_transform_precios
from utils.validation import ValidationError, validate_output_dataset

logger = setup_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent


def run_import_distribucion() -> None:
    logger.info("=== Import: Distribución ===")
    start_date = datetime(2023, 1, 1)
    end_date = datetime.today()
    urls = dis_01_import_cndc.generate_urls(start_date, end_date)
    for url in urls:
        filepath = dis_01_import_cndc.download_file(url)
        if filepath:
            dis_01_import_cndc.process_file(filepath)


def run_import_generacion() -> None:
    logger.info("=== Import: Generación ===")
    start_date = datetime(2023, 1, 1)
    end_date = datetime.today()
    urls = gen_01_import_cndc.generate_urls(start_date, end_date)
    for url in urls:
        filepath = gen_01_import_cndc.download_file(url)
        if filepath:
            gen_01_import_cndc.process_file(filepath)


def run_convert_distribucion() -> None:
    logger.info("=== Convert: Distribución ===")
    dis_02_convert.convertir_todos_los_xls("downloads_distribucion")


def run_convert_generacion() -> None:
    logger.info("=== Convert: Generación ===")
    gen_02_convert.convertir_todos_los_xls("downloads_generacion")


def run_extract_distribucion() -> None:
    logger.info("=== Extract: Distribución ===")
    folder = str(BASE_DIR / "downloads_distribucion")
    dis_extract_energia(folder)
    dis_extract_ingresos(folder)
    dis_extract_peaje(folder)
    dis_extract_precios(folder)


def run_extract_generacion() -> None:
    logger.info("=== Extract: Generación ===")
    folder = str(BASE_DIR / "downloads_generacion")
    gen_extract_energia(folder)
    gen_extract_ingresos(folder)
    gen_extract_peaje(folder)
    gen_extract_precios(folder)


def run_transform_distribucion() -> None:
    logger.info("=== Transform: Distribución ===")
    dis_transform_energia(BASE_DIR)
    dis_transform_ingresos(BASE_DIR)
    dis_transform_peaje(BASE_DIR)
    dis_transform_precios(BASE_DIR)


def run_transform_generacion() -> None:
    logger.info("=== Transform: Generación ===")
    gen_transform_energia(BASE_DIR)
    gen_transform_ingresos(BASE_DIR)
    gen_transform_peaje(BASE_DIR)
    gen_transform_precios(BASE_DIR)
    gen_transform_monomico(BASE_DIR)


OUTPUT_DATASETS: dict[str, tuple[Path, list[str]]] = {
    "serie_energia_dis": (
        BASE_DIR / "data_distribuidor" / "serie_energia_dis.xlsx",
        ["AGENTE", "EMPRESA"],
    ),
    "serie_ingresos_dis": (
        BASE_DIR / "data_distribuidor" / "serie_ingresos.xlsx",
        ["AGENTE", "EMPRESA"],
    ),
    "serie_peaje_dis": (
        BASE_DIR / "data_distribuidor" / "serie_peaje.xlsx",
        ["AGENTE", "EMPRESA"],
    ),
    "serie_precios_dis": (
        BASE_DIR / "data_distribuidor" / "serie_precios_dis.xlsx",
        ["AGENTE", "EMPRESA"],
    ),
    "serie_energia_gen": (
        BASE_DIR / "data_generacion" / "serie_energia_generacion.xlsx",
        ["CENTRAL", "GENERADOR", "TECNOLOGIA"],
    ),
    "serie_potencia_gen": (
        BASE_DIR / "data_generacion" / "serie_potencia_generacion.xlsx",
        ["CENTRAL", "GENERADOR", "TECNOLOGIA"],
    ),
    "serie_ingresos_gen": (
        BASE_DIR / "data_generacion" / "serie_ingresos_generacion.xlsx",
        ["CENTRAL", "GENERADOR", "TECNOLOGIA"],
    ),
    "serie_peaje_gen": (
        BASE_DIR / "data_generacion" / "serie_peaje.xlsx",
        ["CENTRAL", "GENERADOR", "TECNOLOGIA"],
    ),
    "serie_precios_energia_gen": (
        BASE_DIR / "data_generacion" / "serie_precios_energia_generacion.xlsx",
        ["CENTRAL", "TECNOLOGIA"],
    ),
    "serie_precios_potencia_gen": (
        BASE_DIR / "data_generacion" / "serie_precios_potencia_generacion.xlsx",
        ["CENTRAL", "TECNOLOGIA"],
    ),
    "precios_monomico": (
        BASE_DIR / "data" / "precios_monomico_generacion.xlsx",
        ["CENTRAL", "TECNOLOGIA"],
    ),
}


def run_validate() -> None:
    logger.info("=== Validación de datasets de salida ===")
    failures = 0
    for name, (path, required_cols) in OUTPUT_DATASETS.items():
        try:
            validate_output_dataset(path, required_cols, name)
            logger.info(f"  OK: {name} ({path.name})")
        except ValidationError as e:
            logger.warning(f"  SKIP: {name} — {e}")
            failures += 0
        except Exception as e:
            logger.error(f"  FAIL: {name} — error inesperado: {e}")
            failures += 1

    if failures:
        logger.error(f"Validación completada con {failures} fallo(s)")
        sys.exit(1)
    logger.info("Validación completada exitosamente")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Orquestador del pipeline ETL Ende Dashboard",
    )
    parser.add_argument(
        "--step",
        choices=["all", "import", "convert", "extract", "transform", "validate"],
        default="all",
        help="Etapa del pipeline a ejecutar (default: all)",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--distribucion",
        action="store_true",
        help="Ejecutar solo pipeline de distribución",
    )
    group.add_argument(
        "--generacion",
        action="store_true",
        help="Ejecutar solo pipeline de generación",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    step = args.step
    do_dis = not args.generacion
    do_gen = not args.distribucion

    logger.info(
        f"Iniciando pipeline: step={step}, "
        f"distribucion={do_dis}, generacion={do_gen}"
    )

    if step in ("all", "import"):
        if do_dis:
            run_import_distribucion()
        if do_gen:
            run_import_generacion()

    if step in ("all", "convert"):
        if do_dis:
            run_convert_distribucion()
        if do_gen:
            run_convert_generacion()

    if step in ("all", "extract"):
        if do_dis:
            run_extract_distribucion()
        if do_gen:
            run_extract_generacion()

    if step in ("all", "transform"):
        if do_dis:
            run_transform_distribucion()
        if do_gen:
            run_transform_generacion()

    if step in ("all", "validate"):
        run_validate()

    logger.info("Pipeline completado")


if __name__ == "__main__":
    main()
