import difflib
from pathlib import Path

import cv2
import easyocr
import mediapipe as mp
import nltk
import numpy as np
from deepface import DeepFace
from nltk.tokenize import sent_tokenize

# TODO: Remove this ugly thing :(
from utils.metrics import *


def setup_models():
    nltk.download("punkt_tab")
    easyocr.Reader(["pl"])


def recognize_emotions(img_rgb: np.array) -> list:
    """This function detects faces, recognizes emotions, age, gender and race
    of people in an image. Ignores spoofed faces.

    Args:
        img_rgb (np.array): Image in RGB format.

    Returns:
        list: list in the form:
            [{'age': 40,
            'region': {'x': 142,
            'y': 102,
            'w': 266,
            'h': 266,
            'left_eye': None,
            'right_eye': None},
            'face_confidence': 0.89,
            'gender': {'Woman': 88.8154923915863, 'Man': 11.184508353471756},
            'dominant_gender': 'Woman',
            'race': {'asian': 0.6278438959270716,
            'indian': 1.7700599506497383,
            'black': 0.28826487250626087,
            'white': 49.327221512794495,
            'middle eastern': 21.63582593202591,
            'latino hispanic': 26.350781321525574},
            'dominant_race': 'white',
            'emotion': {'angry': 15.988580882549286,
            'disgust': 0.002835433042491786,
            'fear': 23.031800985336304,
            'happy': 1.6180532053112984,
            'sad': 27.11198925971985,
            'surprise': 2.6565074920654297,
            'neutral': 29.59023416042328},
            'dominant_emotion': 'neutral'}]
    """
    try:
        result = DeepFace.analyze(
            img_path=img_rgb,
            actions=["age", "gender", "race", "emotion"],
            anti_spoofing=True,
        )
    except ValueError:
        result = []

    return result


BaseOptions = mp.tasks.BaseOptions
ObjectDetector = mp.tasks.vision.ObjectDetector
ObjectDetectorOptions = mp.tasks.vision.ObjectDetectorOptions
VisionRunningMode = mp.tasks.vision.RunningMode

PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions

detector_options = ObjectDetectorOptions(
    base_options=BaseOptions(model_asset_path="efficientdet_lite0.tflite"),
    max_results=5,
    running_mode=VisionRunningMode.VIDEO,
    category_allowlist=["person"],
    score_threshold=0.5,
)

pose_landmarker_options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path="pose_landmarker_lite.task"),
    running_mode=VisionRunningMode.VIDEO,
)


def detect_people_video(video_path: Path):
    # bboxes: [[x, y, w, h]]
    detection_results = {
        "frame_idxes": [],
        "timestamps": [],
        "number_of_detections": [],
        "bboxes": [],
    }

    with ObjectDetector.create_from_options(detector_options) as detector:
        cap = cv2.VideoCapture(video_path)
        frame_rate = cap.get(cv2.CAP_PROP_FPS)

        frame_index = 0

        while cap.isOpened():
            ret, frame = cap.read()

            if not ret:
                print("Unable to capture video")
                break

            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)

            # Calculate the timestamp of the current frame
            frame_timestamp_ms = int(1000 * frame_index / frame_rate)
            frame_index += 1

            # Detect objects in the frame
            detection_result = detector.detect_for_video(mp_image, frame_timestamp_ms)

            bboxes = []
            for detection in detection_result.detections:
                bbox = detection.bounding_box
                bboxes.append(
                    [int(bbox.origin_x), int(bbox.origin_y), bbox.width, bbox.height]
                )

            detection_results["frame_idxes"].append(frame_index)
            detection_results["timestamps"].append(frame_timestamp_ms)
            detection_results["number_of_detections"].append(
                len(detection_result.detections)
            )
            detection_results["bboxes"].append(bboxes)

        cap.release()

    return detection_results


def detect_expressions_video(video_path: Path): ...


