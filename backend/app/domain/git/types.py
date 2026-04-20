from dataclasses import dataclass
from typing import Dict


@dataclass
class ContributorStats:
    contributors: Dict[str, int]
    top_contributor: str | None
    bus_factor: int