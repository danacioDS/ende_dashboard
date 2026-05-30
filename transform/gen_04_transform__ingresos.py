import re
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd
from logging_config import setup_logger

logger = setup_logger(__name__)

ALIAS = {
    "Kanata en Arocagua": "Kanata ARO",
    "Kanata en Valle Hermoso": "Kanata VHE",
    "Misicuni en Arocagua": "Misicuni ARO",
    "Misicuni en Valle Hermoso": "Misicuni VHE",
    "Yunchara": "Yunchara",
    "Aguaí Energía": "Aguaí Energia",
    "AGUAÍ ENERGÍA S.A.": "Aguaí Energia",
    "Santa Cruz (Aguaí)": "Santa Cruz (Aguaí)",
    "RÍO ELÉCTRICO S.A.": "RIO ELECTRICO S.A.",
    "CHACO ENERGÍAS S.A.": "CHACO ENERGIAS S.A.",
    "RIOELEC S.A.": "RIO ELECTRICO S.A.",
}


def detectar_fila_encabezado(df):
    for i, row in df.iterrows():
        if any(str(cell).strip().upper() == "CENTRAL" for cell in row):
            return i
    return 0


def normalizar_nombre(nombre, nombres_centrales, alias):
    x = str(nombre).strip()
    if x in alias:
        return alias[x]
    x_clean = re.sub(r"\W+", "", x).upper()
    for k in nombres_centrales:
        k_clean = re.sub(r"\W+", "", k).upper()
        if k_clean == x_clean:
            return k
    if "AGUAI" in x_clean or "AGUAÍ" in x_clean:
        if "AUTOPRODUCTOR" in x_clean:
            return "Aguai (Autoproductor)"
        return "Aguaí Energia"
    return x