def _calculate_arm_movement(current, previous):
    # Calculate movement of wrists and elbows
    joints = [15, 16, 13, 14]  # Indices for left/right wrists and elbows
    movement = 0
    for i in joints:
        movement += np.linalg.norm(
            np.array([current[i].x, current[i].y, current[i].z])
            - np.array([previous[i].x, previous[i].y, previous[i].z])
        )
    return movement / len(joints)


def _calculate_twist_turn(current, previous):
    # Calculate movement of shoulders and nose
    joints = [11, 12, 0]  # Indices for left/right shoulders and nose
    movement = 0
    for i in joints:
        movement += np.linalg.norm(
            np.array([current[i].x, current[i].y, current[i].z])
            - np.array([previous[i].x, previous[i].y, previous[i].z])
        )
    return movement / len(joints)


def detect_twists_gests(video_path: Path):
    detection_results = {
        "frame_idxes": [],
        "timestamps": [],
        "twists": [],
        "gesticulations": [],
    }

    with PoseLandmarker.create_from_options(pose_landmarker_options) as landmarker:
        # Open video file or camera
        cap = cv2.VideoCapture(video_path)
        frame_rate = cap.get(cv2.CAP_PROP_FPS)

        frame_index = 0

        previous_landmarks = None

        while cap.isOpened():
            ret, frame = cap.read()

            if not ret:
                print("Unable to capture video")
                break

            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)

            # Calculate the timestamp of the current frame
            frame_timestamp_ms = int(1000 * frame_index / frame_rate)
            frame_index += 1

            pose_landmarker_result = landmarker.detect_for_video(
                mp_image, frame_timestamp_ms
            )

            gest = False
            twist = False

            # Analyze pose landmarks
            if pose_landmarker_result.pose_landmarks:
                current_landmarks = pose_landmarker_result.pose_landmarks[0]

                if previous_landmarks:
                    # Check for gesticulation (arm movement)
                    arm_movement = _calculate_arm_movement(
                        current_landmarks, previous_landmarks
                    )

                    # Check for twisting or turning away (shoulder and head movement)
                    twist_turn = _calculate_twist_turn(
                        current_landmarks, previous_landmarks
                    )

                    if arm_movement > 0.2:  # Adjust threshold as needed
                        gest = True

                    if twist_turn > 0.15:  # Adjust threshold as needed
                        twist = True

                detection_results["frame_idxes"].append(frame_index)
                detection_results["timestamps"].append(frame_timestamp_ms)
                detection_results["gesticulations"].append(gest)
                detection_results["twists"].append(twist)

                previous_landmarks = current_landmarks

        cap.release()

    return detection_results


def extract_subtitles(video_path, reader, frame_skip=20) -> str:
    """
    Extract subtitles from video using EasyOCR.

    Args:
        video_path (str): Path to the video file.
        reader (easyocr.Reader): Initialized EasyOCR reader.
        output_dir (str): Directory to save extracted subtitles.
        frame_skip (int): Number of frames to skip between OCR scans to reduce redundancy.
    """
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    last_text = ""
    subtitles = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = frame[880:, 460:1460]
        # Perform OCR every 'frame_skip' frames to reduce processing
        if frame_count % frame_skip == 0:
            # Optionally, crop the frame to the subtitle area to improve OCR accuracy
            # For simplicity, we'll use the entire frame here
            result = reader.readtext(frame, detail=0, paragraph=True)
            text = " ".join(result).strip()

            if text and text != last_text:
                subtitles.append(text)
                last_text = text
                print(f"Extracted Subtitle: {text}")

        frame_count += 1

    cap.release()

    return " ".join(subtitles)


# Preprocess texts: lowercasing, removing extra spaces, etc.
def preprocess_text(text):
    text = text.lower()
    text = " ".join(text.split())  # Remove extra whitespace
    return text


