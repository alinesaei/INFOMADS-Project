from typing import List, Optional
from .data_models import Job


def edf_policy(current_time: int, active_jobs: List[Job]) -> Optional[Job]:
    eligible_jobs = [j for j in active_jobs if j.remaining_p_j > 0 and j.d_j >= current_time]
    if not eligible_jobs:
        return None

    eligible_jobs.sort(key=lambda j: (j.d_j, j.id))
    return eligible_jobs[0]


def profit_aware_edf_policy(current_time: int, active_jobs: List[Job], params: dict) -> Optional[Job]:
    eligible_jobs = [j for j in active_jobs if j.remaining_p_j > 0 and j.d_j >= current_time]
    if not eligible_jobs:
        return None
    def calculate_score(job: Job) -> float:
        profit_potential = job.w_j + job.l_j
        urgency = job.d_j
        return (params.get('w_profit', 1.0) * profit_potential) - (params.get('w_deadline', 0.1) * urgency)

    eligible_jobs.sort(key=lambda j: calculate_score(j), reverse=True)
    return eligible_jobs[0]
ONLINE_POLICIES = {
    "Earliest Deadline First (EDF)": edf_policy,
    "Profit-Aware EDF": profit_aware_edf_policy
}