import os
import moviepy.editor as mp
from google.cloud import storage
from google.cloud import speech_v1p1beta1 as speech
from pydub import AudioSegment, effects, scipy_effects

def normalizar(source_file):
    #logging.info(messages.INFO_STAGE_NORMALIZAR.value)
    sound = AudioSegment.from_wav(source_file)
    sound = scipy_effects.band_pass_filter(sound, 200, 3100)
    sound = sound.set_channels(1)
    sound = effects.normalize(sound)
    sound.export(source_file, format = 'wav')
    print('fin normalizacion')

def uploadAudio(file, fileFormat, credentialsPath, bucketName):
    # Load credentials in enviromental variable
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentialsPath

    # Connect to the bucket
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucketName)
    blob = bucket.blob('tempAudio.wav')
    
    # Transform video to audio
    if fileFormat:
        # If file is video
        clip = mp.VideoFileClip(file)
        clip.audio.write_audiofile(r"tempAudio.wav")
    else:
        # If file is audio
        clip = mp.AudioFileClip(file)
        clip.write_audiofile(r"tempAudio.wav")
    
    # Normalize audio
    audio = AudioSegment.from_wav(r"tempAudio.wav")
    audio = scipy_effects.band_pass_filter(audio, 200, 3100)
    audio = audio.set_channels(1)
    audio = effects.normalize(audio)
    audio.export(r"tempAudio.wav", format = 'wav')
    # Upload audio to bucket
    blob.upload_from_filename('tempAudio.wav')
    
    # Delete audio file
    os.remove(r"tempAudio.wav")
    
def transcribeAudio(bucketName):
    """Asynchronously transcribes the audio file specified by the gcs_uri."""
    gcs_uri = 'gs://' + bucketName + '/tempAudio.wav'
    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig( 
        language_code = 'es-ES',
        enable_speaker_diarization=True,
        diarization_speaker_count=2,
        #encoding=speech.RecognitionConfig.AudioEncoding.WAV,
        enable_automatic_punctuation=True,
        #sample_rate_hertz=16000
        )

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
            curr_t = word_info.word
        else:
            curr_t = curr_t + ' ' + word_info.word
    transcription.append(curr_t)
    
    # Connect to the bucket
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucketName)
    blob = bucket.blob('tempAudio.wav')
    blob.delete()
    return transcription