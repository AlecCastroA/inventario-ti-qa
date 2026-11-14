import os

ENTORNOS_VALIDOS = {"desarrollo", "prueba", "produccion"}


def obtener_entorno() -> str:
    """Devuelve el entorno activo: desarrollo, prueba o produccion."""
    entorno = os.getenv("APP_ENV", "desarrollo")
    return entorno if entorno in ENTORNOS_VALIDOS else "desarrollo"