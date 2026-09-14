# Librerías
import argparse
import csv
import json
import time
import urllib.error
import urllib.request
from pathlib import Path


# ------------- RUTAS -------------
ruta = Path("Data/grupo_1.csv")
ruta_artistas_final = Path("Resultados/artistas_final.csv")
ruta_errores = Path("Resultados/errores_producidos.csv")
url_api = "https://musicbrainz.org/ws/2"


# ------------------------- OBTENER ARTISTAS -------------------------
def obtener_artistas(limite):
    artistas = []
    id_vistos = set()

    with ruta.open(encoding="utf-8-sig", newline="") as csv_archivo:
        archivo = csv.DictReader(csv_archivo)

        for fila in archivo:
            id_artista = fila["artist_mbid"].strip()
            nombre = fila["artist_name"].strip()

            if not id_artista:
                continue

            if id_artista in id_vistos:
                continue

            id_vistos.add(id_artista)
            artistas.append((id_artista, nombre))

            if len(artistas) == limite:
                break

    return artistas


# ------------------------- CONSULTAR MUSICBRAINZ -------------------------
def consultar_artista(id_artista, intentos=4):
    url = f"{url_api}/artist/{id_artista}?fmt=json&inc=genres%2Btags"
    encabezados = {"User-Agent": "ProyectoWebSemantica"}
    peticion = urllib.request.Request(url, headers=encabezados)

    for intento in range(intentos):
        try:
            with urllib.request.urlopen(peticion, timeout=60) as respuesta:
                datos = json.load(respuesta)

            time.sleep(1.0)
            return datos

        except urllib.error.HTTPError as error:
            ultimo_intento = intento == intentos - 1

            if error.code not in (429, 503) or ultimo_intento:
                raise

            time.sleep(5 * (intento + 1))

    raise RuntimeError("No se pudo consultar MusicBrainz")



# ------------------------- ORGANIZAR DATOS DEL ARTISTA -------------------------
def organizar_artista(datos, nombre, id_artista):
    tipo = datos.get("type") or ""
    area = datos.get("area") or {}
    periodo = datos.get("life-span") or {}
    fecha_inicio = periodo.get("begin") or ""
    fecha_nacimiento = ""
    fecha_formacion = ""

    if tipo == "Person":
        fecha_nacimiento = fecha_inicio
    else:
        fecha_formacion = fecha_inicio

    generos = []
    for genero in datos.get("genres", []):
        generos.append(genero["name"])

    return {
        "mbid_artista": id_artista,
        "nombre_artista": nombre,
        "nombre_musicbrainz": datos.get("name", ""),
        "tipo": tipo,
        "pais_region": area.get("name", ""),
        "fecha_nacimiento": fecha_nacimiento,
        "fecha_formacion": fecha_formacion,
        "generos_musicbrainz": " | ".join(generos),
        "source": "MusicBrainz",
        "url": "https://musicbrainz.org/artist/" + id_artista,
    }


# ------------------------- GUARDAR CONSULTAS CON ERRORES -------------------------
def guardar_errores(errores):
    columnas = ["mbid_artista", "nombre_artista", "tipo_error", "mensaje_error"]
    Path("Resultados").mkdir(parents=True, exist_ok=True)

    with ruta_errores.open("w", encoding="utf-8-sig", newline="") as csv_archivo:
        archivo = csv.DictWriter(csv_archivo, fieldnames=columnas)
        archivo.writeheader()
        archivo.writerows(errores)


# ------------------------- REVISAR ARTISTAS YA GUARDADOS -------------------------
def obtener_artistas_guardados():
    
    artistas_guardados = set()

    if not ruta_artistas_final.exists():
        return artistas_guardados

    with ruta_artistas_final.open(encoding="utf-8-sig", newline="") as csv_archivo:
        archivo = csv.DictReader(csv_archivo)

        for artista in archivo:
            artistas_guardados.add(artista["mbid_artista"])

    return artistas_guardados


# ------------- EJECUCIÓN DEL PROGRAMA -------------
if __name__ == "__main__":
    argumentos = argparse.ArgumentParser()
    argumentos.add_argument("--limite", type=int, default=5)
    opciones = argumentos.parse_args()
    errores = []
    cantidad_exitosos = 0
    columnas = [
        "mbid_artista",
        "nombre_artista",
        "nombre_musicbrainz",
        "tipo",
        "pais_region",
        "fecha_nacimiento",
        "fecha_formacion",
        "generos_musicbrainz",
        "source",
        "url",
    ]
    Path("Resultados").mkdir(parents=True, exist_ok=True)

    artistas_guardados = obtener_artistas_guardados()
    archivo_nuevo = (not ruta_artistas_final.exists() or ruta_artistas_final.stat().st_size == 0)

    with ruta_artistas_final.open("a", encoding="utf-8-sig", newline="") as csv_archivo:
        archivo = csv.DictWriter(csv_archivo, fieldnames=columnas)

        if archivo_nuevo:
            archivo.writeheader()

        for id_artista, nombre in obtener_artistas(opciones.limite):
            if id_artista in artistas_guardados:
                continue

            try:
                datos = consultar_artista(id_artista)
                artista_final = organizar_artista(datos, nombre, id_artista)

                archivo.writerow(artista_final)
                csv_archivo.flush()
                artistas_guardados.add(id_artista)

                print(nombre + ": consulta exitosa")
                cantidad_exitosos += 1
            except Exception as error:
                print(nombre + ": consulta fallida")

                errores.append(
                    {
                        "mbid_artista": id_artista,
                        "nombre_artista": nombre,
                        "tipo_error": type(error).__name__,
                        "mensaje_error": str(error),
                    }
                )

    guardar_errores(errores)

    # ------------- RESULTADOS -------------
    print("Consultas nuevas exitosas:", cantidad_exitosos)
    print("Consultas nuevas fallidas:", len(errores))
    print("Artistas totales guardados:", len(artistas_guardados))
    print("Archivo de errores:", ruta_errores)
