from setuptools import setup, find_packages

setup(
    name="ende_dashboard",
    version="0.1.0",
    description="Ende Dashboard: ETL and Streamlit visualization for CNDC electricity data",
    author="Daniel Canedo",
    packages=find_packages(where="."),  # Busca todos los paquetes en el proyecto
    python_requires=">=3.12",
    install_requires=[
        "pandas",
        "numpy",
        "requests",
        "openpyxl",
        "pyarrow",
        "streamlit",
        "plotly",
        "matplotlib",
        "altair",
        "pytest"
    ],
)