from typing import Dict, List, Tuple
from ortools.sat.python import cp_model
from .data_models import Job, ScheduleResult


def _overlap_len(a1: int, b1: int, a2: int, b2: int) -> int:
    """Length (in unit slots) of the intersection of [a1,b1] and [a2,b2], inclusive."""
    lo = max(a1, a2)
    hi = min(b1, b2)
    return max(0, hi - lo + 1)


def solve_offline_optimal_cp_sat(
    jobs: List[Job],
    T_max: int,
    add_interval_cuts: bool = True,
    max_seconds: float | None = None,
) -> ScheduleResult:
    """
    Offline optimal schedule via time-indexed 0–1 ILP solved with OR-Tools CP-SAT.

    - Time slots are 1..T_max (inclusive).
    - Variables:
        x[j,t] in {0,1}  -> job j runs in slot t
        y[j]   in {0,1}  -> job j is finished
    - Constraints:
        capacity per slot, window feasibility, completion link.
        Optional: interval (demand-bound) cuts for all [a,b] subsets.
    - Objective:
        maximize sum_j (w_j + l_j) * y[j]    (constant shift -sum l_j added to report profit).
    """
    model = cp_model.CpModel()

    # Build x-variables only where slots are feasible (inside [r_j, d_j])
    x: Dict[Tuple[int, int], cp_model.IntVar] = {}
    y: Dict[int, cp_model.IntVar] = {}

    for j in jobs:
        y[j.id] = model.NewBoolVar(f"y_{j.id}")
        for t in range(max(1, j.r_j), min(T_max, j.d_j) + 1):
            x[(j.id, t)] = model.NewBoolVar(f"x_{j.id}_{t}")

    # 1) Capacity: at most one job per time slot
    for t in range(1, T_max + 1):
        vars_in_t = [x[(j.id, t)] for j in jobs if (j.id, t) in x]
        if vars_in_t:
            model.Add(sum(vars_in_t) <= 1)

    # 2) Completion link per job: sum_t x[j,t] = p_j * y[j]
    for j in jobs:
        vars_for_j = [x[(j.id, t)] for t in range(1, T_max + 1) if (j.id, t) in x]
        if vars_for_j:
            model.Add(sum(vars_for_j) == j.p_j * y[j.id])
        else:
            # No feasible slots: force unfinished
            model.Add(y[j.id] == 0)

    # 3) Optional: interval (demand-bound) cuts for all [a,b]
    #    Sum_j min{p_j, |window_j ∩ [a,b]|} * y_j <= |[a,b]|  for all intervals [a,b]
    if add_interval_cuts:
        for a in range(1, T_max + 1):
            for b in range(a, T_max + 1):
                cap = b - a + 1
                coeffs, vars_y = [], []
                for j in jobs:
                    overlap = _overlap_len(j.r_j, j.d_j, a, b)
                    if overlap > 0:
                        coeffs.append(min(j.p_j, overlap))
                        vars_y.append(y[j.id])
                if vars_y:
                    # sum coeffs_i * y_i <= cap
                    model.Add(sum(c * v for c, v in zip(coeffs, vars_y)) <= cap)

    # Objective: maximize sum (w_j + l_j) * y_j  (we add -sum l_j to report profit)
    objective_terms = []
    total_penalty_const = 0
    for j in jobs:
        objective_terms.append((j.w_j + j.l_j, y[j.id]))
        total_penalty_const += j.l_j

    model.Maximize(sum(c * v for c, v in objective_terms))

    # Solver parameters
    solver = cp_model.CpSolver()
    # faster, deterministic-ish settings
    solver.parameters.num_search_workers = 8
    if max_seconds is not None:
        solver.parameters.max_time_in_seconds = float(max_seconds)
    # We want proven optimality when time permits
    solver.parameters.cp_model_presolve = True

    status = solver.Solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        # No feasible schedule (should not happen under our modeling; return empty)
        return ScheduleResult(schedule={}, completed_jobs=set(), failed_jobs=set(), total_profit=-total_penalty_const)

    # Extract schedule: for each slot pick the job with x=1
    schedule: Dict[int, int] = {}
    for (jid, t), var in x.items():
        if solver.Value(var) == 1:
            schedule[t] = jid

    # Completed / failed sets from y
    completed_jobs = {j.id for j in jobs if solver.Value(y[j.id]) == 1}
    all_ids = {j.id for j in jobs}
    failed_jobs = all_ids - completed_jobs

    # True objective value (reward - penalties)
    profit_shifted = int(round(solver.ObjectiveValue()))
    total_profit = profit_shifted - total_penalty_const

    return ScheduleResult(schedule=schedule,
                          completed_jobs=completed_jobs,
                          failed_jobs=failed_jobs,
                          total_profit=total_profit)
