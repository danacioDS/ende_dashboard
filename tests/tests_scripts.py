import os
import pytest

generacion_scripts = [
    "generacion/energia_por_generador.py",
    "generacion/energia_por_tecnologia.py",
    "generacion/capacidad_instalada.py",
    "generacion/costos_generacion.py",
    "generacion/mix_energetico.py"
]

distribucion_scripts = [
    "distribucion/demanda_zonas.py",
    "distribucion/perdidas_tecnicas.py",
    "distribucion/calidad_servicio.py",
    "distribucion/tarifas_electricas.py",
    "distribucion/cobertura_servicio.py"
]

@pytest.mark.parametrize("script", generacion_scripts + distribucion_scripts)
def test_script_existe(script):
    assert os.path.exists(script), f"El script {script} no existe"