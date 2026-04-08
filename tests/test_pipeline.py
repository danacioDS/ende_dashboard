from bienvenidos import ejecutar_script, mostrar_codigo
import pytest
import os

def test_ejecutar_script_archivo_inexistente():
    # Debe manejar archivo que no existe
    non_existent_file = "no_existe.py"
    ejecutar_script(non_existent_file)
    # Se puede verificar que no lanza excepción y muestra error

def test_mostrar_codigo_archivo_inexistente():
    # Debe manejar archivo que no existe
    non_existent_file = "no_existe.py"
    mostrar_codigo(non_existent_file)
    # Verifica que no lanza excepción y muestra error   