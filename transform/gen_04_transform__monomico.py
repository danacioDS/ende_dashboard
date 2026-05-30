from pathlib import Path
import pandas as pd
from logging_config import setup_logger

logger = setup_logger(__name__)


def extract_precio_monomico(input_path: Path, output_path: Path):
    logger.info(f"Extrayendo columnas de precio monómico de {input_path}")
    df = pd.read_excel(input_path)
    precio_cols = [col for col in df.columns if "Precio Monómico" in col]
    df_precios = df[["CENTRAL", "TECNOLOGIA"] + precio_cols]
    df_precios.to_excel(output_path, index=False)
    logger.info(f"Precios monómicos guardados en {output_path}")
    return df


def detect_outliers(input_path: Path, output_long: Path, output_comp: Path):
    logger.info("Detectando outliers en precios monómicos")
    df = pd.read_excel(input_path)

    precio_cols = [col for col in df.columns if col.startswith("Precio Monómico")]
    df_long = df.melt(
        id_vars=["CENTRAL", "TECNOLOGIA"],
        value_vars=precio_cols,
        var_name="MES",
        value_name="PRECIO_MONOMICO",
    )
    df_long["MES"] = df_long["MES"].str.extract(r"(\d{6})")
    df_long["FECHA"] = pd.to_datetime(df_long["MES"], format="%m%Y", errors="coerce")
    df_long = df_long.dropna(subset=["FECHA", "PRECIO_MONOMICO"])

    Q1 = df_long["PRECIO_MONOMICO"].quantile(0.25)
    Q3 = df_long["PRECIO_MONOMICO"].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    logger.info(f"IQR: {IQR:.2f}, límites: [{lower_bound:.2f}, {upper_bound:.2f}]")

    df_sin_outliers = df_long[
        (df_long["PRECIO_MONOMICO"] >= lower_bound)
        & (df_long["PRECIO_MONOMICO"] <= upper_bound)
    ].copy()

    original_shape = df_long.shape
    filtered_shape = df_sin_outliers.shape
    logger.info(
        f"Outliers eliminados: {original_shape[0] - filtered_shape[0]} "
        f"de {original_shape[0]} filas"
    )

    df_sin_outliers.to_excel(output_long, index=False)
    logger.info(f"Datos sin outliers guardados en {output_long}")

    df_merge = df_long.merge(
        df_sin_outliers,
        on=["CENTRAL", "FECHA"],
        suffixes=("_original", "_sin_outliers"),
    )
    subset = [
        "CENTRAL",
        "FECHA",
        "TECNOLOGIA_sin_outliers",
        "PRECIO_MONOMICO_sin_outliers",
    ]
    df_comp = df_merge[subset].copy()
    df_comp.columns = ["CENTRAL", "FECHA", "TECNOLOGIA", "PRECIO_MONOMICO"]
    df_comp["FECHA"] = pd.to_datetime(df_comp["FECHA"], format="%Y-%m-%d")
    df_comp.to_excel(output_comp, index=False)
    logger.info(f"Comparación guardada en {output_comp}")

    return df_comp


def pivot_monomico(comp_path: Path, output_path: Path):
    logger.info(f"Pivotando precios monómicos desde {comp_path}")
    df_comp = pd.read_excel(comp_path)
    df_comp["FECHA"] = pd.to_datetime(df_comp["FECHA"])
    df_comp["MES"] = df_comp["FECHA"].dt.strftime("%m%Y")
    df_comp["col_name"] = "Precio Monómico USD/MWh " + df_comp["MES"]
    df_pivot = df_comp.pivot_table(
        index=["CENTRAL", "TECNOLOGIA"],
        columns="col_name",
        values="PRECIO_MONOMICO",
    ).reset_index()

    def extract_date(col):
        if col.startswith("Precio Monómico"):
            return pd.to_datetime(col[-6:], format="%m%Y")
        return pd.NaT

    fixed_cols = ["CENTRAL", "TECNOLOGIA"]
    date_cols = sorted(
        [col for col in df_pivot.columns if col.startswith("Precio Monómico")],
        key=extract_date,
    )
    df_pivot = df_pivot[fixed_cols + date_cols]
    df_pivot.to_excel(output_path, index=False)
    logger.info(f"Tabla pivotada guardada en {output_path}")


def run_all(base_dir: Path):
    preprocess = base_dir / "preprocess"
    data_out = base_dir / "data_generacion"
    data_dir = base_dir / "data"
    preprocess.mkdir(exist_ok=True)
    data_out.mkdir(exist_ok=True)
    data_dir.mkdir(exist_ok=True)

    input_file = data_out / "serie_ingresos_generacion.xlsx"
    if not input_file.exists():
        logger.error(f"Archivo de entrada no encontrado: {input_file}")
        return

    df = extract_precio_monomico(
        input_file,
        preprocess / "serie_precios_monomico_generacion.xlsx",
    )
    df_comp = detect_outliers(
        preprocess / "serie_precios_monomico_generacion.xlsx",
        data_dir / "serie_precios_sin_outliers.xlsx",
        preprocess / "comparacion_precios_monomico_generacion.xlsx",
    )
    pivot_monomico(
        preprocess / "comparacion_precios_monomico_generacion.xlsx",
        data_dir / "precios_monomico_generacion.xlsx",
    )


if __name__ == "__main__":
    run_all(Path(__file__).resolve().parent.parent)
