import os
import moviepy.editor as mp
from google.cloud import storage
from google.cloud import speech_v1p1beta1 as speech

def uploadAudio(file, fileFormat, credentialsPath, bucketName):
    # Load credentials in enviromental variable
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentialsPath

    # Connect to the bucket
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucketName)
    blob = bucket.blob('tempAudio.mp3')
    
    # Transform video to audio
    if fileFormat:
        # If file is video
        clip = mp.VideoFileClip(file)
        clip.audio.write_audiofile(r"tempAudio.mp3")
    else:
        # If file is audio
        clip = mp.AudioFileClip(file)
        clip.write_audiofile(r"tempAudio.mp3")
    
    # Upload audio to bucket
    blob.upload_from_filename('tempAudio.mp3')
    
    # Delete audio file
    os.remove(r"tempAudio.mp3")
    
def transcribeAudio(bucketName):
    """Asynchronously transcribes the audio file specified by the gcs_uri."""
    gcs_uri = 'gs://' + bucketName + '/tempAudio.mp3'
    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig( 
        language_code = 'es-ES',
        enable_speaker_diarization=True,
        diarization_speaker_count=2,
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        enable_automatic_punctuation=True,
        sample_rate_hertz=16000)

    response = client.long_running_recognize(config=config, audio=audio)

    result = response.result().results[-1]

    words_info = result.alternatives[0].words

    # Printing out the output:
    transcription = []
    curr_s = 0
    curr_t = ''
    for word_info in words_info:
        word_info.word, word_info.speaker_tag
        if curr_s != word_info.speaker_tag:
            transcription.append(curr_t)
            curr_s = word_info.speaker_tag
            curr_t = str(word_info.speaker_tag) + ': ' + word_info.word
        else:
            curr_t = curr_t + ' ' + word_info.word
    transcription.append(curr_t)
    
    # Connect to the bucket
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucketName)
    blob = bucket.blob('tempAudio.mp3')
    blob.delete()
    return transcription