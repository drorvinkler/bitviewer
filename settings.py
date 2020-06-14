from dataclasses import dataclass


@dataclass
class Settings:
    max_bytes: int = 2 ** 20
    bit_borders_start: int = 3
