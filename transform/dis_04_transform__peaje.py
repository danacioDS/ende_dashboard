import re
from datetime import datetime
from pathlib import Path
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

MAPEO_AGENTE_EMPRESA = {
    "Guaracachi": "CRE", "Urubó": "CRE", "Urubó 115 kV": "CRE",
    "Urubó 115": "CRE", "Arboleda": "CRE", "Warnes": "CRE",
    "Brechas": "CRE", "Brechas 69": "CRE", "Brechas 115": "CRE",
    "Troncos": "CRE", "Troncos 115": "CRE", "Troncos - Las Misiones": "CRE",
    "Troncos 115 (Las Misiones)": "CRE", "Yapacaní": "CRE", "Bélgica": "CRE",
    "San Julián": "CRE", "Camiri - Cordillera": "CRE", "Guarayos": "CRE",
    "Kenko": "DELAPAZ", "Cumbre": "DELAPAZ", "Chuspipata": "DELAPAZ",
    "Caranavi": "DELAPAZ", "San Buenaventura": "DELAPAZ", "Palca": "DELAPAZ",
    "Contorno Bajo": "DELAPAZ", "Choquetanga": "DELAPAZ",
    "Arocagua": "ELFEC", "Valle Hermoso": "ELFEC", "Irpa Irpa": "ELFEC",
    "Chimore": "ELFEC", "San José": "ELFEC", "Paracaya": "ELFEC",
    "Carrasco": "ELFEC", "Qollpana": "ELFEC", "Villa Tunari": "ELFEC",
    "Santivañez": "ELFEC",
    "Vinto": "ENDE DEORURO S.A.", "Vinto 115": "ENDE DEORURO S.A.",
    "Catavi": "ENDE DEORURO S.A.", "Jeruyo": "ENDE DEORURO S.A.",
    "Lucianita": "ENDE DEORURO S.A.", "Catavi 115": "ENDE DEORURO S.A.",
    "Pagador": "ENDE DEORURO S.A.",
    "Sacaca": "SEPSA", "Ocuri": "SEPSA", "Potosí": "SEPSA",
    "Potosí 115": "SEPSA", "Potosi 69": "SEPSA", "Potosi 115": "SEPSA",
    "Punutuma": "SEPSA", "Don Diego": "SEPSA", "CM  Karachipampa": "SEPSA",
    "Litio - Lipez": "SEPSA", "Litio 115 kV": "SEPSA", "Torre Huayco": "SEPSA",
    "Portugalete": "SEPSA", "Chilcobija": "SEPSA", "Telamayu": "SEPSA",
    "La Plata": "SEPSA", "ECEBOL Potosí": "SEPSA",
    "Mariaca": "CESSA", "Sucre": "CESSA", "Sucre - Fancesa": "CESSA",
    "Sucre 115": "CESSA",
    "Tazna": "ENDE", "Uyuni": "ENDE", "Uyuni - Uyuni": "ENDE",
    "Las Carreras": "ENDE",
    "Tarija": "SETAR", "Villamontes": "SETAR", "Yacuiba": "SETAR",
    "Bermejo": "SETAR",
    "Yucumo": "ENDE DELBENI S.A.M.", "San Borja": "ENDE DELBENI S.A.M.",
    "San Ignacio de Moxos": "ENDE DELBENI S.A.M.", "Trinidad": "ENDE DELBENI S.A.M.",
    "Paraíso": "ENDE DELBENI S.A.M.",
    "EMDEECRUZ": "NO REGULADOS", "EMVINTO - COMIBOL": "NO REGULADOS",
    "COBOCE": "NO REGULADOS", "MINERA SAN CRISTOBAL S.A.": "NO REGULADOS",
    "YLB (Contrato ENDE)": "NO REGULADOS", "LAS LOMAS": "NO REGULADOS",
    "CERAMICA GUADALQUIVIR": "NO REGULADOS", "EMPACAR S.A.": "NO REGULADOS",
    "Aguaí Energia": "AGUAÍ ENERGÍA S.A.", "Aguai (Autoproductor)": "AGUAÍ ENERGÍA S.A.",
}


def detectar_fila_encabezado(df):
    for i, row in df.iterrows():
        if any(str(cell).strip().upper() == "AGENTE" for cell in row):
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


