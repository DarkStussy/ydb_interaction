from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class PoolConfig:
    size: int = 100
    workers_threads_count: int = 4
    initializer = None
    min_pool_size: int = 0

    def to_dict(self):
        return asdict(self)
