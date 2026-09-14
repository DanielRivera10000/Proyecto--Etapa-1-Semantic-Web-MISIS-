# Librerías
import csv
from pathlib import Path


# ------------- RUTA DEL ARCHIVO CSV -------------
ruta = Path("Data/grupo_1.csv")


# ------------------------- ANÁLISIS DEL DATASET GRUPO_1 -------------------------
def analizar_archivo(ruta: Path) -> None:
    cantidad_filas = 0
    cantidad_duplicados = 0
    cantidad_canciones_sin_anio = 0

    canciones = set()
    id_canciones = set()

    artistas = set()
    id_artistas = set()

    combinaciones_vistas = set()

    with ruta.open(encoding="utf-8-sig", newline="") as csv_archivo:
        archivo = csv.DictReader(csv_archivo)
        columnas = archivo.fieldnames or []

        for fila in archivo:
            cantidad_filas += 1
            valores = {}

            for columna in columnas:
                valor = fila.get(columna)
                if valor is None:
                    valor = ""
                valores[columna] = valor.strip()

            canciones.add(valores["title"])
            id_canciones.add(valores["track_id"])
            artistas.add(valores["artist_name"])
            id_artistas.add(valores["artist_mbid"])

            if valores["year"] in {"", "0"}:
                cantidad_canciones_sin_anio += 1

            clave = (
                valores["title"].lower(),
                valores["artist_name"].lower(),
                valores["release"].lower(),
            )
            if clave in combinaciones_vistas:
                cantidad_duplicados += 1
            combinaciones_vistas.add(clave)

    canciones.discard("")
    id_artistas.discard("")
    cantidad_canciones_con_anio = cantidad_filas - cantidad_canciones_sin_anio

    # ------------- RESULTADOS -------------
    print("Filas:", cantidad_filas)
    print("Canciones Unicas:", len(id_canciones))
    print("Títulos Unicos:", len(canciones))
    print("Artistas Unicos:", len(id_artistas))
    print("Canciones con año:", cantidad_canciones_con_anio)
    print("Canciones sin año:", cantidad_canciones_sin_anio)
    print("Posibles Duplicados:", cantidad_duplicados)

# ------------- EJECUCIÓN DEL PROGRAMA -------------
if __name__ == "__main__":
    analizar_archivo(ruta)