def procesar_archivos(
    centrales_file: Path, input_pattern: str, output_prefix: Path
):
    logger.info("Procesando archivos de peaje (distribución)")
    try:
        df_centrales = pd.read_excel(centrales_file)
        df_centrales["AGENTE"] = df_centrales["AGENTE"].astype(str).str.strip()
        if not {"AGENTE", "EMPRESA"}.issubset(df_centrales.columns):
            logger.error("El archivo debe contener columnas 'AGENTE' y 'EMPRESA'")
            return
        mapeo_generadores = dict(zip(df_centrales["AGENTE"], df_centrales["EMPRESA"]))
        nombres_centrales = set(df_centrales["AGENTE"])
        mapeo_completo = {**mapeo_generadores, **MAPEO_AGENTE_EMPRESA}
    except Exception as e:
        logger.error(f"Error al cargar archivo de mapeo {centrales_file}: {e}")
        return

    base = Path(input_pattern).parent
    pat = Path(input_pattern).name
    for input_file in sorted(base.glob(pat)):
        if not input_file.name.endswith(".xlsx"):
            continue
        match = re.search(r"extracted_peaje_c_ret_(\d+)\.xlsx", input_file.name)
        if not match:
            continue
        file_number = match.group(1)
        output_file = output_prefix / f"peaje_agentes_{file_number}.xlsx"
        if output_file.exists():
            logger.info(f"[Omitido] {output_file} ya existe.")
            continue
        try:
            df_raw = pd.read_excel(input_file, header=None)
            start_row = detectar_fila_encabezado(df_raw)
            df = pd.read_excel(input_file, skiprows=start_row)
            df.columns = [str(col).strip() for col in df.columns]
            if df.columns.duplicated().any():
                df = df.loc[:, ~df.columns.duplicated(keep="first")]
            central_col = next(
                (
                    c
                    for c in df.columns
                    if "central" in c.lower() or "agente" in c.lower()
                ),
                None,
            )
            if central_col and central_col != "AGENTE":
                df = df.rename(columns={central_col: "AGENTE"})
            if "AGENTE" not in df.columns:
                logger.error(f"No se encontró columna 'AGENTE' en {input_file}")
                continue
            df["AGENTE"] = df["AGENTE"].astype(str).str.strip()
            pattern_basura = r"TOTAL|TOTALES|Nota|Tipo de cambio|nan|CARGOS POR INYECCIONES|TOTAL\s*-\s*AGUAI"
            df = df[~df["AGENTE"].str.contains(pattern_basura, case=False, na=True, regex=True)]
            df = df[~df["AGENTE"].str.match(r"^\d{4}-\d{2}-\d{2}", na=False)]
            df = df[~df["AGENTE"].str.upper().str.contains(r"AGENTE\s*ENERGIA|POTENCIA", na=False)]
            df = df[df["AGENTE"].notna() & (df["AGENTE"] != "")]
            df["AGENTE_CLEAN"] = df["AGENTE"].str.strip().str.upper()
            centrales_validas = set(x.upper() for x in nombres_centrales)
            first_valid_idx = df[df["AGENTE_CLEAN"].isin(centrales_validas)].index.min()
            if pd.isna(first_valid_idx):
                logger.error(f"No se encontraron centrales válidas en {input_file}")
                continue
            df = df.loc[first_valid_idx:].copy()
            df["AGENTE_NORMALIZADA"] = df["AGENTE"].apply(
                lambda x: normalizar_nombre(x, nombres_centrales, ALIAS)
            )
            df["EMPRESA"] = df["AGENTE_NORMALIZADA"].map(mapeo_completo)
            aguai_centrales = ["Aguaí Energia", "Aguai (Autoproductor)"]
            for central in aguai_centrales:
                if central not in df["AGENTE_NORMALIZADA"].values:
                    nueva_fila = {"AGENTE_NORMALIZADA": central, "EMPRESA": "AGUAÍ ENERGÍA S.A."}
                    for col in df.columns:
                        if "kW" in col or "kWh" in col or "USD" in col:
                            nueva_fila[col] = 0.0
                    df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
            for col in df.columns:
                if "kW" in col or "kWh" in col or "USD" in col:
                    df[col] = (
                        df[col]
                        .astype(str)
                        .str.replace(",", "")
                        .str.replace(" ", "")
                        .replace("nan", None)
                        .astype(float)
                    )
            peaje_cols = [col for col in df.columns if "Peaje" in col and "USD" in col]
            columnas_conservar = ["AGENTE_NORMALIZADA", "EMPRESA"] + peaje_cols
            df_final = df[columnas_conservar].copy()
            df_final = df_final.rename(columns={"AGENTE_NORMALIZADA": "AGENTE"})
            rename_columns = {
                "Energía": "Energía kWh",
                "Potencia Firme Remunerada": "Potencia kW",
            }
            df_final = df_final.rename(columns=rename_columns)
            df_final.to_excel(output_file, index=False)
            logger.info(f"[OK] {input_file} -> {output_file}")
            faltantes = df_final[df_final["EMPRESA"].isna()]["AGENTE"].unique()
            if len(faltantes) > 0:
                logger.warning(f"{len(faltantes)} centrales sin EMPRESA: {list(faltantes[:3])}")
        except Exception as e:
            logger.error(f"[Error] {input_file}: {e}")
            try:
                Path("./errors").mkdir(exist_ok=True)
                df.to_excel(f"./errors/ERROR_{file_number}.xlsx", index=False)
            except Exception as inner_e:
                logger.error(f"Error al guardar archivo de error: {inner_e}")


