import re
from typing import Dict, List
from core.data_models import Job, ParsedInstance


def parse_test_instances(file_content: str) -> Dict[str, ParsedInstance]:
    instances = {}
    blocks = re.split(r'Test [Ii]nstance (.+?):', file_content)

    if len(blocks) < 3:
        return {}

    for i in range(1, len(blocks), 2):
        instance_name_part = blocks[i].strip()
        instance_data = blocks[i + 1].strip()

        name = f"Test Instance {instance_name_part}"
        lines = [line for line in instance_data.split('\n') if line.strip()]

        try:
            num_jobs = int(lines[0])
            job_lines = lines[1: 1 + num_jobs]
            schedule_lines = lines[1 + num_jobs: 1 + num_jobs * 2]
            profit_line = lines[-1]

            # Parse jobs
            jobs = []
            max_deadline = 0
            for idx, line in enumerate(job_lines):
                parts = [p.strip() for p in line.split(',')]
                p, d, r, w, l = map(int, parts)
                jobs.append(Job(id=idx + 1, p_j=p, r_j=r, d_j=d, w_j=w, l_j=l))
                if d > max_deadline:
                    max_deadline = d

            # parse offline schedule (for comparison)
            offline_schedule = {}
            for idx, line in enumerate(schedule_lines):
                job_id = idx + 1
                if 'null' not in line.lower():
                    slots = list(map(int, line.replace(',', ' ').split()))
                    offline_schedule[job_id] = slots

            offline_profit = int(profit_line)

            T_max = max(d for d in [job.d_j for job in jobs] + [10])

            instances[name] = ParsedInstance(
                name=name,
                jobs=jobs,
                T_max=T_max,
                offline_schedule=offline_schedule,
                offline_profit=offline_profit
            )
        except (ValueError, IndexError) as e:
            print(f"couldnt' parse block for instance '{name}' -  errror: {e}")
            continue

    return instances