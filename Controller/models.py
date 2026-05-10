from dataclasses import dataclass, field
from typing import List


@dataclass
class Segment:
    name: str
    size: int
    base: int = -1  # Physical base address; -1 means not allocated


@dataclass
class Process:
    name: str
    segments: List[Segment] = field(default_factory=list)
    is_allocated: bool = False


@dataclass
class Hole:
    start: int
    size: int

    @property
    def end(self):
        return self.start + self.size


@dataclass
class AllocatedBlock:
    start: int
    size: int
    process_name: str
    segment_name: str

    @property
    def end(self):
        return self.start + self.size
