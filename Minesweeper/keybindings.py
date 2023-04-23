# type: ignore
import curses.ascii

class KeyConfig():
    def __init__(self, source_dict):
        self.key_dict_valid(source_dict, error=True)

        # input validation complete; set attributes
        for category in source_dict.values():
            for id, (key, descrip) in category.items():
                if hasattr(self, id):
                    raise KeybindingError(
                        f"control {id} defined multiple times"
                    )
                else:
                    setattr(self, id.upper(), Key(id, key, descrip))

    def __getattr__(self, name):
        raise AttributeError(
            f"key id {name} was requested, but it wasn't present in the keybinding configuration"
        )

    @staticmethod
    def key_dict_valid(source_dict, error: bool) -> bool:
        """Raise errors if error=True, otherwise return True if dict is valid and False otherwise"""
        # first, check that there are no overlaps anywhere with the "Universal" category
        all_keys = list()
        for category in source_dict.values():
            for _, (key, _) in category.items():
                all_keys.append(key)

        for _, (key, _) in source_dict["Universal"].items():
            if all_keys.count(key) > 1:
                if error:
                    return False
                raise KeybindingError(f"universal keybinding clash: key \"{key}\"")

        # next, check for overlaps within each of the categories
        for cat_name, category in source_dict.items():
            cat_keys = list()
            for _, (key, _) in category.items():
                if key in cat_keys:
                    if error:
                        return False
                    raise KeybindingError(f"keybinding clash in category {cat_name}: key \"{key}\"")
                else:
                    cat_keys.append(key)
        
        return True

class Key():
    key_names = {
        "Escape": (chr(curses.ascii.ESC),),
        "Up arrow": ("KEY_UP", "KEY_A2"),
        "Left arrow": ("KEY_LEFT", "KEY_B1"),
        "Down arrow": ("KEY_DOWN", "KEY_C2"),
        "Right arrow": ("KEY_RIGHT", "KEY_B3"),
        "Enter": (chr(curses.ascii.LF),),
        "Backspace": (chr(curses.ascii.BS),),
        "Delete": ("KEY_DC",)
    }

    def __init__(self, id:str, key: str, descrip: str):
        self.id = id
        self.name = '"' + key + '"'

        if len(key) == 1:
            self._key = (key,)
        elif key in self.key_names.keys():
            self._key = self.key_names[key]
        else:
            raise KeybindingError(f"key {key} undefined")
        
        self.descrip = descrip

    def __eq__(self, other):
        if isinstance(other, Key):
            return self._key == other._key
        elif isinstance(other, str):
            return other in self._key
        else:
            return NotImplemented

    def __repr__(self):
        return f"{self.id}: {self.name}"
    
    def __str__(self):
        return self.name


class KeybindingError(RuntimeError):
    pass


if __name__ == "__main__":
    import json
    
    with open("data.json", "r") as f:
        data = json.load(f)

    cfg = KeyConfig(data["controls"])
