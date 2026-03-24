class ProfileManager :
    def __init__(self):
        self.profiles = {}
        self.current_profile = None
        self.profile_order = []

    def register_profile(self, key, name, actions) :
        """Regsitra un perfil con su tecla, nombre y mapa de gestos a acciones."""
        self.profiles[key] = {
            "name": name,
            "actions": actions
        }
        self.profile_order.append(key)

    def switch_to(self, key):
        """Cambia al perfil indicado por tecla."""
        if key in self.profiles:
            self.current_profile = key
            print(f"[PERFIL] Cambiado a: {self.profiles[key]['name']}")
            return self.profiles[key]
        return None
    
    def get_current_actions(self):
        """Devuelve el mapa de acciones del perfil activado."""
        if self.current_profile and self.current_profile in self.profiles:
            return self.profiles[self.current_profile]["actions"]
        return{}
    
    def get_current_name(self):
        """Devuelve el nombre del perfil activo."""
        if self.current_profile and self.current_profile in self.profiles:
            return self.profiles[self.current_profile]["name"]
        return "Sin perfil"