import math

def EDF(jobs, T):
    total = 0
    completed = set()
    available_jobs = []
    remaining_jobs = {j: jobs[j]['p'] for j in range(len(jobs))}

    for t in range(1, T + 1):
        # Add new jobs
        for j, job in enumerate(jobs):
            if job['r'] == t:
                available_jobs.append(j)

        # Filter jobs
        available_jobs = [j for j in available_jobs if t < jobs[j]['d'] and j not in completed]

        if available_jobs:
            #jobs with earliest deadline
            exe_j = min(available_jobs, key = lambda j: jobs[j]['d'])
            remaining_jobs[exe_j] -= 1

            # calculate total completed jobs
            if remaining_jobs[exe_j] == 0:
                completed.add(exe_j)
                total += jobs[exe_j]['w']
        
        # missed jobs
        for j in available_jobs:
            if t == jobs[j]['d'] and j not in completed:
                total -= jobs[j]['l']
    
    return total
def EDF_threshold(jobs, T, a = 1.0):
    total =0
    return total
def EDF_replacement(jobs, T):

    total = 0
    completed = set()
    available_jobs = set()
    remaining_jobs = {j: jobs[j]['p'] for j in range(len(jobs))}
    running_job = None

    for t in range(1, T + 1):
        
        for j, job in enumerate(jobs):
            if job['r'] == t:
                available_jobs.add(j)
        
        candidates = {j for j in available_jobs if remaining_jobs[j] > 0 and t + remaining_jobs[j] -1 <= jobs[j]['d']}
        if running_job is not None:
            candidates.add(running_job)

        if not candidates:
            continue
        
        def score(j):
            remain = remaining_jobs[j]
            if remain <= 0:
                return -1e9
            urgency = 1.0 / (jobs[j]['d'] - t + 1)
            return (jobs[j]['w'] + jobs[j]['l']) * urgency / remain
        
        best_job = max(candidates, key=score)

        if running_job != best_job:
            running_job = best_job

        remaining_jobs[running_job] -= 1
        if remaining_jobs[running_job] == 0:
            completed.add(running_job)
            total += jobs[running_job]['w']
            running_job = None
            
    for j, job in enumerate(jobs):
        if j not in completed:
            total -= job['l']

    return total

