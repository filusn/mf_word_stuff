from pathlib import Path

from flask import Flask, request
from flask_cors import CORS

from mf_word_stuff.utils.audio import extract_audio, transcribe_file, translate_to_eng

app = Flask(__name__)
CORS(app)

@app.route("/analyzeVideo", methods=["POST"])
def analyze_video():
    data = request.json
    mp4 = data.get("url")
    extract_audio(Path(mp4))
    transcription = transcribe_file(Path(mp4).with_suffix('.wav'))
    return transcription.text

@app.route("/translateVideo", methods=["POST"])
def translate_video():
    data = request.json
    text = data.get("text")
    transcription = translate_to_eng(text)
    return transcription


@app.route("/translateVideo", methods=["POST"])
def detect_silences():
    data = request.json
    text = data.get("text")
    transcription = translate_to_eng(text)
    return transcription


if __name__=='__main__':
    app.run(host='localhost', port=5000)