def procesar_archivos(centrales_file: Path, input_pattern: str, output_prefix: Path):
    logger.info("Procesando archivos de ingresos (generación)")
    try:
        df_centrales = pd.read_excel(centrales_file)
        df_centrales["CENTRAL"] = df_centrales["CENTRAL"].astype(str).str.strip()
        if not {"CENTRAL", "GENERADOR", "TECNOLOGIA"}.issubset(df_centrales.columns):
            logger.error("El archivo debe contener columnas 'CENTRAL', 'GENERADOR' y 'TECNOLOGIA'")
            return
        mapeo_generadores = dict(zip(df_centrales["CENTRAL"], df_centrales["GENERADOR"]))
        mapeo_tecnologia = dict(zip(df_centrales["CENTRAL"], df_centrales["TECNOLOGIA"]))
        nombres_centrales = set(df_centrales["CENTRAL"])
        for central_aguai in ["Aguaí Energia", "Aguai (Autoproductor)"]:
            if central_aguai not in mapeo_generadores:
                mapeo_generadores[central_aguai] = "AGUAÍ ENERGÍA S.A."
                mapeo_tecnologia[central_aguai] = "Biomasa"
    except Exception as e:
        logger.error(f"Error al cargar archivo de mapeo {centrales_file}: {e}")
        return

    base = Path(input_pattern).parent
    pat = Path(input_pattern).name
    for input_file in sorted(base.glob(pat)):
        if not input_file.name.endswith(".xlsx"):
            continue
        match = re.search(r"extracted_ingresos_c_iny_(\d+)\.xlsx", input_file.name)
        if not match:
            continue
        file_number = match.group(1)
        output_file = output_prefix / f"ingresos_centrales_{file_number}.xlsx"
        if output_file.exists():
            logger.info(f"[Omitido] {output_file} ya existe.")
            continue
        try:
            df_raw = pd.read_excel(input_file, header=None)
            start_row = detectar_fila_encabezado(df_raw)
            df = pd.read_excel(input_file, skiprows=start_row)
            df.columns = [str(col).strip() for col in df.columns]
            central_col = next(
                (
                    c
                    for c in df.columns
                    if "central" in c.lower() or "agente" in c.lower()
                ),
                None,
            )
            if central_col and central_col != "CENTRAL":
                df = df.rename(columns={central_col: "CENTRAL"})
            if "CENTRAL" not in df.columns:
                logger.error(f"No se encontró columna 'CENTRAL' en {input_file}")
                continue
            df["CENTRAL"] = df["CENTRAL"].astype(str).str.strip()
            pattern_basura = r"TOTAL|TOTALES|Nota|Tipo de cambio|nan|CARGOS POR INYECCIONES|TOTAL\s*-\s*AGUAI"
            df = df[~df["CENTRAL"].str.contains(pattern_basura, case=False, na=True, regex=True)]
            df = df[~df["CENTRAL"].str.match(r"^\d{4}-\d{2}-\d{2}", na=False)]
            df = df[~df["CENTRAL"].str.upper().str.contains(r"CENTRAL\s*ENERGIA|POTENCIA", na=False)]
            df = df[df["CENTRAL"].notna() & (df["CENTRAL"] != "")]
            df["CENTRAL_CLEAN"] = df["CENTRAL"].str.strip().str.upper()
            centrales_validas = set(x.upper() for x in nombres_centrales)
            first_valid_idx = df[df["CENTRAL_CLEAN"].isin(centrales_validas)].index.min()
            if pd.isna(first_valid_idx):
                logger.error(f"No se encontraron centrales válidas en {input_file}")
                continue
            df = df.loc[first_valid_idx:].copy()
            df["CENTRAL_NORMALIZADA"] = df["CENTRAL"].apply(
                lambda x: normalizar_nombre(x, nombres_centrales, ALIAS)
            )
            df["GENERADOR"] = df["CENTRAL_NORMALIZADA"].map(mapeo_generadores)
            df["TECNOLOGIA"] = df["CENTRAL_NORMALIZADA"].map(mapeo_tecnologia)
            aguai_centrales = ["Aguaí Energia", "Aguai (Autoproductor)"]
            for central in aguai_centrales:
                if central not in df["CENTRAL_NORMALIZADA"].values:
                    nueva_fila = {
                        "CENTRAL": central,
                        "CENTRAL_NORMALIZADA": central,
                        "GENERADOR": "AGUAÍ ENERGÍA S.A.",
                        "TECNOLOGIA": "Biomasa",
                    }
                    for col in df.columns:
                        if "kW" in col or "kWh" in col:
                            nueva_fila[col] = 0.0
                    df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
            for col in df.columns:
                if "kW" in col or "kWh" in col:
                    df[col] = (
                        df[col]
                        .astype(str)
                        .str.replace(",", "")
                        .str.replace(" ", "")
                        .replace("nan", None)
                        .astype(float)
                    )
            columnas_finales = ["CENTRAL_NORMALIZADA", "GENERADOR", "TECNOLOGIA"] + [
                c
                for c in df.columns
                if c not in ["CENTRAL", "CENTRAL_NORMALIZADA", "CENTRAL_CLEAN", "GENERADOR", "TECNOLOGIA"]
            ]
            df_final = df[columnas_finales].rename(columns={"CENTRAL_NORMALIZADA": "CENTRAL"})
            df_final.to_excel(output_file, index=False)
            logger.info(f"[OK] {input_file} -> {output_file}")
            faltantes = df_final[df_final["GENERADOR"].isna()]["CENTRAL"].unique()
            if len(faltantes) > 0:
                logger.warning(f"{len(faltantes)} centrales sin GENERADOR: {list(faltantes[:3])}")
        except Exception as e:
            logger.error(f"[Error] {input_file}: {e}")
            try:
                Path("./errors").mkdir(exist_ok=True)
                df.to_excel(f"./errors/ERROR_{file_number}.xlsx", index=False)
            except Exception as inner_e:
                logger.error(f"Error al guardar archivo de error: {inner_e}")


def consolidate_to_long(output_prefix: Path, output_path: Path):
    logger.info("Consolidando a formato largo (ingresos generación)")
    archivos = sorted(output_prefix.glob("ingresos_centrales_*.xlsx"))
    if not archivos:
        logger.warning("No se encontraron archivos.")
        return
    registros = []
    for archivo in archivos:
        try:
            periodo = archivo.stem.split("_")[-1]
            mes = int(periodo[:2])
            año = 2000 + int(periodo[2:])
            fecha = datetime(año, mes, 1)
            df = pd.read_excel(archivo)
            if "CENTRAL" not in df.columns:
                logger.warning(f"Omitido: {archivo} no tiene columna CENTRAL.")
                continue
            columnas_necesarias = ["CENTRAL", "GENERADOR"]
            columnas_datos = [col for col in df.columns if col not in columnas_necesarias + ["TECNOLOGIA"]]
            if not columnas_datos:
                logger.warning(f"Omitido: {archivo} no tiene columnas de datos.")
                continue
            if "TECNOLOGIA" not in df.columns:
                df["TECNOLOGIA"] = None
            temp = pd.melt(
                df,
                id_vars=["CENTRAL", "GENERADOR", "TECNOLOGIA"],
                value_vars=columnas_datos,
                var_name="VARIABLE",
                value_name="VALOR",
            )
            temp["FECHA"] = fecha
            registros.append(temp)
        except Exception as e:
            logger.error(f"Error procesando {archivo}: {e}")
            continue
    if not registros:
        logger.error("No se pudo consolidar ningún archivo válido.")
        return
    df_largo = pd.concat(registros, ignore_index=True)
    df_largo = df_largo[["FECHA", "CENTRAL", "GENERADOR", "TECNOLOGIA", "VARIABLE", "VALOR"]]
    df_largo.to_excel(output_path, index=False)
    logger.info(f"Consolidación completada. Filas: {len(df_largo)}. Guardado en {output_path}")


