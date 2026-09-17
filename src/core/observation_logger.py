# src/core/observation_logger.py
from collections import deque
from datetime import datetime
import json

class ObservationLogger:
    def __init__(self, buffer_size=20):
        # Circular buffer: stores the last N gestures
        self.gesture_buffer = deque(maxlen=buffer_size)
        self.session_start = datetime.now()
        self.active_profile = "PC"

    def log_gesture(self, gesture: str):
        """Call every time a valid gesture is detected."""
        self.gesture_buffer.append({
            "gesture": gesture,
            "timestamp": datetime.now().isoformat()
        })

    def set_profile(self, profile: str):
        """Update when the user changes profiles."""
        self.active_profile = profile

    def get_context_snapshot(self) -> str:
        """Returns the current context as a JSON string, ready for the LLM."""
        now = datetime.now()
        session_minutes = (now - self.session_start).seconds // 60

        # Calculate recent gestures with relative time
        recent = []
        for entry in list(self.gesture_buffer)[-10:]:  # last 10
            ts = datetime.fromisoformat(entry["timestamp"])
            seconds_ago = int((now - ts).total_seconds())
            recent.append({
                "gesture": entry["gesture"],
                "time_ago_s": seconds_ago
            })

        # Frequency: gestures in the last 30 seconds
        last_30s = [
            e for e in self.gesture_buffer
            if (now - datetime.fromisoformat(e["timestamp"])).total_seconds() < 30
        ]
        if len(last_30s) >= 5:
            frequency = "high"
        elif len(last_30s) >= 2:
            frequency = "medium"
        else:
            frequency = "low"

        # Time of day
        hour = now.hour
        if 6 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 18:
            time_of_day = "afternoon"
        elif 18 <= hour < 22:
            time_of_day = "evening"
        else:
            time_of_day = "late_night"

        snapshot = {
            "timestamp": now.isoformat(),
            "active_profile": self.active_profile,
            "recent_gestures": recent,
            "gesture_frequency": frequency,
            "session_duration_min": session_minutes,
            "time_of_day": time_of_day
        }

        return json.dumps(snapshot, ensure_ascii=False, indent=2)
    