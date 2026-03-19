class GestureClassifier:
    def __init__(self):
        self.TIP_IDS = [4, 8, 12, 16, 20]

    def get_finger_states(self, landmarks):
        if not landmarks or len(landmarks) < 21:
            return None

        fingers = []

        # Pulgar: comparar posición horizontal (x) respecto a su base
        if landmarks[4][0] < landmarks[3][0]:
            fingers.append(1)
        else:
            fingers.append(0)

        # Dedos índice, medio, anular, meñique: comparar posición vertical (y)
        for tip_id in self.TIP_IDS[1:]:
            if landmarks[tip_id][1] < landmarks[tip_id - 2][1]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers  # [pulgar, indice, medio, anular, menique]

    def classify(self, landmarks):
        if not landmarks or len(landmarks) < 21:
            return "NO_HAND"

        fingers = self.get_finger_states(landmarks)
        if fingers is None:
            return "NO_HAND"

        # Dedos sin contar el pulgar
        non_thumb = fingers[1:]

        # Mano abierta: todos extendidos
        if fingers == [1, 1, 1, 1, 1]:
            return "OPEN_HAND"

        # Mano cerrada: todos doblados
        if fingers == [0, 0, 0, 0, 0]:
            return "CLOSED_FIST"

        # Índice arriba: solo índice extendido
        if non_thumb == [1, 0, 0, 0] and fingers[0] == 0:
            return "INDEX_UP"

        # Dos dedos: índice y medio extendidos
        if non_thumb == [1, 1, 0, 0] and fingers[0] == 0:
            return "TWO_FINGERS"

        # Pulgar arriba / abajo: solo los 4 dedos doblados, pulgar libre
        # No importa el estado del pulgar en fingers[], usamos posición Y directamente
        if non_thumb == [0, 0, 0, 0]:
            thumb_tip_y  = landmarks[4][1]
            thumb_base_y = landmarks[2][1]
            wrist_y      = landmarks[0][1]

            # Pulgar apunta hacia arriba: punta más alta que su base Y más alta que muñeca
            if thumb_tip_y < thumb_base_y and thumb_tip_y < wrist_y:
                return "THUMB_UP"

            # Pulgar apunta hacia abajo: punta más baja que su base
            if thumb_tip_y > thumb_base_y:
                return "THUMB_DOWN"

        return "UNKNOWN"