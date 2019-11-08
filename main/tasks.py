# Import libraries
from __future__ import absolute_import
from celery import task
from celery import Celery
from pydub import AudioSegment
import io
import os
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import wave
from google.cloud import storage
from django.core.mail import send_mail
from django.conf import settings
import subprocess


app = Celery('SpeechToTextMicroservice')
app.config_from_object('django.conf:settings')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTFILE_PATH = BASE_DIR+"/Transcripts/" #Final transcript path
BUCKET_NAME = "sgpost-img-upload" #Name of the bucket


def mp3_to_wav(audio_file_name):
	if audio_file_name.split('.')[1] == 'mp3': 
		sound = AudioSegment.from_mp3(audio_file_name)
		audio_file_name = audio_file_name.split('.')[0] + '.wav'
		sound.export(audio_file_name, format="wav")


def stereo_to_mono(audio_file_name):
	sound = AudioSegment.from_wav(audio_file_name)
	sound = sound.set_channels(1)
	sound.export(audio_file_name, format="wav")


def frame_rate_channel(audio_file_name):
	with wave.open(audio_file_name, "rb") as wave_file:
		frame_rate = wave_file.getframerate()
		channels = wave_file.getnchannels()
		return frame_rate,channels


def upload_blob(bucket_name, source_file_name, destination_blob_name):
	"""Uploads a file to the bucket."""
	storage_client = storage.Client()
	bucket = storage_client.get_bucket(bucket_name)
	blob = bucket.blob(destination_blob_name)
	blob.upload_from_filename(source_file_name)


def delete_blob(bucket_name, blob_name):
	"""Deletes a blob from the bucket."""
	storage_client = storage.Client()
	bucket = storage_client.get_bucket(bucket_name)
	blob = bucket.blob(blob_name)
	blob.delete()


def google_transcribe(audio_file_name,filepath):
	file_name = filepath + audio_file_name
	mp3_to_wav(file_name)
	# The name of the audio file to transcribe
	frame_rate, channels = frame_rate_channel(file_name)
	if channels > 1:
		stereo_to_mono(file_name)
	bucket_name = BUCKET_NAME
	source_file_name = filepath + audio_file_name
	destination_blob_name = audio_file_name
	upload_blob(bucket_name, source_file_name, destination_blob_name)
	gcs_uri = 'gs://' + BUCKET_NAME + '/' + audio_file_name
	transcript = ''
	client = speech.SpeechClient()
	audio = types.RecognitionAudio(uri=gcs_uri)
	config = types.RecognitionConfig(
	encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
	sample_rate_hertz=frame_rate,
	language_code='en-US')
	# Detects speech in the audio file
	operation = client.long_running_recognize(config, audio)
	response = operation.result(timeout=10000)
	for result in response.results:
		transcript += result.alternatives[0].transcript
	delete_blob(bucket_name, destination_blob_name)
	return transcript


def write_transcripts(transcript_filename,transcript):
	"""We can send an email with the text or upload the file on 
	google drive and send the link.
	Currently the file is being just saved and the code 
	to send the email is configured."""
	f = open(OUTPUTFILE_PATH + transcript_filename,"w+")
	f.write(transcript)
	f.close()
	# subject = 'Thank you'
	# message = 'Working fine'
	# email_from = settings.EMAIL_HOST_USER
	# recipient_list = ['kohlishivam5522@gmail.com',]
	# send_mail( subject, message, email_from, recipient_list )


@app.task(name='sppech_to_text')
def speech_to_text(path_file):
	audio_file_name = path_file.split("/")[-1]
	filepath = path_file.replace(audio_file_name,"")
	transcript = google_transcribe(audio_file_name,filepath)
	transcript_filename = audio_file_name.split('.')[0] + '.txt'
	write_transcripts(transcript_filename,transcript)
	print("Success")
