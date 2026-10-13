from rdflib import Graph, Namespace, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD

from rdflib.collection import Collection



# ------------- URL -------------
MUSIC = Namespace("https://github.com/DanielRivera10000/Proyecto--Etapa-1-Semantic-Web-MISIS-/ontology#")

# ------------------------- GENERAR ONTOLOGIA -------------------------
def generar_ontologia():
    grafo = Graph()
    grafo.bind("music", MUSIC)

    # ------------------------- CLASES -------------------------
    clases = [
        ("Cancion", "Canción", "Pista musical identificada por un track_id."),
        ("Artista", "Artista", "Persona o grupo que interpreta una canción."),
        ("Lanzamiento", "Lanzamiento", "Publicación a la que pertenece una canción."),
        ("GeneroMusical", "Género musical", "Categoría musical que se usa para clasificar una canción."),
        ("Lugar", "Lugar", "País o región registrado para un artista."),
        ("Fuente", "Fuente", "Origen de los datos usados."),
        ("Grupo", "Grupo", "Artista identficado como un grupo musical de individuos."),
        ("Persona", "Persona", "Artista identificado como una persona individual."),
    ]

    for nombre, etiqueta, descripcion in clases:
        clase = MUSIC[nombre]
        grafo.add((clase, RDF.type, OWL.Class))
        grafo.add((clase, RDFS.label, Literal(etiqueta, lang="es")))
        grafo.add((clase, RDFS.comment, Literal(descripcion, lang="es")))

    # Jerarquia de artistas
    grafo.add((MUSIC.Grupo, RDFS.subClassOf, MUSIC.Artista))
    grafo.add((MUSIC.Persona, RDFS.subClassOf, MUSIC.Artista))

    # ------------------------- PROPIEDADES DE OBJETO -------------------------
    propiedades_objeto = [
        ("interpretadoPor", "interpretado por", "Relaciona una canción con su artista.", MUSIC.Cancion, MUSIC.Artista),
        ("perteneceALanzamiento", "pertenece a lanzamiento", "Relaciona una canción con su lanzamiento.", MUSIC.Cancion, MUSIC.Lanzamiento),
        ("tieneGenero", "tiene género", "Relaciona un artista con un género musical.", MUSIC.Artista, MUSIC.GeneroMusical),
        ("asociadoALugar", "asociado a lugar", "Relaciona un artista con su país o región.", MUSIC.Artista, MUSIC.Lugar),
        ("tieneGeneroPrincipal", "tiene género principal", "Relaciona una canción con su género principal.", MUSIC.Cancion, MUSIC.GeneroMusical),
        ("tieneGeneroMinoritario", "tiene género minoritario", "Relaciona una canción con su género minoritario.", MUSIC.Cancion, MUSIC.GeneroMusical),
        ("obtenidoDe", "obtenido de", "Relaciona una canción o un artista con su fuente de información.", None, MUSIC.Fuente),
    ]

    for nombre, etiqueta, descripcion, dominio, rango in propiedades_objeto:
        propiedad = MUSIC[nombre]
        grafo.add((propiedad, RDF.type, OWL.ObjectProperty))
        grafo.add((propiedad, RDFS.label, Literal(etiqueta, lang="es")))
        grafo.add((propiedad, RDFS.comment, Literal(descripcion, lang="es")))

        if dominio is not None:
            grafo.add((propiedad, RDFS.domain, dominio))

        grafo.add((propiedad, RDFS.range, rango))

    # ------------------------- PROPIEDADES DE DATOS -------------------------
    propiedades_datos = [
        ("track_id", "identificador de pista", "Identificador de la canción en el dataset.", MUSIC.Cancion, XSD.string),
        ("titulo", "título", "Título de la canción.", MUSIC.Cancion, XSD.string),
        ("anio", "año", "Año de la canción.", MUSIC.Cancion, XSD.integer),
        ("duracion", "duración", "Duración de la canción en segundos.", MUSIC.Cancion, XSD.decimal),
        ("clasificacionAmbigua", "clasificación ambigua", "Indica si el genero de la canción es ambiguo.", MUSIC.Cancion, XSD.boolean),
        ("mbid_artista", "identificador MusicBrainz", "Identificador MusicBrainz del artista.", MUSIC.Artista, XSD.string),
        ("nombre_artista", "nombre del artista", "Nombre original del artista.", MUSIC.Artista, XSD.string),
        ("nombre_musicbrainz", "nombre en MusicBrainz", "Nombre del artista en MusicBrainz.", MUSIC.Artista, XSD.string),
        ("nombre", "nombre", "Nombre de un género, lugar, lanzamiento o fuente.", None, XSD.string),
        ("url", "URL", "Dirección web de la fuente.", MUSIC.Fuente, XSD.anyURI),
        ("fecha_formacion", "fecha de formación", "Fecha de creación del grupo.", MUSIC.Grupo, XSD.string),
        ("fecha_nacimiento", "fecha de nacimiento", "Fecha de nacimiento del artista.", MUSIC.Persona, XSD.string),
    ]

    for nombre, etiqueta, descripcion, dominio, rango in propiedades_datos:
        propiedad = MUSIC[nombre]
        grafo.add((propiedad, RDF.type, OWL.DatatypeProperty))
        grafo.add((propiedad, RDFS.label, Literal(etiqueta, lang="es")))
        grafo.add((propiedad, RDFS.comment, Literal(descripcion, lang="es")))

        if dominio is not None:
            grafo.add((propiedad, RDFS.domain, dominio))

        grafo.add((propiedad, RDFS.range, rango))



    # ------------------------- AXIOMAS OWL -------------------------

    # Propiedades Nuevas
    propiedades_nuevas = [
        (MUSIC.interpreta, "interpreta", "Relaciona un artista con la canción que interpreta.", MUSIC.Artista, MUSIC.Cancion),
        (MUSIC.contieneCancion, "contiene canción", "Relaciona un lanzamiento con una canción.", MUSIC.Lanzamiento, MUSIC.Cancion),
        (MUSIC.tieneMismoTituloQue, "tiene el mismo título que", "Relaciona canciones que comparten título.", MUSIC.Cancion, MUSIC.Cancion),
    ]

    for propiedad, etiqueta, descripcion, dominio, rango in propiedades_nuevas:
        grafo.add((propiedad, RDF.type, OWL.ObjectProperty))
        grafo.add((propiedad, RDFS.label, Literal(etiqueta, lang="es")))
        grafo.add((propiedad, RDFS.comment, Literal(descripcion, lang="es")))
        grafo.add((propiedad, RDFS.domain, dominio))
        grafo.add((propiedad, RDFS.range, rango))

    # Clases Nuevas
    grafo.add((MUSIC.CancionClasificada, RDF.type, OWL.Class))
    grafo.add((MUSIC.CancionClasificada, RDFS.label, Literal("Canción clasificada", lang="es")))
    grafo.add((MUSIC.CancionClasificada, RDFS.comment, Literal(
        "Canción que tiene al menos un género principal.", lang="es"
    )))

    # Axioma 1 - Cancion y Artista son disjuntas
    grafo.add((MUSIC.Cancion, OWL.disjointWith, MUSIC.Artista))

    # Axioma 2 - Persona y Grupo son disjuntas
    grafo.add((MUSIC.Persona, OWL.disjointWith, MUSIC.Grupo))

    # Axioma 3 - Propiedades inversas
    grafo.add((MUSIC.interpretadoPor, OWL.inverseOf, MUSIC.interpreta))

    # Axioma 4 - Propiedades inversas
    grafo.add((MUSIC.perteneceALanzamiento, OWL.inverseOf, MUSIC.contieneCancion))

    # Axioma 5 - Propiedad simetrica
    grafo.add((MUSIC.tieneMismoTituloQue, RDF.type, OWL.SymmetricProperty))

    # Axioma 6 - Propiedad funcional
    grafo.add((MUSIC.duracion, RDF.type, OWL.FunctionalProperty))

    # Axioma 7 - Cada cancion tiene exactamente un track_id
    restriccion_id = BNode()

    grafo.add((restriccion_id, RDF.type, OWL.Restriction))
    grafo.add((restriccion_id, OWL.onProperty, MUSIC.track_id))
    grafo.add((restriccion_id, OWL.cardinality, Literal(1, datatype=XSD.nonNegativeInteger)))
    grafo.add((MUSIC.Cancion, RDFS.subClassOf, restriccion_id))

    # Axioma 8 - Definicion de CancionClasificada
    restriccion_genero = BNode()

    grafo.add((restriccion_genero, RDF.type, OWL.Restriction))
    grafo.add((restriccion_genero, OWL.onProperty, MUSIC.tieneGeneroPrincipal))
    grafo.add((restriccion_genero, OWL.someValuesFrom, MUSIC.GeneroMusical))

    interseccion = BNode()

    grafo.add((interseccion, RDF.type, OWL.Class))
    grafo.add((interseccion, OWL.intersectionOf,
               Collection(grafo, BNode(), [MUSIC.Cancion, restriccion_genero]).uri))
    grafo.add((MUSIC.CancionClasificada, OWL.equivalentClass, interseccion))


    # ------------------------- EXPORTAR -------------------------
    grafo.serialize(destination="ontology.ttl", format="turtle")

    print("Archivo generado: ontology.ttl")
    print("Tripletas:", len(grafo))


# ------------- EJECUCION DEL PROGRAMA -------------
if __name__ == "__main__":
    generar_ontologia()

