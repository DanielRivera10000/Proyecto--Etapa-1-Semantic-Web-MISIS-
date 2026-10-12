
# Librerías
import csv
from pathlib import Path


# ------------- RUTAS -------------
ruta = Path("Resultados/canciones_final.csv")
ruta_tagtraum = Path("Data/Tagtraum/msd_tagtraum_cd2.cls")
ruta_canciones_final = Path("Resultados/canciones_enriquecidas_final.csv")


# ------------------------- OBTENER GENEROS TAGTRAUM -------------------------
def obtener_generos_tagtraum():
    generos = {}

    with ruta_tagtraum.open(encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()

            # Ignorar comentarios y lineas vacias
            if not linea or linea.startswith("#"):
                continue

            datos = linea.split("\t")

            if len(datos) not in (2, 3):
                raise ValueError("Formato incorrecto en Tagtraum")

            id_cancion = datos[0].strip()
            genero_principal = datos[1].strip()

            genero_minoritario = ""
            if len(datos) == 3:
                genero_minoritario = datos[2].strip()

            if id_cancion in generos:
                raise ValueError("Identificador duplicado: " + id_cancion)

            generos[id_cancion] = {
                "genero_principal": genero_principal,
                "genero_minoritario": genero_minoritario,
            }

    return generos


# ------------------------- GENERAR CANCIONES ENRIQUECIDAS -------------------------
def generar_canciones(generos):
    cantidad_canciones = 0
    cantidad_tagtraum = 0
    cantidad_ambiguas = 0
    cantidad_musicbrainz = 0
    cantidad_ambas = 0

    columnas_nuevas = [
        "genero_tagtraum",
        "genero_minoritario_tagtraum",
        "clasificacion_ambigua",
        "fuente_genero",
        "fuentes_integradas",
        "estado_integracion",
    ]

    with ruta.open(encoding="utf-8-sig", newline="") as csv_entrada:
        canciones = csv.DictReader(csv_entrada)
        columnas_originales = canciones.fieldnames or []

        if "track_id" not in columnas_originales:
            raise ValueError("No se encontro la columna track_id")

        columnas_finales = columnas_originales + [
            columna for columna in columnas_nuevas
            if columna not in columnas_originales
        ]

        with ruta_canciones_final.open(
            "w", encoding="utf-8-sig", newline=""
        ) as csv_salida:

            archivo = csv.DictWriter(
                csv_salida,
                fieldnames=columnas_finales
            )
            archivo.writeheader()

            for cancion in canciones:
                cantidad_canciones += 1

                id_cancion = cancion["track_id"].strip()
                genero = generos.get(id_cancion)

                tiene_musicbrainz = (
                    cancion.get("source", "").strip().lower()
                    == "musicbrainz"
                )

                fuentes = ["Million Song Dataset"]

                if tiene_musicbrainz:
                    cantidad_musicbrainz += 1
                    fuentes.append("MusicBrainz")

                if genero:
                    cantidad_tagtraum += 1

                    cancion["genero_tagtraum"] = genero["genero_principal"]
                    cancion["genero_minoritario_tagtraum"] = genero["genero_minoritario"]

                    if genero["genero_minoritario"]:
                        cancion["clasificacion_ambigua"] = "Si"
                        cantidad_ambiguas += 1
                    else:
                        cancion["clasificacion_ambigua"] = "No"

                    cancion["fuente_genero"] = "Tagtraum CD2"
                    fuentes.append("Tagtraum CD2")

                else:
                    cancion["genero_tagtraum"] = ""
                    cancion["genero_minoritario_tagtraum"] = ""
                    cancion["clasificacion_ambigua"] = ""
                    cancion["fuente_genero"] = ""

                # Identificar que fuentes enriquecieron la cancion
                if tiene_musicbrainz and genero:
                    cancion["estado_integracion"] = "Ambas fuentes"
                    cantidad_ambas += 1

                elif tiene_musicbrainz:
                    cancion["estado_integracion"] = "Solo MusicBrainz"

                elif genero:
                    cancion["estado_integracion"] = "Solo Tagtraum"

                else:
                    cancion["estado_integracion"] = "Sin enriquecimiento"

                cancion["fuentes_integradas"] = " | ".join(fuentes)

                archivo.writerow(cancion)

    # ------------- RESULTADOS -------------
    print("Archivo generado:", ruta_canciones_final)
    print("Canciones totales:", cantidad_canciones)
    print("Canciones con Tagtraum:", cantidad_tagtraum)
    print("Clasificaciones ambiguas:", cantidad_ambiguas)
    print("Canciones con MusicBrainz:", cantidad_musicbrainz)
    print("Canciones con ambas fuentes:", cantidad_ambas)
    print(
        "Canciones enriquecidas por al menos una fuente:",
        cantidad_tagtraum + cantidad_musicbrainz - cantidad_ambas
    )


# ------------- EJECUCION DEL PROGRAMA -------------
if __name__ == "__main__":
    Path("Resultados").mkdir(parents=True, exist_ok=True)

    generos = obtener_generos_tagtraum()
    generar_canciones(generos)
