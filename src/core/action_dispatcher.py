import time
import threading

class ActionDispatcher:
    def __init__(self, hold_time=0.5, repeat_interval=0.2, intent_interval=15):
        self.hold_time = hold_time
        self.repeat_interval = repeat_interval
        self.current_gesture = None
        self.gesture_start = None
        self.last_executed = None
        self.actions = {}
        self.executed_at = None
        self.repeat_gestures = set()
        self.last_repeat_time = None

        # Intent engine (opcional, se activa si se configura)
        self.intent_interval = intent_interval  # segundos entre consultas
        self.observation_logger = None
        self.intent_engine = None
        self.last_intent = None
        self._intent_thread = None
        self._running = False

    def setup_intent(self, observation_logger, intent_engine):
        """Conecta el logger y el engine al dispatcher."""
        self.observation_logger = observation_logger
        self.intent_engine = intent_engine

    def start_intent_loop(self):
        """Inicia el hilo de inferencia en segundo plano."""
        self._running = True
        self._intent_thread = threading.Thread(target=self._intent_loop, daemon=True)
        self._intent_thread.start()

    def stop_intent_loop(self):
        self._running = False

    def _intent_loop(self):
        """Corre en segundo plano: cada intent_interval segundos consulta a Gemini."""
        while self._running:
            time.sleep(self.intent_interval)
            if self.observation_logger and self.intent_engine:
                snapshot = self.observation_logger.get_context_snapshot()
                result = self.intent_engine.infer(snapshot)
                self.last_intent = result
                self._handle_intent(result)

    def _handle_intent(self, intent: dict):
        """Ejecuta la acción sugerida si la confianza es suficiente."""
        action = intent.get("suggested_action", "none")
        confidence = intent.get("confidence", 0.0)

        print(f"[INTENT] {intent.get('inferred_intent')} | acción: {action} | confianza: {confidence:.2f}")

        if confidence < 0.7 or action == "none":
            return

        # Mapeo de acciones sugeridas por Gemini a acciones registradas
        intent_action_map = {
            "skip_track":     "NEXT_TRACK",
            "pause_media":    "CLOSED_FIST",
            "increase_volume":"OPEN_HAND",
            "lower_volume":   "THUMB_DOWN",
            "suggest_break":  None,  # placeholder futuro
        }

        mapped = intent_action_map.get(action)
        if mapped and mapped in self.actions:
            print(f"[INTENT] Ejecutando acción automática: {mapped}")
            self.actions[mapped]()

    def register(self, gesture, action, repeat=False):
        self.actions[gesture] = action
        if repeat:
            self.repeat_gestures.add(gesture)

    def update(self, gesture):
        now = time.time()

        # Loguear gesto si el logger está conectado
        if self.observation_logger and gesture not in ("NO_HAND", "UNKNOWN"):
            self.observation_logger.log_gesture(gesture)

        if gesture != self.current_gesture:
            self.current_gesture = gesture
            self.gesture_start = now
            self.last_repeat_time = None
            self.last_executed = None
            return None

        if gesture in ("NO_HAND", "UNKNOWN"):
            self.last_executed = None
            self.last_repeat_time = None
            return None

        elapsed = now - self.gesture_start

        if gesture in self.repeat_gestures and gesture == self.last_executed:
            if self.last_repeat_time is None or (now - self.last_repeat_time) >= self.repeat_interval:
                if gesture in self.actions:
                    self.actions[gesture]()
                    self.last_repeat_time = now
                    self.executed_at = now
                    return gesture
            return None

        if elapsed >= self.hold_time and gesture != self.last_executed:
            if gesture in self.actions:
                self.actions[gesture]()
                self.last_executed = gesture
                self.executed_at = now
                self.last_repeat_time = now
                return gesture

        return None

    def get_progress(self):
        if self.current_gesture in ("NO_HAND", "UNKNOWN", None):
            return 0.0
        if self.executed_at and (time.time() - self.executed_at) < 0.3:
            return 1.0
        elapsed = time.time() - self.gesture_start
        return min(elapsed / self.hold_time, 1.0)