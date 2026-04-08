import os
import tempfile
import subprocess
from Bienvenidos import ejecutar_script, mostrar_codigo

def test_mostrar_codigo_crea_codigo(monkeypatch):
    # Crear un archivo temporal
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".py") as tmp:
        tmp.write("x = 5\ny = 10\nprint(x + y)")
        tmp_path = tmp.name

    # Verificar que la función no arroja error
    mostrar_codigo(tmp_path)

    # Limpiar archivo temporal
    os.remove(tmp_path)

def test_ejecutar_script_exitoso(monkeypatch):
    # Crear un script temporal que imprime algo
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".py") as tmp:
        tmp.write("print('Hola mundo')")
        tmp_path = tmp.name

    # Ejecutar el script
    ejecutar_script(tmp_path)

    # Limpiar archivo temporal
    os.remove(tmp_path)

def test_ejecutar_script_inexistente():
    # Archivo que no existe
    ejecutar_script("archivo_que_no_existe.py")