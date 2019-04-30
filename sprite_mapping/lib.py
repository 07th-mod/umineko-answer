from collections import defaultdict, Counter
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


class SpriteCounter:
    def __init__(self):
        self.map = defaultdict(Counter)

    def add_value(self, key, value):
        self.map[key][value] += 1

    def add_score(self, key, value, score):
        self.map[key][value] += score

    def get_value(self, key):
        return self.map[key]


def get_old_sprite_path(name, expression, variant):
    return f'bmp\\TATI\\{name}\\{variant}\\{name}_{expression}'
