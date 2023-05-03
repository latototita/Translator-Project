import os
import json
import speech_recognition as sr
from langdetect import detect
from translate import Translator
from bottle import route, run, template
@route('/')
def index():
    return template('index')
@route('/submit', method='POST')
def submit():
    # Retrieve the audio file from the form
    audio_file = request.files.get('audio')

    # Create a speech recognition object
    r = sr.Recognizer()

    # Convert audio to text
    try:
        with sr.AudioFile(audio_file.file) as source:
            audio = r.record(source)
        text = r.recognize_sphinx(audio)
    except Exception as e:
        text = ''
        print(e)

    # Detect the language of the text
    lang = detect(text)

    # Translate the text to the default language
    default_lang = 'en'
    if lang != default_lang:
        translator = Translator(from_lang=lang, to_lang=default_lang)
        translated_text = translator.translate(text)
    else:
        translated_text = text

    # Translate the text to the other user's language
    other_user_lang = 'fr'
    if default_lang != other_user_lang:
        translator = Translator(from_lang=default_lang, to_lang=other_user_lang)
        translated_text = translator.translate(translated_text)
    else:
        translated_text = translated_text

    # Use the translated text to look up the appropriate response in the dataset
    if other_user_lang in translations and translated_text in translations[other_user_lang]:
        response = translations[other_user_lang][translated_text]
    else:
        response = "I'm sorry, I don't understand."

    # Render the response
    return template('response', response=response)
if __name__ == '__main__':
    # Set the path to the dataset folder
    DATASET_PATH = 'path/to/dataset/folder'

    # Load the translation dataset for each language
    translations = {}
    for lang_code in os.listdir(DATASET_PATH):
        with open(os.path.join(DATASET_PATH, lang_code), 'r', encoding='utf-8') as f:
            translations[lang_code] = json.load(f)

    # Run the app
    run(host='localhost', port=8080)
