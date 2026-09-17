import platform
import pyautogui

class PCController:
    def __init__(self):
        self.system = platform.system()
        pyautogui.FAILSAFE = False

    def volume_up(self):
        if self.system == "Windows":
            pyautogui.press('volumeup')
        print("[PC] Volume Up")

    def volume_down(self):
        if self.system == "Windows":
            pyautogui.press('volumedown')
        print("[PC] Volume Down")

    def mute(self):
        if self.system == "Windows":
            pyautogui.press('volumemute')
        print("[PC] Mute")

    def next_track(self):
        if self.system == "Windows":
            pyautogui.press('nexttrack')
        print("[PC] Next Track")

    def prev_track(self):
        if self.system == "Windows":
            pyautogui.press('prevtrack')
        print("[PC] Previous Track")

    def play_pause(self):
        if self.system == "Windows":
            pyautogui.press('playpause')
        print("[PC] Play/Pause")