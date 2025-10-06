from typing import List, Callable, Dict
from .data_models import Job, ScheduleResult
import copy


class OnlineScheduler:

    def __init__(self, jobs: List[Job], policy_func: Callable, T_max: int, policy_params: Dict = None):
        self.all_jobs = {j.id: copy.deepcopy(j) for j in jobs}
        self.policy_func = policy_func
        self.T_max = T_max
        self.policy_params = policy_params if policy_params else {}

    def run(self) -> ScheduleResult:
        schedule: Dict[int, int] = {}
        active_jobs: List[Job] = []
        job_map = {j.id: j for j in self.all_jobs.values()}

        for t in range(1, self.T_max + 1):
            # reveal new jobs
            for job in self.all_jobs.values():
                if job.r_j == t:
                    active_jobs.append(job)

            # Select a job to run using the chosen policy
            if self.policy_func.__name__ == "profit_aware_edf_policy":
                job_to_run = self.policy_func(t, active_jobs, self.policy_params)
            else:
                job_to_run = self.policy_func(t, active_jobs)

            if job_to_run:
                schedule[t] = job_to_run.id
                job_to_run.remaining_p_j -= 1

            # updat job states
            active_jobs = [j for j in active_jobs if j.remaining_p_j > 0 and j.d_j >= t]

        # final profit
        completed_jobs = {j.id for j in self.all_jobs.values() if j.remaining_p_j == 0}
        failed_jobs = set(self.all_jobs.keys()) - completed_jobs

        total_profit = sum(job_map[job_id].w_j for job_id in completed_jobs) - \
                       sum(job_map[job_id].l_j for job_id in failed_jobs)

        return ScheduleResult(schedule, completed_jobs, failed_jobs, total_profit)