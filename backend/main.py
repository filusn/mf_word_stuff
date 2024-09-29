import sqlite3

from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

from mf_word_stuff.utils.audio import extract_audio, transcribe_file
from safe_shopping.safe_shopping.backend.markers.registration_date import registration_date
from safe_shopping.safe_shopping.backend.markers.ssl_certificate import ssl_certificate

app = Flask(__name__)
CORS(app)

@app.route("/hello", methods=["POST"])
def hello():
    data = request.json
    greet = data.get('greet')
    return jsonify("hello")

@app.route("/calculateSiteMarkers", methods=["POST"])
def calculate_site_markers():
    results = {}

    data = request.json
    url = data.get("url")
    markers = [
        ssl_certificate,
        registration_date
    ]

    # Check url vs each marker
    for marker_func in markers:
        func_name = marker_func.__name__
        try:
            results[func_name] = marker_func(url)
        except Exception as e:
            results[func_name] = False

    return jsonify(results)


@app.route("/analyzeVideo", methods=["POST"])
def validate_address_in_db():
    data = request.json
    mp4 = data.get("url")
    extract_audio(Path(mp4))
    transcription = transcribe_file(Path(mp4).with_suffix('.wav'))
    return transcription.text

def is_site_blacklisted(url_to_check):
    # TODO: get it from DB
    blacklisted_sites = ['https://allegro.pl/']
    return url_to_check.lower() in [site.lower() for site in blacklisted_sites]

@app.route('/check_site', methods=['POST'])
def check_site():
    data = request.get_json()
    url_to_check = data.get('url')
    if not url_to_check:
        return jsonify({'error': 'No URL provided'})

    is_listed = is_site_blacklisted(url_to_check)
    return jsonify({'url': url_to_check, 'is_listed': is_listed})


if __name__=='__main__':
    app.run(host='localhost', port=5000)