def align_segments(subtitles, transcription):
    """
    Align segments using SequenceMatcher's get_matching_blocks.

    Args:
        subtitles (list): List of subtitle segments.
        transcription (list): List of transcription segments.

    Returns:
        list of tuples: Aligned pairs (subtitle, transcription)
    """
    matcher = difflib.SequenceMatcher(None, subtitles, transcription)
    matches = matcher.get_matching_blocks()

    aligned_pairs = []
    for match in matches:
        for i in range(match.size):
            aligned_pairs.append((subtitles[match.a + i], transcription[match.b + i]))

    return aligned_pairs


def compare_subtitles(video_path: Path, transcription_text: str):
    reader = easyocr.Reader(["pl"])
    extracted_subtitles_text = extract_subtitles(video_path, reader, frame_skip=15)

    extracted_subtitles_text = preprocess_text(extracted_subtitles_text)
    transcription_text = preprocess_text(transcription_text)

    extracted_subtitles_sentences = sent_tokenize(extracted_subtitles_text)
    transcription_sentences = sent_tokenize(transcription_text)

    # Ensure both lists have the same length
    min_length = min(len(extracted_subtitles_sentences), len(transcription_sentences))
    extracted_subtitles_sentences = extracted_subtitles_sentences[:min_length]
    transcription_sentences = transcription_sentences[:min_length]

    # Initialize lists to store similarity scores
    sequence_matcher_scores = []
    levenshtein_scores = []
    jaccard_scores = []
    fuzzy_scores = []
    rapidfuzz_scores = []

    aligned_pairs = align_segments(
        extracted_subtitles_sentences, transcription_sentences
    )

    # Now, compare aligned_pairs as before
    for i, (subtitle, transcription) in enumerate(aligned_pairs, 1):
        seq_score = calculate_sequence_matcher(subtitle, transcription)
        lev_score = calculate_levenshtein(subtitle, transcription)
        jac_score = calculate_jaccard(subtitle, transcription)
        fuzz_score = calculate_fuzzy_matching(subtitle, transcription)
        rapidfuzz_score = calculate_rapidfuzz_matching(subtitle, transcription)

        sequence_matcher_scores.append(seq_score)
        levenshtein_scores.append(lev_score)
        jaccard_scores.append(jac_score)
        fuzzy_scores.append(fuzz_score)
        rapidfuzz_scores.append(rapidfuzz_score)

    # Calculate average similarity scores
    avg_seq = np.mean(sequence_matcher_scores) * 100
    avg_lev = np.mean(levenshtein_scores) * 100
    avg_jac = np.mean(jaccard_scores) * 100
    avg_fuzz = np.mean(fuzzy_scores) * 100
    avg_rapidfuzz = np.mean(rapidfuzz_scores) * 100

    # Identify segments with low similarity (e.g., below 70%)
    threshold = 70
    for i in range(min_length):
        if (
            sequence_matcher_scores[i] * 100 < threshold
            or levenshtein_scores[i] * 100 < threshold
            or jaccard_scores[i] * 100 < threshold
            or fuzzy_scores[i] * 100 < threshold
            or rapidfuzz_scores[i] * 100 < threshold
        ):
            print(f"\nLow Similarity in Segment {i+1}:")
            print(f"Subtitle: {extracted_subtitles_sentences[i]}")
            print(f"Transcription: {transcription_sentences[i]}")
            print(f"SequenceMatcher: {sequence_matcher_scores[i] * 100:.2f}%")
            print(f"Levenshtein: {levenshtein_scores[i] * 100:.2f}%")
            print(f"Jaccard: {jaccard_scores[i] * 100:.2f}%")
            print(f"Fuzzy Matching: {fuzzy_scores[i] * 100:.2f}%")
            print(f"RapidFuzz Matching: {rapidfuzz_scores[i] * 100:.2f}%")

    similarity_scores = {
        "Sequence Matcher Score": avg_seq,
        "Levenshtein Distance": avg_lev,
        "Jaccard Distance": avg_jac,
        "Fuzzy Matching Score": avg_fuzz,
        "Rapid Fuzzy Matching": avg_rapidfuzz,
    }

    return similarity_scores
