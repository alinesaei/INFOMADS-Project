from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class Job:
    """Represents a single job with its properties."""
    id: int
    p_j: int  # processing time
    r_j: int  #release time
    d_j: int  #deadline
    w_j: int  #reward
    l_j: int  #penalty

    # State for the simulation
    remaining_p_j: int = field(init=False)

    def __post_init__(self):
        # init remaining processing tim
        self.remaining_p_j = self.p_j


@dataclass
class ScheduleResult:
    """scheduling output storing"""
    schedule: Dict[int, int]  # Timeslot -> Job ID
    completed_jobs: set[int]
    failed_jobs: set[int]
    total_profit: int


@dataclass
class ParsedInstance:
    """stores parsed instance data"""
    name: str
    jobs: List[Job]
    T_max: int
    offline_schedule: Dict[int, List[int]]
    offline_profit: int