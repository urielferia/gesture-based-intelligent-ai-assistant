class ProfileManager :
    def __init__(self):
        self.profiles = {}
        self.current_profile = None
        self.profile_order = []

    def register_profile(self, key, name, actions):
        """Registers a profile with its key, name, and gesture-to-action map."""
        self.profiles[key] = {
            "name": name,
            "actions": actions
        }
        self.profile_order.append(key)

    def switch_to(self, key):
        """Switches to the profile indicated by key."""
        if key in self.profiles:
            self.current_profile = key
            print(f"[PROFILE] Switched to: {self.profiles[key]['name']}")
            return self.profiles[key]
        return None
    
    def get_current_actions(self):
        """Returns the action map of the active profile."""
        if self.current_profile and self.current_profile in self.profiles:
            return self.profiles[self.current_profile]["actions"]
        return {}
    
    def get_current_name(self):
        """Returns the name of the active profile."""
        if self.current_profile and self.current_profile in self.profiles:
            return self.profiles[self.current_profile]["name"]
        return "No Profile"