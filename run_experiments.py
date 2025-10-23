import random
import matplotlib.pyplot as plt
from offline_algorithm import offline_alg
from online_algorithms import EDF, EDF_threshold, EDF_replacement



def random_jobs(n, T=50, seed = None):
    if seed:
        random.seed(seed)
    jobs = []
    for _ in range(n):
        r = random.randint(1, T//2)
        p = random.randint(1, 5)
        d = min(T, r + random.randint(5, 15))
        w = random.randint(1, 100)
        l = random.randint(5, 50)
        jobs.append({'r': r, 'p': p, 'd': d, 'w': w, 'l': l})
    return jobs

def evaluate_algorithms(jobs_list = [10,20,50], T=50):
    results = {'EDF':[], 'EDF Threshold':[], 'EDF Replacement':[]}
    
    for n in jobs_list:
        jobs = random_jobs(n, T)
        _, _, _, opt_profit = offline_alg(jobs, Tt=T, time_limit=60)

        edf = EDF(jobs, T)
        threshold = EDF_threshold(jobs, T)
        replacement = EDF_replacement(jobs, T)

        results['EDF'].append(edf / opt_profit if opt_profit else 0)
        results['EDF Threshold'].append(threshold / opt_profit if opt_profit else 0)
        results['EDF Replacement'].append(replacement / opt_profit if opt_profit else 0)

        print(f"Jobs: {n}, Optimal: {opt_profit:.1f}, EDF: {edf:.1f}, Threshold: {threshold:.1f}, Replacement: {replacement:.1f}")

    plt.plot(jobs_list, results['EDF'], label='EDF')
    plt.plot(jobs_list, results['EDF Threshold'], label = 'EDF Threshold')
    plt.plot(jobs_list, results['EDF Replacement'], label = 'EDF Replacement')
    plt.xlabel('Number of Jobs')
    plt.ylabel('Profit Ratio to Optimal')
    plt.title('Online Algorithms Performance')
    plt.legend()
    plt.show()
    plt.grid(True)

def evaluate_algorithms_manual():
    # results = {'EDF':[], 'EDF Threshold':[], 'EDF Replacement':[]}
    
    manual_jobs = [
        {'r': 1, 'd': 9, 'p': 4, 'w': 10, 'l': 10},   # j1
        {'r': 3, 'd': 5, 'p': 2, 'w': 10, 'l': 15},   # j2
        {'r': 2, 'd': 7, 'p': 5, 'w': 10, 'l': 5},    # j3
        {'r': 6, 'd': 7, 'p': 2, 'w': 1,  'l': 100},  # j4
        {'r': 2, 'd': 3, 'p': 1, 'w': 3,  'l': 1}     # j5
    ]
    T = 10
    _, _, _, opt_profit = offline_alg(manual_jobs, Tt=T, time_limit=60)

    edf = EDF(manual_jobs, T)
    threshold = EDF_threshold(manual_jobs, T)
    replacement = EDF_replacement(manual_jobs, T)

    print("\nManual Test Case Results:")
    print("-------------------------")
    print(f"\n--- Jobs={len(manual_jobs)} --- ")
    print(f"Jobs: {len(manual_jobs)}, Optimal: {opt_profit:.1f}, EDF: {edf:.1f}, Threshold: {threshold:.1f}, Replacement: {replacement:.1f}")

    ratios = [edf/opt_profit, threshold/opt_profit, replacement/opt_profit]
    labels = ['EDF', 'EDF Threshold', 'EDF Replacement']
    plt.bar(labels, ratios)
    plt.ylim(0, 1.2)
    plt.xlabel('Number of Jobs')
    plt.ylabel('Profit Ratio to Optimal')
    plt.title('Online Algorithms Performance')
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    evaluate_algorithms()
    evaluate_algorithms_manual()