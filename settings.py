from dataclasses import dataclass


@dataclass
class Settings:
    max_bytes: int = 2 ** 20
    bit_borders_start: int = 3
    row_width: int = 80
    bit_size: int = 10
