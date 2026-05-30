import re
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd
from logging_config import setup_logger

logger = setup_logger(__name__)


def combine_with_empresa_mapping(
    empresas_file: Path,
    input_pattern: str,
    output_prefix: Path,
):
    logger.info("Iniciando combinación con mapeo de empresas (ingresos)")
    try:
        df_empresas = pd.read_excel(empresas_file)
        if "AGENTE" not in df_empresas.columns or "EMPRESA" not in df_empresas.columns:
            logger.error("El archivo empresas debe contener columnas 'AGENTE' y 'EMPRESA'")
            return
        df_empresas["AGENTE"] = df_empresas["AGENTE"].astype(str).str.strip()
        mapeo_empresas = dict(zip(df_empresas["AGENTE"], df_empresas["EMPRESA"]))
        nombres_empresas = {k: k for k in df_empresas["AGENTE"].unique()}
    except Exception as e:
        logger.error(f"Error cargando {empresas_file}: {e}")
        return

    base = Path(input_pattern).parent
    pat = Path(input_pattern).name
    for input_file in sorted(base.glob(pat)):
        if not input_file.name.endswith(".xlsx"):
            continue
        match = re.search(r"extracted_ingresos_c_ret_(\d+)\.xlsx", input_file.name)
        if not match:
            continue
        file_number = match.group(1)
        output_file = output_prefix / f"ingresos_empresas_{file_number}.xlsx"
        if output_file.exists():
            logger.info(f"Archivo {output_file} ya existe. Omitiendo.")
            continue
        try:
            df_energia = pd.read_excel(input_file)
            df_energia.columns = [col.strip() for col in df_energia.columns]
            agent_col = next(
                (col for col in df_energia.columns if "agente" in col.lower()), None
            )
            if agent_col and agent_col != "AGENTE":
                df_energia = df_energia.rename(columns={agent_col: "AGENTE"})
            if "AGENTE" not in df_energia.columns:
                logger.error(f"No se encontró columna 'AGENTE' en {input_file}")
                continue
            df_energia["AGENTE"] = df_energia["AGENTE"].astype(str).str.strip()

            def normalizar_nombre(x):
                x = str(x).strip()
                if x in nombres_empresas:
                    return nombres_empresas[x]
                x_clean = x.replace("-", "").replace(" ", "")
                for k in nombres_empresas:
                    if k.replace("-", "").replace(" ", "") == x_clean:
                        return nombres_empresas[k]
                return x

            df_energia["AGENTE_NORMALIZADO"] = df_energia["AGENTE"].apply(normalizar_nombre)
            df_energia["EMPRESA"] = df_energia["AGENTE_NORMALIZADO"].map(mapeo_empresas)
            cols = ["AGENTE_NORMALIZADO", "EMPRESA"] + [
                col
                for col in df_energia.columns
                if col not in ["AGENTE_NORMALIZADO", "EMPRESA", "AGENTE"]
            ]
            df_resultado = df_energia[cols].rename(
                columns={"AGENTE_NORMALIZADO": "AGENTE"}
            )
            df_resultado.to_excel(output_file, index=False)
            logger.info(f"Procesado: {input_file} -> {output_file}")
            if df_resultado["EMPRESA"].isna().any():
                missing = df_resultado[df_resultado["EMPRESA"].isna()]["AGENTE"].unique()
                logger.warning(f"{len(missing)} agentes sin empresa asignada: {list(missing[:3])}")
        except Exception as e:
            logger.error(f"Error procesando {input_file}: {e}")


def consolidate_to_long(output_prefix: Path, output_path: Path):
    logger.info("Consolidando a formato largo (ingresos)")
    archivos = sorted(output_prefix.glob("ingresos_empresas_*.xlsx"))
    if not archivos:
        logger.warning("No se encontraron archivos para consolidar.")
        return
    registros = []
    for archivo in archivos:
        try:
            periodo = archivo.stem.split("_")[-1]
            mes = int(periodo[:2])
            año = 2000 + int(periodo[2:])
            fecha = datetime(año, mes, 1)
            df = pd.read_excel(archivo)
            if "AGENTE" not in df.columns:
                logger.warning(f"Omitido: {archivo} no tiene columna AGENTE.")
                continue
            for col in df.columns:
                if col in ["AGENTE", "EMPRESA"]:
                    continue
                temp = df[["AGENTE", "EMPRESA", col]].copy()
                temp["FECHA"] = fecha
                temp["VARIABLE"] = col
                temp = temp.rename(columns={col: "VALOR"})
                registros.append(temp)
        except Exception as e:
            logger.error(f"Error procesando {archivo}: {e}")
            continue
    if not registros:
        logger.error("No se pudo consolidar ningún archivo válido.")
        return
    df_largo = pd.concat(registros, ignore_index=True)
    df_largo = df_largo[["FECHA", "AGENTE", "EMPRESA", "VARIABLE", "VALOR"]]
    df_largo.to_excel(output_path, index=False)
    logger.info(f"Consolidación completada. Filas: {len(df_largo)}. Guardado en {output_path}")


