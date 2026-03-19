import time

class ActionDispatcher:
    def __init__(self, hold_time=0.5, repeat_interval=0.2):
        self.hold_time = hold_time
        self.repeat_interval = repeat_interval
        self.current_gesture = None
        self.gesture_start = None
        self.last_executed = None
        self.actions = {}
        self.executed_at = None
        self.repeat_gestures = set()
        self.last_repeat_time = None

    def register(self, gesture, action, repeat=False):
        self.actions[gesture] = action
        if repeat:
            self.repeat_gestures.add(gesture)

    def update(self, gesture):
        now = time.time()

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