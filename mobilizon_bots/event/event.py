from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


@dataclass
class MobilizonEvent:
    """Class representing an event retrieved from Mobilizon."""

    name: str
    description: str
    begin_datetime: datetime
    end_datetime: datetime
    last_accessed: datetime
    mobilizon_link: str
    mobilizon_id: str
    thumbnail_link: Optional[str] = None
    location: Optional[str] = None

    def _fill_template(self, pattern: str) -> str:
        return pattern.format(**asdict(self))

    def format(self, pattern: str) -> str:
        return self._fill_template(pattern)
