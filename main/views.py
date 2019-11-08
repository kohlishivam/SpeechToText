# Import libraries
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.files.storage import FileSystemStorage
import os
from pydub import AudioSegment
import speech_recognition as sr
from os import path
from .tasks import speech_to_text


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def upload(request):
	return render(request, 'main/index.html')


@csrf_exempt
def process_upload(request):
	# for audio files more than 1 minute in length, we have to process the file in the background
	if request.method == 'POST' and request.FILES['myfile']:
		myfile = request.FILES['myfile']
		fs = FileSystemStorage()
		filename = fs.save(myfile.name, myfile)
		uploaded_file_url = fs.url(filename)
		path_file = BASE_DIR + uploaded_file_url
		path_splitted = path_file.split(".")[-1]
		speech_to_text.delay(path_file)
		return HttpResponse("You will recieve an email")
	else:
		return render(request, 'main/index.html')


@csrf_exempt
def process_upload_1(request):
	# for audio files less than 1 minute in length
	if request.method == 'POST' and request.FILES['myfile']:
		myfile = request.FILES['myfile']
		fs = FileSystemStorage()
		filename = fs.save(myfile.name, myfile)
		uploaded_file_url = fs.url(filename)
		path_file = BASE_DIR + uploaded_file_url
		print(path_file)
		path_splitted= path_file.split(".")
		sound = AudioSegment.from_file(path_file, path_splitted[-1])
		sound.export(BASE_DIR + "/transcript.wav", format="wav")
		AUDIO_FILE = BASE_DIR + "/transcript.wav"
		r = sr.Recognizer()
		with sr.AudioFile(AUDIO_FILE) as source:
				audio = r.record(source)  # read the entire audio file   
				return HttpResponse("Transcription: " + r.recognize_google(audio))
	else:
		return render(request, 'main/index.html')
