class GestureClassifier:
    def __init__(self):
        self.TIP_IDS = [4, 8, 12, 16, 20]

    def get_finger_states(self, landmarks):
        if not landmarks or len(landmarks) < 21:
            return None

        fingers = []

        if landmarks[4][0] < landmarks[3][0]:
            fingers.append(1)
        else:
            fingers.append(0)

        for tip_id in self.TIP_IDS[1:]:
            if landmarks[tip_id][1] < landmarks[tip_id - 2][1]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers

    def classify(self, landmarks):
        if not landmarks or len(landmarks) < 21:
            return "NO_HAND"

        fingers = self.get_finger_states(landmarks)
        if fingers is None:
            return "NO_HAND"

        non_thumb = fingers[1:]

        if fingers == [1, 1, 1, 1, 1]:
            return "OPEN_HAND"

        if fingers == [0, 0, 0, 0, 0]:
            return "CLOSED_FIST"

        if non_thumb == [1, 0, 0, 0] and fingers[0] == 0:
            return "INDEX_UP"

        if non_thumb == [1, 1, 0, 0] and fingers[0] == 0:
            return "TWO_FINGERS"

        if non_thumb == [0, 0, 0, 0]:
            thumb_tip_y  = landmarks[4][1]
            thumb_base_y = landmarks[2][1]
            wrist_y      = landmarks[0][1]

            if thumb_tip_y < thumb_base_y and thumb_tip_y < wrist_y:
                return "THUMB_UP"

            if thumb_tip_y > thumb_base_y:
                return "THUMB_DOWN"

        return "UNKNOWN"