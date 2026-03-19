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