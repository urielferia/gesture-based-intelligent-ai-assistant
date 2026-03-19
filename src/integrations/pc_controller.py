import platform
import pyautogui

class PCController:
    def __init__(self):
        self.system = platform.system()
        pyautogui.FAILSAFE = False

    def volume_up(self):
        if self.system == "Windows":
            pyautogui.press('volumeup')
        print("[PC] Volumen subido")

    def volume_down(self):
        if self.system == "Windows":
            pyautogui.press('volumedown')
        print("[PC] Volumen bajado")

    def mute(self):
        if self.system == "Windows":
            pyautogui.press('volumemute')
        print("[PC] Mute")

    def next_track(self):
        if self.system == "Windows":
            pyautogui.press('nexttrack')
        print("[PC] Siguiente cancion")

    def prev_track(self):
        if self.system == "Windows":
            pyautogui.press('prevtrack')
        print("[PC] Cancion anterior")

    def play_pause(self):
        if self.system == "Windows":
            pyautogui.press('playpause')
        print("[PC] Play/Pause")