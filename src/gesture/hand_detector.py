import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import urllib.request
import os

MODEL_PATH = "hand_landmarker.task"
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"

CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (5,9),(9,10),(10,11),(11,12),
    (9,13),(13,14),(14,15),(15,16),
    (13,17),(17,18),(18,19),(19,20),
    (0,17)
]

if not os.path.exists(MODEL_PATH):
    print("Descargando modelo... (solo la primera vez)")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print("Modelo descargado.")

class HandDetector:
    def __init__(self):
        base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            running_mode=vision.RunningMode.VIDEO
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        self.latest_result = None

    def process_frame(self, frame, timestamp_ms):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        self.latest_result = self.detector.detect_for_video(mp_image, timestamp_ms)
        return self.draw_landmarks(frame)

    def draw_landmarks(self, frame):
        if not self.latest_result or not self.latest_result.hand_landmarks:
            return frame
        h, w, _ = frame.shape
        for hand_landmarks in self.latest_result.hand_landmarks:
            points = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks]
            for a, b in CONNECTIONS:
                cv2.line(frame, points[a], points[b], (0, 200, 255), 2)
            for x, y in points:
                cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
        return frame

    def get_landmarks(self, frame):
        landmarks = []
        if not self.latest_result or not self.latest_result.hand_landmarks:
            return landmarks
        h, w, _ = frame.shape
        for hand_landmarks in self.latest_result.hand_landmarks:
            for lm in hand_landmarks:
                landmarks.append((int(lm.x * w), int(lm.y * h)))
        return landmarks


if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    detector = HandDetector()
    timestamp = 0

    print("Detección iniciada. Presiona Q para salir.")

    while True:
        success, frame = cap.read()
        if not success:
            break

        timestamp += 33
        frame = detector.process_frame(frame, timestamp)
        landmarks = detector.get_landmarks(frame)

        cv2.putText(frame, f"Puntos detectados: {len(landmarks)}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.8, (0, 255, 0), 2)

        cv2.imshow("GBIAS - Hand Detector", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()