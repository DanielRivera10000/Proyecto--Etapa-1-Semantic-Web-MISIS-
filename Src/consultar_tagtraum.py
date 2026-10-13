
import csv
from pathlib import Path


# ------------- RUTAS -------------
ruta = Path("Resultados/canciones_final.csv")
ruta_tagtraum = Path("Data/Tagtraum/msd_tagtraum_cd2.cls")
ruta_salida = Path("Resultados/canciones_enriquecidas_final.csv")


# ------------------------- OBTENER GENEROS -------------------------
def obtener_generos_tagtraum():
    generos = {}

    with ruta_tagtraum.open(encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()

            if not linea or linea.startswith("#"):
                continue

            datos = linea.split("\t")

            if len(datos) not in (2, 3):
                raise ValueError("Formato incorrecto en Tagtraum")

            track_id = datos[0].strip()

            if track_id in generos:
                raise ValueError("Identificador duplicado: " + track_id)

            principal = datos[1].strip()
            minoritario = datos[2].strip() if len(datos) == 3 else ""

            generos[track_id] = (principal, minoritario)

    return generos


# ------------------------- ENRIQUECER CANCIONES -------------------------
def generar_canciones(generos):
    total = 0
    con_tagtraum = 0
    ambiguas = 0
    con_musicbrainz = 0
    con_ambas = 0

    columnas_nuevas = [
        "genero_tagtraum",
        "genero_minoritario_tagtraum",
        "clasificacion_ambigua",
        "fuente_genero",
        "fuentes_integradas",
        "estado_integracion",
    ]

    with ruta.open(encoding="utf-8-sig", newline="") as entrada:
        canciones = csv.DictReader(entrada)
        columnas = canciones.fieldnames or []

        if "track_id" not in columnas:
            raise ValueError("No se encontro la columna track_id")

        columnas_finales = columnas + [
            nombre for nombre in columnas_nuevas if nombre not in columnas
        ]

        with ruta_salida.open("w", encoding="utf-8-sig", newline="") as salida:
            archivo = csv.DictWriter(salida, fieldnames=columnas_finales)
            archivo.writeheader()

            for cancion in canciones:
                total += 1

                track_id = cancion["track_id"].strip()
                tiene_tagtraum = track_id in generos
                principal, minoritario = generos.get(track_id, ("", ""))

                tiene_musicbrainz = (
                    cancion.get("source", "").strip().lower() == "musicbrainz"
                )

                fuentes = ["Million Song Dataset"]

                if tiene_musicbrainz:
                    con_musicbrainz += 1
                    fuentes.append("MusicBrainz")

                if tiene_tagtraum:
                    con_tagtraum += 1
                    fuentes.append("Tagtraum CD2")

                    if minoritario:
                        ambiguas += 1

                if tiene_musicbrainz and tiene_tagtraum:
                    estado = "Ambas fuentes"
                    con_ambas += 1
                elif tiene_musicbrainz:
                    estado = "Solo MusicBrainz"
                elif tiene_tagtraum:
                    estado = "Solo Tagtraum"
                else:
                    estado = "Sin enriquecimiento"

                cancion.update({
                    "genero_tagtraum": principal,
                    "genero_minoritario_tagtraum": minoritario,
                    "clasificacion_ambigua": (
                        ("Si" if minoritario else "No") if tiene_tagtraum else ""
                    ),
                    "fuente_genero": "Tagtraum CD2" if tiene_tagtraum else "",
                    "fuentes_integradas": " | ".join(fuentes),
                    "estado_integracion": estado,
                })

                archivo.writerow(cancion)

    # ------------------------- RESULTADOS -------------------------
    print("Archivo generado:", ruta_salida)
    print("Canciones totales:", total)
    print("Canciones con Tagtraum:", con_tagtraum)
    print("Canciones con ambas fuentes:", con_ambas)


# ------------- EJECUCION DEL PROGRAMA -------------
if __name__ == "__main__":
    Path("Resultados").mkdir(parents=True, exist_ok=True)

    generos = obtener_generos_tagtraum()
    generar_canciones(generos)

