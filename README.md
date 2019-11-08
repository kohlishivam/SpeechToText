# Speech to text using Google API and Celery

A Django application that handles audio file upload and extracts the speech from the audio file and finally converts it into Text.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install -r requirements.txt
```

## Running

First we need to run the redis server
```terminal
$ redis-server
```
Now, we will run the celery server
```terminal
$ celery -A SpeechToTextMicroservice worker -l info
```
Finally, run the Django server
```terminal
$ python3 manage.py makemigrations
$ python3 manage.py migrate
$ python3 manage.py runserver
```
