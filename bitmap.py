from dataclasses import dataclass
from typing import List


@dataclass
class Bitmap:
    data: bytes
    width: int
    bytes_per_row: int
    remainder: List[bool]
