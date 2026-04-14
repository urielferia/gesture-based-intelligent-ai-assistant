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
from src.core.profile_manager import ProfileManager
from src.integrations.pc_controller import PCController
from src.core.observation_logger import ObservationLogger
from src.core.intent_engine import IntentEngine

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
    "THUMB_UP":     (0, 255, 255),
    "THUMB_DOWN":   (128, 0, 255),
    "PREV_TRACK":   (255, 165, 0),
    "NEXT_TRACK":   (255, 100, 0),
    "SPIDERMAN":    (255, 0, 150),
    "PROFILE_1":    (255, 200, 0),
    "PROFILE_2":    (0, 255, 120),
    "PROFILE_3":    (180, 100, 255),
    "PROFILE_4":    (0, 180, 255),
    "UNKNOWN":      (180, 180, 180),
    "NO_HAND":      (180, 180, 180),
}

PROFILE_COLORS = {
    "1": (255, 200, 0),
    "2": (0, 255, 120),
    "3": (180, 100, 255),
    "4": (0, 180, 255),
}

SYSTEM_GESTURES = {"SPIDERMAN", "PROFILE_1", "PROFILE_2", "PROFILE_3", "PROFILE_4", "QUIT"}

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


def draw_profile_indicator(frame, profile_name, profile_key, paused):
    h, w, _ = frame.shape
    color = PROFILE_COLORS.get(profile_key, (255, 255, 255))
    label = f"Perfil {profile_key}: {profile_name}"
    cv2.putText(frame, label, (w - 280, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    if paused:
        cv2.putText(frame, "PAUSADO", (w - 140, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)


def build_dispatcher(profile_actions, pc):
    dispatcher = ActionDispatcher(hold_time=0.5)
    repeat_gestures = ["THUMB_UP", "THUMB_DOWN"]
    for gesture, action_name in profile_actions.items():
        action = getattr(pc, action_name, None)
        if action:
            dispatcher.register(gesture, action, repeat=(gesture in repeat_gestures))
        else:
            dispatcher.register(gesture, lambda n=action_name: print(f"[ACCION] {n}"),
                                repeat=(gesture in repeat_gestures))
    return dispatcher


if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    detector = HandDetector()
    pc = PCController()
    paused = True

    profiles = ProfileManager()

    profiles.register_profile("1", "PC", {
        "OPEN_HAND":   "play_pause",
        "CLOSED_FIST": "mute",
        "PREV_TRACK":  "prev_track",
        "NEXT_TRACK":  "next_track",
        "THUMB_UP":    "volume_up",
        "THUMB_DOWN":  "volume_down",
    })

    profiles.register_profile("2", "Luces", {
        "OPEN_HAND":   "lights_on",
        "CLOSED_FIST": "lights_off",
        "THUMB_UP":    "brightness_up",
        "THUMB_DOWN":  "brightness_down",
    })

    profiles.register_profile("3", "Zen", {
        "OPEN_HAND":   "zen_on",
        "CLOSED_FIST": "zen_off",
        "THUMB_UP":    "brightness_up",
        "THUMB_DOWN":  "brightness_down",
    })

    profiles.register_profile("4", "Musica", {
        "OPEN_HAND":   "play_pause",
        "CLOSED_FIST": "mute",
        "PREV_TRACK":  "prev_track",
        "NEXT_TRACK":  "next_track",
        "THUMB_UP":    "volume_up",
        "THUMB_DOWN":  "volume_down",
    })

    profiles.switch_to("1")
    logger = ObservationLogger()
    engine = IntentEngine()
    dispatcher = build_dispatcher(profiles.get_current_actions(), pc)
    dispatcher.setup_intent(logger, engine)
    dispatcher.start_intent_loop()

    # Dispatcher exclusivo para gestos de sistema
    system_dispatcher = ActionDispatcher(hold_time=0.8)
    system_dispatcher.register("SPIDERMAN", lambda: None)
    system_dispatcher.register("PROFILE_1", lambda: None)
    system_dispatcher.register("PROFILE_2", lambda: None)
    system_dispatcher.register("PROFILE_3", lambda: None)
    system_dispatcher.register("PROFILE_4", lambda: None)
    system_dispatcher.register("QUIT", lambda: None)

    quit_dispatcher = ActionDispatcher(hold_time=5.0)
    quit_dispatcher.register("QUIT", lambda: None)

    timestamp = 0
    print("Sistema iniciado. Gestos de perfil para cambiar. Spiderman para pausar. Q para salir.")

    while True:
        success, frame = cap.read()
        if not success:
            break

        timestamp += 33
        frame = detector.process_frame(frame, timestamp)
        landmarks = detector.get_landmarks(frame)
        gesture = detector.classifier.classify(landmarks)
        color = GESTURE_COLORS.get(gesture, (180, 180, 180))

        #QUIT siempre activo para cerrar el programa
        if gesture == "QUIT":
            executed_quit = quit_dispatcher.update(gesture)
            progress = quit_dispatcher.get_progress()
            if executed_quit == "QUIT":
                print("[SISTEMA] Cerrando programa...")
                break

        # Spiderman siempre activo para pausar/reanudar
        if gesture == "SPIDERMAN":
            executed_system = system_dispatcher.update(gesture)
            progress = system_dispatcher.get_progress()
            if executed_system == "SPIDERMAN":
                paused = not paused
                print(f"[SISTEMA] {'Pausado' if paused else 'Reanudado'}")

        # Cambio de perfil y acciones solo si NO está pausado
        elif not paused:
            if gesture in SYSTEM_GESTURES:
                executed_system = system_dispatcher.update(gesture)
                progress = system_dispatcher.get_progress()
                if executed_system in ("PROFILE_1", "PROFILE_2", "PROFILE_3", "PROFILE_4"):
                    key = executed_system[-1]
                    profiles.switch_to(key)
                    dispatcher = build_dispatcher(profiles.get_current_actions(), pc)
                    dispatcher.setup_intent(logger, engine)
                    dispatcher.start_intent_loop
                    logger.set_profile(profiles.get_current_name())
            else:
                system_dispatcher.update("NO_HAND")
                executed = dispatcher.update(gesture)
                progress = dispatcher.get_progress()

        # Si está pausado e hizo otro gesto, ignorar todo
        else:
            system_dispatcher.update("NO_HAND")
            dispatcher.update("NO_HAND")
            progress = 0.0

        hand_label = "Mano de control detectada" if landmarks else "Esperando mano de control..."
        cv2.putText(frame, hand_label, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 1)

        cv2.putText(frame, f"Gesto: {gesture}", (10, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)

        draw_progress_bar(frame, progress, gesture, color)
        draw_profile_indicator(frame, profiles.get_current_name(),
                               profiles.current_profile, paused)

        cv2.imshow("GBIAS - Intelligent Assistant", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if dispatcher.last_intent:
            intent_text = dispatcher.last_intent.get("inferred_intent", "")[:50]
            conf = dispatcher.last_intent.get("confidence", 0.0)
            cv2.putText(frame, f"Intent: {intent_text}", (10, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 0), 1)
            cv2.putText(frame, f"Conf: {conf:.2f}", (10, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 0), 1)

    cap.release()
    cv2.destroyAllWindows()