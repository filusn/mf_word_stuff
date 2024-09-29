from pathlib import Path

from flask import Flask, request
from flask_cors import CORS

from mf_word_stuff.utils.audio import extract_audio, transcribe_file

app = Flask(__name__)
CORS(app)

@app.route("/analyzeVideo", methods=["POST"])
def validate_address_in_db():
    data = request.json
    mp4 = data.get("url")
    extract_audio(Path(mp4))
    transcription = transcribe_file(Path(mp4).with_suffix('.wav'))
    return transcription.text


if __name__=='__main__':
    app.run(host='localhost', port=5000)