def pivot_and_calculate_monomico(
    input_path: Path, output_path: Path, data_output: Path
):
    logger.info("Pivotando y calculando precio monómico (ingresos generación)")
    df = pd.read_excel(input_path)
    df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce", unit="d")
    df = df.dropna(subset=["FECHA"])
    df["CENTRAL"] = df["CENTRAL"].astype(str).str.strip()
    df["GENERADOR"] = df["GENERADOR"].astype(str).str.strip()
    df["TECNOLOGIA"] = df["TECNOLOGIA"].astype(str).str.strip()
    df["VARIABLE"] = df["VARIABLE"].astype(str).str.strip()
    df = df[
        df["VARIABLE"].isin(
            [
                "Energía KWh",
                "Ingresos Energía USD",
                "Ingresos Renovables USD",
                "Ingresos Potencia USD",
            ]
        )
    ]
    df["VALOR"] = pd.to_numeric(df["VALOR"], errors="coerce")
    df = df.dropna(subset=["VALOR"])
    df["MES_ANIO"] = df["FECHA"].dt.strftime("%m%Y")
    df["CENTRAL"] = df["CENTRAL"].replace("nan", pd.NA).ffill()
    df["GENERADOR"] = df["GENERADOR"].replace("nan", pd.NA).ffill()
    df["COLUMNA"] = df["VARIABLE"] + " " + df["MES_ANIO"]
    df_pivot = df.pivot_table(
        index=["CENTRAL", "GENERADOR", "TECNOLOGIA"],
        columns="COLUMNA",
        values="VALOR",
        aggfunc="first",
    )
    cols = df_pivot.columns.tolist()

    def extraer_anio_mes(col_name):
        try:
            fecha = col_name.split()[-1]
            mes = int(fecha[:2])
            anio = int(fecha[2:])
            return (anio, mes)
        except Exception:
            return (0, 0)

    energia_cols = sorted(
        [c for c in cols if c.startswith("Energía KWh")], key=extraer_anio_mes
    )
    ingresos_energia_cols = sorted(
        [c for c in cols if c.startswith("Ingresos Energía USD")], key=extraer_anio_mes
    )
    ingresos_renovables_cols = sorted(
        [c for c in cols if c.startswith("Ingresos Renovables USD")],
        key=extraer_anio_mes,
    )
    ingresos_potencia_cols = sorted(
        [c for c in cols if c.startswith("Ingresos Potencia USD")],
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
    df = df_final[~df_final["CENTRAL"].isin(agentes_a_eliminar)].copy()
    numeric_cols = df.columns.drop(["CENTRAL", "GENERADOR", "TECNOLOGIA"])
    for col in numeric_cols:
        if df[col].dtype == object:
            df[col] = df[col].str.replace(",", "", regex=False)
        df[col] = pd.to_numeric(df[col], errors="coerce")

    periods = []
    for col in df.columns:
        if col.startswith("Energía KWh") or col.startswith("Ingresos Energía USD") or col.startswith("Ingresos Renovables USD") or col.startswith("Ingresos Potencia USD"):
            period = col.split(" ")[-1]
            periods.append(period)

    for period in set(periods):
        energia_col = f"Energía KWh {period}"
        ing_ener_col = f"Ingresos Energía USD {period}"
        ing_ren_col = f"Ingresos Renovables USD {period}"
        ing_pot_col = f"Ingresos Potencia USD {period}"
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
    centrales_file = base_dir / "data_generacion" / "empresas_generadoras.xlsx"
    pre_data = base_dir / "pre_data"
    preprocess = base_dir / "preprocess"
    data_out = base_dir / "data_generacion"
    pre_data.mkdir(exist_ok=True)
    preprocess.mkdir(exist_ok=True)
    data_out.mkdir(exist_ok=True)

    procesar_archivos(
        centrales_file,
        str(base_dir / "downloads_generacion" / "extracted_ingresos_c_iny_*.xlsx"),
        pre_data,
    )
    consolidate_to_long(pre_data, preprocess / "serie_temporal_ingresos_generacion.xlsx")
    pivot_and_calculate_monomico(
        preprocess / "serie_temporal_ingresos_generacion.xlsx",
        preprocess / "serie_ingresos_cronologica_generacion.xlsx",
        data_out / "serie_ingresos_generacion.xlsx",
    )


if __name__ == "__main__":
    run_all(Path(__file__).resolve().parent.parent)
