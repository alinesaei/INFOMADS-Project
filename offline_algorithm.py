from ortools.sat.python import cp_model

def offline_alg(jobs, Tt, add_interval_cuts= True, time_limit = 60):
    model = cp_model.CpModel()

    x = {}
    y = {}

    for j, job in enumerate(jobs):
        y[j] = model.NewBoolVar(f"y_{j}")
        for t in range(job["r"], job["d"] + 1):
            x[j, t] = model.NewBoolVar(f"x_{j}_{t}")
    
    for t in range(1, Tt +1):
        model.Add(sum(x[j, t] for j, job in enumerate(jobs) if (j, t) in x) <= 1)
    
    for j, job in enumerate(jobs):
        model.Add(sum(x[j, t] for t in range(job["r"], job["d"] + 1)) == job["p"] * y[j])

    if add_interval_cuts:
        for a in range(1, Tt + 1):
            for b in range(a, Tt):
                cap = b - a + 1
                expr = []
                for j, job in enumerate(jobs):
                    overlap = max(0, min(job['d'], b) - max(job['r'], a) +1)
                    if overlap >0:
                        expr.append(model.NewIntVar(0, min(job['p'], overlap), f"overlap_{j}_{a}_{b}"))
                        model.Add(expr[-1] == min(job['p'], overlap) *y[j])
                if expr:
                    model.Add(sum(expr) <= cap)

    objec = sum((job["w"] + job["l"]) * y[j] for j, job in enumerate(jobs))
    penalty = sum(job["l"] for job in jobs)
    model.Maximize(objec)

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 8
    if time_limit:
        solver.parameters.max_time_in_seconds = time_limit
    
    status = solver.Solve(model)

    schedule ={}
    completed, failed = [], []
    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        for t in range(1, Tt +1):
            schedule[t] = None
            for j, job in enumerate(jobs):
                if (j,t) in x and solver.Value(x[j,t]) == 1:
                    schedule[t] = j
        completed = [j for j in range(len(jobs)) if solver.Value(y[j]) == 1]
        failed = [j for j in range(len(jobs)) if j not in completed]
        profit = solver.Value(objec) - penalty
    else:
        profit = -penalty
    return schedule, completed, failed, profit
