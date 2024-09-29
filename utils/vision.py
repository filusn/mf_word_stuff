from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
from moviepy.editor import VideoFileClip

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
