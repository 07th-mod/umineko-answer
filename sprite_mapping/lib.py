from typing import Dict


class SpriteModeLookup:
    def __init__(self):
        self.map = {} #type: Dict[str, int]

    def set_sprite_type(self, name: str, value: int):
        self.map[name] = int(value)

    def get_sprite_type(self, name: str) -> int:
        """
        The default type for a sprite is '1'
        :param name: sprite name, eg KUM
        :return: the number of the sprite
        """
        return self.map.get(name, 1)

    def reset_sprite_types(self):
        self.map.clear()


def get_old_sprite_path(name, expression, variant):
    return f'bmp\\TATI\\{name}\\{variant}\\{name}_{expression}'
