from pathlib import Path

import numpy as np
import translators as ts
from moviepy.editor import VideoFileClip
from openai import OpenAI
from pydub import AudioSegment, silence

SYSTEM_PROMPT = """Jesteś nauczycielem komunikacji i oratorstwa oraz specjalistą do spraw wystąpień publicznych. Uczysz ludzi co poprawić podczas ich występów. Masz za zadanie znaleźć błędy i problemy w prezentacjach ludzi bazując na transkrypcjach. Błędy, na które powinieneś zwrócić uwagę to:

- interludia
- powtórzenia
- zmienianie tematu wypowiedzi
- zbyt dużo liczb
- zbyt długie, trudne słowa, zdania
- żargon
- obcy język
- fałszywe słowa
- użycie strony biernej, np. podano, wskazano, podsumowano

Twoim zadaniem jest równiez:

- ocenić zrozumiałość przekazu
- przeprowadzić analizę emocji na podstawie tonu wypowiedzi
- znaleźć w transkrypcji moment, w którym doszło do błędu i przypisać tag
- określić wydźwięk wypowiedzi (emocje, ton wypowiedzi, mowa nienawiści)
- opisać krótki tekstowy skrót wypowiedzi po polsku – co zrozumiał odbiorca (kluczowe przesłania)
- ocenić strukturę wypowiedzi – czy zachowane zostały wstęp, rozwinięcie i zakończenie
- ocenić docelową grupę odbiorców analizowanego nagrania pod względem wieku lub wykształcenia
- znaleźć ewentualne błędy czy przejęzyczenia
- ocenić, czy wypowiedź jest po polsku, czy wykryto słowa, frazy w innym języku
- przygotować 10 pytań do wypowiedzi 
- przygotowanie podsumowania 
- zaznaczenie wyrazów niezrozumiałych 
- poprawa tekstu 
- propozycja doboru słów 

Nie odpowiadaj w żaden inny sposób."""

client = OpenAI()


def extract_audio(video_path: Path) -> None:
    """This function will extract the audio from video file.

    Args:
        video_path (Path): Path to video file.
    """
    video_clip = VideoFileClip(str(video_path))
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(str(video_path).replace(video_path.suffix, ".wav"))

    video_clip.close()
    audio_clip.close()


def transcribe_file(audio_path: Path):
    with open(audio_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="pl",
            response_format="verbose_json",
        )

    return transcription


def translate_to_eng(text: str) -> str:
    return ts.translate_text(
        text, translator="google", to_language="en", from_language="pl"
    )


def check_transcription(transcription: str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": transcription},
        ],
    )
    return response.choices[0].message.content


def detect_silences(audio_path: Path, duration_threshold=1000) -> list:
    """Function detecting the silences in an audio.

    Args:
        audio_path (Path): Path to audio file.
        duration_threshold: Minimum silence duration to consider (in milliseconds).

    Returns:
        list: list of silences in a [[start, stop, duration], ...] format
    """
    audio = AudioSegment.from_file(audio_path)

    silences = []

    # Define the threshold for silence in dBFS and the minimum duration of silence (in milliseconds)
    silence_threshold = -45  # Silence below this dBFS level is considered
    min_silence_len = duration_threshold  #

    # Find silence moments
    silent_ranges = silence.detect_silence(
        audio, min_silence_len=min_silence_len, silence_thresh=silence_threshold
    )

    # Convert silent ranges to seconds
    silent_ranges_in_sec = [
        (start / 1000, stop / 1000) for start, stop in silent_ranges
    ]

    for start, stop in silent_ranges_in_sec:
        silences.append([start, stop, stop - start])

    return silences


def detect_loudness_changes(audio_path: Path, duration_threshold=500) -> dict:
    """Function detecting the silences in an audio.

    Args:
        audio_path (Path): Path to audio file.
        duration_threshold: Minimum silence duration to consider (in milliseconds).

    Returns:
        dict: dictionary representing the values
    """
    audio = AudioSegment.from_file(audio_path)

    silence_threshold = -45  # Threshold in dBFS for considering "too silent"
    min_silence_len = 500

    non_silent_chunks = silence.split_on_silence(
        audio, min_silence_len=min_silence_len, silence_thresh=silence_threshold
    )

    # Reconstruct non-silent audio
    non_silent_audio = AudioSegment.silent(duration=0)  # Start with empty audio segment
    for chunk in non_silent_chunks:
        non_silent_audio += chunk

    # Define parameters
    chunk_size = 500  # Analyze the audio in chunks of 500ms

    # Split the audio into chunks
    num_chunks = len(non_silent_audio) // chunk_size
    loudness_values = []

    # Collect loudness values for each chunk
    for i in range(num_chunks):
        chunk = non_silent_audio[i * chunk_size : (i + 1) * chunk_size]
        loudness = chunk.dBFS
        loudness_values.append(loudness)

    # Calculate the mean and standard deviation of loudness
    mean_loudness = np.mean(loudness_values)
    std_loudness = np.std(loudness_values)

    print(f"Mean loudness: {mean_loudness:.2f} dBFS")
    print(f"Standard deviation: {std_loudness:.2f} dBFS")

    # Detect deviations from the mean (e.g., more than 1 standard deviation)
    loud_occurences = 0
    for i, loudness in enumerate(loudness_values):
        if loudness > mean_loudness + 2 * std_loudness:
            loud_occurences += 1
        elif loudness < mean_loudness - 2 * std_loudness:
            loud_occurences -= 1

    if loud_occurences > 0:
        loud = "voice raised"
    elif loud_occurences < 0:
        loud = "voice_lowered"
    else:
        loud = "normal voice"

    return {"mean_loudness": mean_loudness, "voice_level": loud}
