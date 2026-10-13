# Proyecto – Etapa 2 de Web Semántica (MISIS)

## 1. Requisitos

- Python 3 y Docker Desktop.
- Git y Git LFS (para descargar `instances.ttl`, que supera los 100 MB).
- Biblioteca RDFLib.

## 2. Descargar el proyecto

En una terminal, ejecutar:

- git lfs install
- git clone https://github.com/DanielRivera10000/Proyecto--Etapa-1-Semantic-Web-MISIS-.git
- cd Proyecto--Etapa-1-Semantic-Web-MISIS-
- git lfs pull
- python -m pip install rdflib

Es necesario tener GIT LFS para poder descargar las instancias debido a su peso.

## 3. Generar la ontología y las instancias

Los archivos `ontology.ttl` e `instances.ttl` ya estan incluidos. Para volver a genrarlos, se realizan los siguientes comandos.

- python Src/generacion_ontologia.py
- python Src/generacion_instancias.py

El segundo programa utiliza `Resultados/canciones_enriquecidas_final.csv`. Si se desea reconstruir los datos enriquecidos. Realizar los sigueintes comandos

- python Src/consultar_musicbrainz.py --limite 5 (Escoges)
- python Src/generacion_datos.py
- python Src/consultar_tagtraum.py
- python Src/generacion_instancias.py

## 4. Iniciar Fuseki

Abrir Docker Desktop y ejecutar:

```powershell
docker compose up -d
```

Para detern Fuseki

```powershell
docker compose down
```

Abrir **http://localhost:3030**. El usuario es `admin` y la contraseña local está configurada en `docker-compose.yml` (`proyecto1`).

En la interfaz de Fuseki:

1. Entrar a `Manage datasets` → `Add new dataset`.
2. Crear el dataset `musica` (preferiblemente con almacenamiento `TDB2`).
3. Abrir el dataset y seleccionar `Add data`.
4. Subir `ontology.ttl` y después `instances.ttl`.
5. Entrar a `Query` para ejecutar las consultas.

## 5. Ejecutar las consultas SPARQL

Las cinco consultas están en `Consultas/consultas.sparql`

1. Abrir el archivo de consultas.
2. Copiar una consulta a la vez.
3. Pegarla en la pestaña `Query` del dataset `musica` y ejecutarla.
4. Comparar los resultados con `Resultados Consultas.pdf`.