def consolidate_to_long(output_prefix: Path, output_path: Path):
    logger.info("Consolidando a formato largo (peaje)")
    archivos = sorted(output_prefix.glob("peaje_agentes_*.xlsx"))
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
            columnas_necesarias = ["AGENTE", "EMPRESA"]
            columnas_datos = [col for col in df.columns if col not in columnas_necesarias]
            if not columnas_datos:
                logger.warning(f"Omitido: {archivo} no tiene columnas de datos.")
                continue
            if "TECNOLOGIA" not in df.columns:
                df["TECNOLOGIA"] = None
            temp = pd.melt(
                df,
                id_vars=["AGENTE", "EMPRESA"],
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
    df_largo = df_largo[["FECHA", "AGENTE", "EMPRESA", "VARIABLE", "VALOR"]]
    df_largo.to_excel(output_path, index=False)
    logger.info(f"Consolidación completada. Filas: {len(df_largo)}. Guardado en {output_path}")


def pivot_and_aggregate_peaje(input_path: Path, pivot_path: Path, output_path: Path):
    logger.info("Pivotando y agregando peaje")
    df = pd.read_excel(input_path)
    df["FECHA"] = pd.to_datetime(df["FECHA"])
    df["PERIODO"] = df["FECHA"].dt.strftime("%m%Y")
    df["COLUMNA"] = df["VARIABLE"] + " " + df["PERIODO"]
    tabla_pivot = df.pivot_table(
        index=["AGENTE", "EMPRESA"],
        columns="COLUMNA",
        values="VALOR",
        aggfunc="sum",
    ).reset_index()
    fixed_cols = ["AGENTE", "EMPRESA"]
    other_cols = [c for c in tabla_pivot.columns if c not in fixed_cols]
    cols_df = pd.DataFrame(
        {
            "col_name": other_cols,
            "variable": [c.split()[0] for c in other_cols],
            "periodo": [c.split()[-1] for c in other_cols],
        }
    )
    cols_df["fecha"] = pd.to_datetime(cols_df["periodo"], format="%m%Y")
    cols_df = cols_df.sort_values(by=["variable", "fecha"])
    ordered_columns = fixed_cols + cols_df["col_name"].tolist()
    tabla_pivot = tabla_pivot[ordered_columns]
    tabla_pivot.to_excel(pivot_path, index=False)
    logger.info(f"Pivot guardado en {pivot_path}")

    # Depuración: agregar columnas de peaje por mes
    df = pd.read_excel(pivot_path)
    peaje_cols = [
        col
        for col in df.columns
        if "Peaje" in col
        and any(x in col for x in ["ENDE Trans.", "ENDE USD", "ISA", "TESA", "filiales"])
    ]
    fechas = sorted(set(col.split()[-1] for col in peaje_cols))
    peaje_generacion = pd.DataFrame(df[fixed_cols])
    for fecha in fechas:
        columnas_mes = [col for col in peaje_cols if col.endswith(fecha)]
        peaje_generacion[f"Peaje generación USD/MWh {fecha}"] = df[columnas_mes].sum(axis=1)
    cols_ordenadas = fixed_cols + sorted(
        [col for col in peaje_generacion.columns if col.startswith("Peaje generación")],
        key=lambda x: pd.to_datetime(x.split()[-1], format="%m%Y"),
    )
    peaje_generacion = peaje_generacion[cols_ordenadas]
    peaje_generacion.to_excel(output_path, index=False)
    logger.info(f"Peaje agregado guardado en {output_path}")


def run_all(base_dir: Path):
    centrales_file = base_dir / "data_distribuidor" / "empresas_distribuidoras.xlsx"
    pre_data = base_dir / "pre_data"
    preprocess = base_dir / "preprocess"
    data_out = base_dir / "data_distribuidor"
    pre_data.mkdir(exist_ok=True)
    preprocess.mkdir(exist_ok=True)
    data_out.mkdir(exist_ok=True)

    procesar_archivos(
        centrales_file,
        str(base_dir / "downloads_distribucion" / "extracted_peaje_c_ret_*.xlsx"),
        pre_data,
    )
    consolidate_to_long(pre_data, preprocess / "serie_peaje_filiales.xlsx")
    pivot_and_aggregate_peaje(
        preprocess / "serie_peaje_filiales.xlsx",
        preprocess / "serie_peaje_filiales_2.xlsx",
        data_out / "serie_peaje.xlsx",
    )


if __name__ == "__main__":
    run_all(Path(__file__).resolve().parent.parent)
