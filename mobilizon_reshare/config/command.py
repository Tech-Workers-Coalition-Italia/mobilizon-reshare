import dataclasses


@dataclasses.dataclass
class CommandConfig:
    dry_run: bool = dataclasses.field(default=False)
