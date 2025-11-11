from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Stats:
    total: int
    successful: int
    failed: int
