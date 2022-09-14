import os

def errorsAutomaticTranscription(file, fileFormat, key, bucket):
    accepted_video_extensions = {'.mp4', '.mkv', '.ogv','.webm','.avi','.mov'}
    accepted_audio_extensions = {'.ogg', '.mp3', '.wav','.m4a'}
    if file == '':
        raise ValueError('El path del archivo esta sin completar')
    elif fileFormat and os.path.splitext(file)[1].lower() not in accepted_video_extensions:
        raise ValueError('Formato de video no válido. Formatos aceptados: mp4, mkv, ogv, webm, avi, mov')
    elif not fileFormat and os.path.splitext(file)[1].lower() not in accepted_audio_extensions:
        raise ValueError('Formato de audio no válido. Formatos aceptados: ogg, mp3, wav, p4a')
    elif key == '':
        raise ValueError('El path de la clave de cuenta de servicio esta sin completar')
    elif os.path.splitext(key)[1].lower() != '.json':
        raise ValueError('La clave de cuenta de servicio debe ser un archivo de tipo json')
    elif bucket == '':
        raise ValueError('El nombre del bucket esta sin completar')

def errorsManualTranscription(text):
    if text == '':
        raise ValueError('La transcripción manual esta sin completar')

def errorsGraphGeneration(script):
    if script == '':
        raise ValueError('El guion esta sin completar')
    elif os.path.splitext(script)[1].lower() != '.json':
        raise ValueError('El guion debe ser un archivo de tipo json')

def errorNeo4j(user, pwd, port):
    if user == '':
        raise ValueError('El usuario de Neo4j esta sin completar')
    elif pwd == '':
        raise ValueError('La contraseña de Neo4j esta sin completar')
    elif port == '':
        raise ValueError('El puerto de Neo4j esta sin completar')

ayuda = '''
Formatos de video aceptados: mp4, mkv, ogv, webm, avi, mov

Formatos de audio aceptados: ogg, mp3, wav, p4a

Clave de cuenta de servicio: debe tener permisos en Google Cloud Storage

Nombre bucket: Nombre del bucket de Google Cloud Storage 

Para más información acceder a https://github.com/Hugarc02/TFG2022ExtraccionRecuerdos
'''