import csv
import hashlib

from decimal import Decimal
from pathlib import Path
from urllib.parse import quote
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, XSD

# ------------- RUTAS Y URL -------------
ruta = Path("Resultados/canciones_enriquecidas_final.csv")
MUSIC = Namespace("https://github.com/DanielRivera10000/Proyecto--Etapa-1-Semantic-Web-MISIS-/ontology#")
RECURSOS = Namespace("https://github.com/DanielRivera10000/Proyecto--Etapa-1-Semantic-Web-MISIS-/recurso/")


def crear_uri(tipo, texto):
    texto = " ".join(texto.strip().casefold().split())
    clave = hashlib.sha256(texto.encode("utf-8")).hexdigest()[:24]
    return URIRef(str(RECURSOS) + tipo + "/" + clave)


def agregar_dato(grafo, sujeto, propiedad, valor, tipo=None):
    if str(valor).strip():
        grafo.add((sujeto, propiedad, Literal(str(valor).strip(), datatype=tipo)))


# ------------------------- GENERAR INSTANCIAS -------------------------
def generar_instancias():
    grafo = Graph()
    grafo.bind("music", MUSIC)
    grafo.bind("res", RECURSOS)
    canciones = set()
    registrados = {tipo: set() for tipo in ("artista", "lanzamiento", "genero", "lugar")}

    def registrar(tipo, clave, nombre, clase):
        recurso = crear_uri(tipo, clave)
        if recurso not in registrados[tipo]:
            registrados[tipo].add(recurso)
            grafo.add((recurso, RDF.type, clase))
            agregar_dato(grafo, recurso, MUSIC.nombre, nombre)
        return recurso

    # ------------------------- FUENTES -------------------------
    fuentes = {
        "msd": RECURSOS["fuente/million-song-dataset"],
        "musicbrainz": RECURSOS["fuente/musicbrainz"],
        "tagtraum": RECURSOS["fuente/tagtraum-cd2"],
    }

    for clave, nombre in [("msd", "Million Song Dataset"),
                          ("musicbrainz", "MusicBrainz"), ("tagtraum", "Tagtraum CD2")]:
        grafo.add((fuentes[clave], RDF.type, MUSIC.Fuente))
        agregar_dato(grafo, fuentes[clave], MUSIC.nombre, nombre)

    agregar_dato(grafo, fuentes["musicbrainz"], MUSIC.url, "https://musicbrainz.org/", XSD.anyURI)

    # ------------------------- LEER CSV -------------------------
    with ruta.open(encoding="utf-8-sig", newline="") as archivo_csv:
        archivo = csv.DictReader(archivo_csv)

        necesarias = {"track_id", "title", "year", "duration", "artist_mbid", "artist_name", "release"}
        faltantes = necesarias - set(archivo.fieldnames or [])

        if faltantes:
            raise ValueError("Faltan columnas: " + ", ".join(sorted(faltantes)))

        for fila in archivo:
            track_id = fila["track_id"].strip()

            if not track_id or track_id in canciones:
                raise ValueError("track_id vacio o duplicado: " + track_id)

            canciones.add(track_id)

            # ------------------------- CANCIONES -------------------------
            cancion = URIRef(str(RECURSOS) + "cancion/" + quote(track_id, safe=""))

            grafo.add((cancion, RDF.type, MUSIC.Cancion))
            grafo.add((cancion, MUSIC.obtenidoDe, fuentes["msd"]))

            agregar_dato(grafo, cancion, MUSIC.track_id, track_id)
            agregar_dato(grafo, cancion, MUSIC.titulo, fila["title"])

            anio = fila["year"].strip()
            if anio and anio != "0":
                agregar_dato(grafo, cancion, MUSIC.anio, int(anio), XSD.integer)

            duracion = fila["duration"].strip()
            if duracion:
                valor = Decimal(duracion)
                if valor.is_finite() and valor >= 0:
                    agregar_dato(grafo, cancion, MUSIC.duracion, valor, XSD.decimal)

            # ------------------------- ARTISTAS -------------------------
            mbid = fila["artist_mbid"].strip()
            nombre = fila["artist_name"].strip()
            artista = None

            if mbid:
                artista = URIRef(str(RECURSOS) + "artista/" + quote(mbid.lower(), safe=""))
            elif nombre:
                artista = crear_uri("artista/sin-mbid", nombre)

            if artista is not None:
                registrados["artista"].add(artista)

                grafo.add((artista, RDF.type, MUSIC.Artista))
                grafo.add((artista, MUSIC.obtenidoDe, fuentes["msd"]))
                grafo.add((cancion, MUSIC.interpretadoPor, artista))

                for columna, propiedad in [
                    ("artist_mbid", MUSIC.mbid_artista),
                    ("artist_name", MUSIC.nombre_artista),
                    ("nombre_musicbrainz", MUSIC.nombre_musicbrainz),
                ]:
                    agregar_dato(grafo, artista, propiedad, fila.get(columna, ""))

                # ------------------------- PERSONA Y GRUPO -------------------------
                tipo = fila.get("tipo", "").strip().lower()

                if tipo == "person":
                    grafo.add((artista, RDF.type, MUSIC.Persona))
                    agregar_dato(grafo, artista, MUSIC.fecha_nacimiento,
                                 fila.get("fecha_nacimiento", ""))

                elif tipo in ("group", "orchestra", "choir"):
                    grafo.add((artista, RDF.type, MUSIC.Grupo))
                    agregar_dato(grafo, artista, MUSIC.fecha_formacion,
                                 fila.get("fecha_formacion", ""))

                # ------------------------- LUGARES -------------------------
                pais = fila.get("pais_region", "").strip()

                if pais:
                    lugar = registrar("lugar", pais, pais, MUSIC.Lugar)
                    grafo.add((artista, MUSIC.asociadoALugar, lugar))

                # ------------------------- GENEROS MUSICBRAINZ -------------------------
                for genero in fila.get("generos_musicbrainz", "").split("|"):
                    genero = genero.strip()

                    if genero:
                        recurso_genero = registrar(
                            "genero", genero, genero, MUSIC.GeneroMusical
                        )
                        grafo.add((artista, MUSIC.tieneGenero, recurso_genero))

            # ------------------------- LANZAMIENTOS -------------------------
            lanzamiento = fila["release"].strip()

            if lanzamiento:
                clave = (str(artista) if artista is not None else track_id) + "|" + lanzamiento
                recurso_lanzamiento = registrar(
                    "lanzamiento", clave, lanzamiento, MUSIC.Lanzamiento
                )
                grafo.add((cancion, MUSIC.perteneceALanzamiento, recurso_lanzamiento))

            # ------------------------- GENEROS TAGTRAUM -------------------------
            for columna, propiedad in [
                ("genero_tagtraum", MUSIC.tieneGeneroPrincipal),
                ("genero_minoritario_tagtraum", MUSIC.tieneGeneroMinoritario),
            ]:
                genero = fila.get(columna, "").strip()

                if genero:
                    recurso_genero = registrar(
                        "genero", genero, genero, MUSIC.GeneroMusical
                    )
                    grafo.add((cancion, propiedad, recurso_genero))

            ambigua = fila.get("clasificacion_ambigua", "").strip().casefold()

            if ambigua in ("si", "sí", "no"):
                agregar_dato(
                    grafo, cancion, MUSIC.clasificacionAmbigua,
                    str(ambigua != "no").lower(), XSD.boolean
                )

            # ------------------------- PROCEDENCIA -------------------------
            fuentes_csv = fila.get("fuentes_integradas", "").lower()

            tiene_mb = (
                "musicbrainz" in fuentes_csv
                or fila.get("source", "").strip().lower() == "musicbrainz"
            )

            tiene_tagtraum = (
                "tagtraum" in fuentes_csv
                or bool(fila.get("genero_tagtraum", "").strip())
            )

            if tiene_mb:
                grafo.add((cancion, MUSIC.obtenidoDe, fuentes["musicbrainz"]))

                if artista is not None:
                    grafo.add((artista, MUSIC.obtenidoDe, fuentes["musicbrainz"]))

            if tiene_tagtraum:
                grafo.add((cancion, MUSIC.obtenidoDe, fuentes["tagtraum"]))

    # ------------------------- EXPORTAR -------------------------
    grafo.serialize(destination="instances.ttl", format="turtle")

    print("Archivo generado: instances.ttl")
    print("Canciones:", len(canciones))

    for tipo, nombre in [
        ("artista", "Artistas"),
        ("lanzamiento", "Lanzamientos"),
        ("genero", "Generos musicales"),
        ("lugar", "Lugares"),
    ]:
        print(nombre + ":", len(registrados[tipo]))

    print("Fuentes:", len(fuentes))
    print("Tripletas:", len(grafo))


# ------------- EJECUCION DEL PROGRAMA -------------
if __name__ == "__main__":
    generar_instancias()

