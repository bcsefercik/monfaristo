from enum import Enum


class ChoiceEnum(Enum):
    """Simple Enum that has a choices option"""

    @classmethod
    def choices(cls):
        return tuple((prop.name, prop.value) for prop in cls)
