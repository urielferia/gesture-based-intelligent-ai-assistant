# src/core/observation_logger.py
from collections import deque
from datetime import datetime
import json

class ObservationLogger:
    def __init__(self, buffer_size=20):
        # Buffer circular: guarda los últimos N gestos
        self.gesture_buffer = deque(maxlen=buffer_size)
        self.session_start = datetime.now()
        self.active_profile = "PC"

    def log_gesture(self, gesture: str):
        """Llamar cada vez que se detecta un gesto válido."""
        self.gesture_buffer.append({
            "gesture": gesture,
            "timestamp": datetime.now().isoformat()
        })

    def set_profile(self, profile: str):
        """Actualizar cuando el usuario cambia de perfil."""
        self.active_profile = profile

    def get_context_snapshot(self) -> str:
        """Devuelve el contexto actual como JSON string, listo para el LLM."""
        now = datetime.now()
        session_minutes = (now - self.session_start).seconds // 60

        # Calcular gestos recientes con tiempo relativo
        recent = []
        for entry in list(self.gesture_buffer)[-10:]:  # últimos 10
            ts = datetime.fromisoformat(entry["timestamp"])
            seconds_ago = int((now - ts).total_seconds())
            recent.append({
                "gesture": entry["gesture"],
                "time_ago_s": seconds_ago
            })

        # Frecuencia: gestos en los últimos 30 segundos
        last_30s = [
            e for e in self.gesture_buffer
            if (now - datetime.fromisoformat(e["timestamp"])).total_seconds() < 30
        ]
        if len(last_30s) >= 5:
            frequency = "alta"
        elif len(last_30s) >= 2:
            frequency = "media"
        else:
            frequency = "baja"

        # Hora del día
        hour = now.hour
        if 6 <= hour < 12:
            time_of_day = "mañana"
        elif 12 <= hour < 18:
            time_of_day = "tarde"
        elif 18 <= hour < 22:
            time_of_day = "noche"
        else:
            time_of_day = "madrugada"

        snapshot = {
            "timestamp": now.isoformat(),
            "active_profile": self.active_profile,
            "recent_gestures": recent,
            "gesture_frequency": frequency,
            "session_duration_min": session_minutes,
            "time_of_day": time_of_day
        }

        return json.dumps(snapshot, ensure_ascii=False, indent=2)
    