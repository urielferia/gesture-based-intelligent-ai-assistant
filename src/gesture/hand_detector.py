import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import urllib.request
import os
from gesture_classifier import GestureClassifier

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
            num_hands=2,  # Detectamos 2 para poder filtrar por lateralidad
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            running_mode=vision.RunningMode.VIDEO
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        self.latest_result = None
        self.classifier = GestureClassifier()

    def get_left_hand_index(self):
        """Devuelve el índice de la mano izquierda en los resultados, o None si no está."""
        if not self.latest_result or not self.latest_result.handedness:
            return None
        for i, handedness in enumerate(self.latest_result.handedness):
            # MediaPipe etiqueta la mano izquierda como "Left" en imagen espejada
            # por eso buscamos "Left" — es la mano izquierda del usuario
            if handedness[0].category_name == "Left":
                return i
        return None

    def process_frame(self, frame, timestamp_ms):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        self.latest_result = self.detector.detect_for_video(mp_image, timestamp_ms)
        return self.draw_landmarks(frame)

    def draw_landmarks(self, frame):
        right_index = self.get_left_hand_index()
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
        right_index = self.get_left_hand_index()
        if right_index is None:
            return []
        h, w, _ = frame.shape
        hand_landmarks = self.latest_result.hand_landmarks[right_index]
        return [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks]


if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    detector = HandDetector()
    timestamp = 0

    print("Detección iniciada — solo mano izquierda activa.")
    print("Presiona Q para salir.")

    while True:
        success, frame = cap.read()
        if not success:
            break

        timestamp += 33
        frame = detector.process_frame(frame, timestamp)
        landmarks = detector.get_landmarks(frame)

        gesture = detector.classifier.classify(landmarks)
        color = GESTURE_COLORS.get(gesture, (180, 180, 180))

        # Indicador de mano activa
        hand_label = "Mano izquierda detectada" if landmarks else "Esperando mano izquierda..."
        cv2.putText(frame, hand_label,
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 200, 255), 1)

        cv2.putText(frame, f"Gesto: {gesture}",
                    (10, 65), cv2.FONT_HERSHEY_SIMPLEX,
                    1.0, color, 2)

        cv2.imshow("GBIAIS - Hand Detector", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()