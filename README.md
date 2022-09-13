# TFG 2021-2022 Extracción de recuerdos de videos

En este repositorio se encuentra el código del Trabajo de Fin de Grado **Extracción de recuerdos de videos** de la Universidad Complutense de Madrid, realizado por Hugo García González y dirigido por Alberto Díaz Esteban.

Los archivos principales **main.py**, **graph_queries.py**, **graph_queries_aux.py**, **transcribe.py** y **gui_aux.py** son el código fuente del sistema creado en este trabajo.

El directorio **Version_Google_Colab** contiene una versión del sistema implementado en un notebook para ser ejecutado en Google Colab.

El directorio **Archivos_Ejemplo** contiene un ejemplo de archivo de guión de entrevista.

El directorio **Configs** contiene la configuración de la libreria Grafeno.

Los directorios **Grafeno** y **Version_Google_Colab/Grafeno** contienen una versión modificada de la librería de python Grafeno creada por Antonio F. G. Sevilla. Para consultar el fork de la versión modicada acceda al siguiente repositiorio: 
https://github.com/Hugarc02/grafeno-TFG-2022

## Instrucciones de instalación

1. Instalar las librerias definidas en **requirements.txt**. ```pip install requirements.txt```

2. Instalar complementos necesarios usando los siguientes comandos.

```pip install --upgrade google-cloud-speech```
```python -m spacy download es_core_news_lg```
```python -m spacy download es_dep_news_trf```
```python -m nltk.downloader wordnet_ic```
```python -m nltk.downloader omw-1.4```
```python -m nltk.downloader wordnet```

3. Descargar repositiorio completo en un directorio.

4. Ejecutar **main.py** desde ese directorio. ```python main.py```

## Google Cloud Speech-to-text API

Para usar la **transcripción automática**, es necesario habilitar la transcripción asíncrona de Google Cloud. Los pasos son los siguientes:

* Registrarse en Google Cloud
* Crear proyecto en Google Cloud
* Habilitar la API Google Speech to Text
* Crear cuenta de servicio con rol "Administrador de almacenamiento"
* Crear y descargar clave JSON de la cuenta de servicio
* Crear bucket de almacenamiento en Google Cloud Storage

En el sistema habrá que seleccionar las ruta al JSON de la clave de cuenta de servicio, y insertar el nombre del bucket de Google Cloud Storage.

## Base de datos Neo4j

Para almacenar el resultado en una base de datos Neo4j, es necesario tener una base de datos de Neo4j desktop o Neo4j sandbox activa. En el sistema habra que insertar la uri de la base de datos, el usuario y la contraseña.

Ejemplos de formato de uri: ```bolt://localhost:XXXX```, ```bolt://XX.XXX.XX.XXX:XXXX``` 

## Version Google Colab

Para usar el sistema en Google Colab, descargar los archivos de el directiorio **Version_Google_Colab** en Google Drive, y abrir **colab_ver.ipynb**.


