import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import urllib.request
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.gesture.gesture_classifier import GestureClassifier
from src.core.action_dispatcher import ActionDispatcher
from src.integrations.pc_controller import PCController

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

GESTURE_COLORS = {
    "OPEN_HAND":    (0, 255, 0),
    "CLOSED_FIST":  (0, 0, 255),
    "INDEX_UP":     (255, 255, 0),
    "TWO_FINGERS":  (255, 165, 0),
    "THUMB_UP":     (0, 255, 255),
    "THUMB_DOWN":   (128, 0, 255),
    "UNKNOWN":      (180, 180, 180),
    "NO_HAND":      (180, 180, 180),
}

if not os.path.exists(MODEL_PATH):
    print("Descargando modelo... (solo la primera vez)")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print("Modelo descargado.")

class HandDetector:
    def __init__(self):
        base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=2,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            running_mode=vision.RunningMode.VIDEO
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        self.latest_result = None
        self.classifier = GestureClassifier()

    def get_control_hand_index(self):
        if not self.latest_result or not self.latest_result.handedness:
            return None
        for i, handedness in enumerate(self.latest_result.handedness):
            if handedness[0].category_name == "Left":
                return i
        return None

    def process_frame(self, frame, timestamp_ms):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        self.latest_result = self.detector.detect_for_video(mp_image, timestamp_ms)
        return self.draw_landmarks(frame)

    def draw_landmarks(self, frame):
        right_index = self.get_control_hand_index()
        if right_index is None:
            return frame
        h, w, _ = frame.shape
        hand_landmarks = self.latest_result.hand_landmarks[right_index]
        points = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks]
        for a, b in CONNECTIONS:
            cv2.line(frame, points[a], points[b], (0, 200, 255), 2)
        for x, y in points:
            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
        return frame

    def get_landmarks(self, frame):
        right_index = self.get_control_hand_index()
        if right_index is None:
            return []
        h, w, _ = frame.shape
        hand_landmarks = self.latest_result.hand_landmarks[right_index]
        return [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks]


def draw_progress_bar(frame, progress, gesture, color):
    h, w, _ = frame.shape
    bar_w = int(w * 0.4)
    bar_x = int(w * 0.3)
    bar_y = h - 40
    bar_h = 16

    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (50, 50, 50), -1)
    fill = int(bar_w * progress)
    if fill > 0:
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill, bar_y + bar_h), color, -1)
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (200, 200, 200), 1)


if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    detector = HandDetector()
    pc = PCController()

    dispatcher = ActionDispatcher(hold_time=0.5)
    dispatcher.register("THUMB_UP",    pc.volume_up,   repeat=True)
    dispatcher.register("THUMB_DOWN",  pc.volume_down, repeat=True)
    dispatcher.register("OPEN_HAND",   pc.play_pause)
    dispatcher.register("CLOSED_FIST", pc.mute)
    dispatcher.register("INDEX_UP",    pc.prev_track)
    dispatcher.register("TWO_FINGERS", pc.next_track)

    timestamp = 0
    print("Sistema iniciado. Manten un gesto 0.5 segundos para ejecutarlo.")
    print("Presiona Q para salir.")

    while True:
        success, frame = cap.read()
        if not success:
            break

        timestamp += 33
        frame = detector.process_frame(frame, timestamp)
        landmarks = detector.get_landmarks(frame)

        gesture = detector.classifier.classify(landmarks)
        executed = dispatcher.update(gesture)
        progress = dispatcher.get_progress()
        color = GESTURE_COLORS.get(gesture, (180, 180, 180))

        hand_label = "Mano de control detectada" if landmarks else "Esperando mano de control..."
        cv2.putText(frame, hand_label, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 1)

        cv2.putText(frame, f"Gesto: {gesture}", (10, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)

        if executed:
            cv2.putText(frame, f"EJECUTADO: {executed}", (10, 105),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        draw_progress_bar(frame, progress, gesture, color)

        cv2.imshow("GBIAS - Action Dispatcher", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()