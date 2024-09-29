from pathlib import Path

import translators as ts
from moviepy.editor import VideoFileClip
from openai import OpenAI

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

api_key = ""
client = OpenAI(api_key=api_key)


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


if __name__ == "__main__":
    extract_audio("data/HY_2024_film_01.mp4")
    transcription = transcribe_file("data/HY_2024_film_01.wav")
    print(transcription)
