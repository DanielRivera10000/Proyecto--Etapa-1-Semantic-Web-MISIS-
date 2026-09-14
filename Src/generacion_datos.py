
import csv
from pathlib import Path


# ------------- RUTAS -------------
ruta = Path("Data/grupo_1.csv")
ruta_artistas_final = Path("Resultados/artistas_final.csv")
ruta_canciones_final = Path("Resultados/canciones_final.csv")


# ------------------------- OBTENER CANCIONES -------------------------
def obtener_canciones():
    canciones = []

    with ruta.open(encoding="utf-8-sig", newline="") as csv_archivo:
        archivo = csv.DictReader(csv_archivo)
        columnas = archivo.fieldnames or []

        for cancion in archivo:
            canciones.append(cancion)

    return canciones, columnas


# ------------------------- CARGAR ARTISTAS ENRIQUECIDOS -------------------------
def cargar_artistas_final():

    artistas_final = {}

    with ruta_artistas_final.open(encoding="utf-8-sig", newline="") as csv_archivo:
        archivo = csv.DictReader(csv_archivo)

        for artista in archivo:
            id_artista = artista["mbid_artista"]
            artistas_final[id_artista] = artista

    return artistas_final


# ------------------------- GENERAR CANCIONES ENRIQUECIDAS (Conexiones) -------------------------
def generar_canciones(artistas_final):
    canciones, columnas_originales = obtener_canciones()
    cantidad_enriquecidas = 0

    columnas_nuevas = [
        "nombre_musicbrainz",
        "tipo",
        "pais_region",
        "fecha_nacimiento",
        "fecha_formacion",
        "generos_musicbrainz",
        "source",
        "url",
        "estado",
    ]

    with ruta_canciones_final.open("w", encoding="utf-8-sig", newline="") as csv_archivo:
        archivo = csv.DictWriter(csv_archivo, fieldnames=columnas_originales + columnas_nuevas,)
        archivo.writeheader()

        for cancion in canciones:
            id_artista = cancion["artist_mbid"].strip()
            artista = artistas_final.get(id_artista)

            if artista:
                cancion["nombre_musicbrainz"] = artista["nombre_musicbrainz"]
                cancion["tipo"] = artista["tipo"]
                cancion["pais_region"] = artista["pais_region"]
                cancion["fecha_nacimiento"] = artista["fecha_nacimiento"]
                cancion["fecha_formacion"] = artista["fecha_formacion"]
                cancion["generos_musicbrainz"] = artista["generos_musicbrainz"]
                cancion["source"] = artista["source"]
                cancion["url"] = artista["url"]
                cancion["estado"] = "enriquecida"
                cantidad_enriquecidas += 1
            else:
                for columna in columnas_nuevas:
                    cancion[columna] = ""
                cancion["estado"] = "sin consultar"

            archivo.writerow(cancion)

    cantidad_canciones = len(canciones)

    # ------------- RESULTADOS -------------
    print("Archivo generado:", ruta_canciones_final)
    print("Canciones totales:", cantidad_canciones)
    print("Canciones enriquecidas:", cantidad_enriquecidas)
    print("Canciones sin enriquecer:", cantidad_canciones - cantidad_enriquecidas)


# ------------- EJECUCIÓN DEL PROGRAMA -------------
if __name__ == "__main__":
    Path("Resultados").mkdir(parents=True, exist_ok=True)
    artistas_final = cargar_artistas_final()
    generar_canciones(artistas_final)