def pivot_and_calculate_monomico(input_path: Path, output_path: Path, data_output: Path):
    logger.info("Pivotando y calculando precio monómico (ingresos)")
    df = pd.read_excel(input_path)
    df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce", unit="d")
    df = df.dropna(subset=["FECHA"])
    df["AGENTE"] = df["AGENTE"].astype(str).str.strip()
    df["EMPRESA"] = df["EMPRESA"].astype(str).str.strip()
    df["VARIABLE"] = df["VARIABLE"].astype(str).str.strip()
    df = df[
        df["VARIABLE"].isin(
            [
                "Energía MWh",
                "Ingresos Energía MWh",
                "Ingresos Renovables MWh",
                "Ingresos Potencia kW",
            ]
        )
    ]
    df["VALOR"] = pd.to_numeric(df["VALOR"], errors="coerce")
    df = df.dropna(subset=["VALOR"])
    df["MES_ANIO"] = df["FECHA"].dt.strftime("%m%Y")
    df["AGENTE"] = df["AGENTE"].replace("nan", pd.NA).ffill()
    df["EMPRESA"] = df["EMPRESA"].replace("nan", pd.NA).ffill()
    df["COLUMNA"] = df["VARIABLE"] + " " + df["MES_ANIO"]
    df_pivot = df.pivot_table(
        index=["AGENTE", "EMPRESA"],
        columns="COLUMNA",
        values="VALOR",
        aggfunc="first",
    )
    cols = df_pivot.columns.tolist()

    def extraer_anio_mes(col_name):
        fecha = col_name.split()[-1]
        mes = int(fecha[:2])
        anio = int(fecha[2:])
        return (anio, mes)

    energia_cols = sorted(
        [c for c in cols if c.startswith("Energía MWh")], key=extraer_anio_mes
    )
    ingresos_energia_cols = sorted(
        [c for c in cols if c.startswith("Ingresos Energía MWh")], key=extraer_anio_mes
    )
    ingresos_renovables_cols = sorted(
        [c for c in cols if c.startswith("Ingresos Renovables MWh")],
        key=extraer_anio_mes,
    )
    ingresos_potencia_cols = sorted(
        [c for c in cols if c.startswith("Ingresos Potencia kW")],
        key=extraer_anio_mes,
    )
    cols_ordenadas = (
        energia_cols
        + ingresos_energia_cols
        + ingresos_renovables_cols
        + ingresos_potencia_cols
    )
    df_pivot = df_pivot[cols_ordenadas]
    df_final = df_pivot.reset_index()
    df_final.to_excel(output_path, index=False)
    logger.info(f"Serie cronológica guardada en {output_path}")

    # Depuración y cálculo de precio monómico
    agentes_a_eliminar = [
        "TOTAL - CESSA", "TOTAL - CRE R.L.", "TOTAL CRE", "TOTAL - DELAPAZ",
        "TOTAL - ELFEC", "TOTAL - ENDE", "TOTAL ENDE DELBENI S.A.M.",
        "TOTAL - ENDE DEORURO S.A.", "TOTALES", "Tipo de cambio",
        "TOTAL - SEPSA", "TOTAL - SETAR",
    ]
    df = df_final[~df_final["AGENTE"].isin(agentes_a_eliminar)].copy()

    numeric_cols = df.columns.drop(["AGENTE", "EMPRESA"])
    for col in numeric_cols:
        if df[col].dtype == object:
            df[col] = df[col].str.replace(",", "", regex=False)
        df[col] = pd.to_numeric(df[col], errors="coerce")

    periods = []
    for col in df.columns:
        if col.startswith("Energía MWh "):
            period = col.split(" ")[-1]
            periods.append(period)

    for period in periods:
        energia_col = f"Energía MWh {period}"
        ing_ener_col = f"Ingresos Energía MWh {period}"
        ing_ren_col = f"Ingresos Renovables MWh {period}"
        ing_pot_col = f"Ingresos Potencia kW {period}"
        precio_col = f"Precio Monómico USD/MWh {period}"
        if all(
            col in df.columns
            for col in [energia_col, ing_ener_col, ing_ren_col, ing_pot_col]
        ):
            total_ingresos = df[ing_ener_col] + df[ing_ren_col] + df[ing_pot_col]
            df[precio_col] = np.where(
                df[energia_col] > 0,
                (total_ingresos / df[energia_col]) * 1000,
                np.nan,
            )
        else:
            logger.warning(f"Columnas incompletas para el período {period}")

    df.to_excel(data_output, index=False)
    logger.info(f"Datos con precio monómico guardados en {data_output}")


def run_all(base_dir: Path):
    empresas_file = base_dir / "data_distribuidor" / "empresas_distribuidoras.xlsx"
    pre_data = base_dir / "pre_data"
    preprocess = base_dir / "preprocess"
    data_out = base_dir / "data_distribuidor"
    pre_data.mkdir(exist_ok=True)
    preprocess.mkdir(exist_ok=True)
    data_out.mkdir(exist_ok=True)

    combine_with_empresa_mapping(
        empresas_file,
        str(base_dir / "downloads_distribucion" / "extracted_ingresos_c_ret_*.xlsx"),
        pre_data,
    )
    consolidate_to_long(
        pre_data,
        preprocess / "serie_temporal_ingresos_dis.xlsx",
    )
    pivot_and_calculate_monomico(
        preprocess / "serie_temporal_ingresos_dis.xlsx",
        preprocess / "serie_ingresos_cronologica_dis.xlsx",
        data_out / "serie_ingresos.xlsx",
    )


if __name__ == "__main__":
    run_all(Path(__file__).resolve().parent.parent)
