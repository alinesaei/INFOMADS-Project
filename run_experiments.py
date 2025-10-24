import random
import matplotlib.pyplot as plt
from offline_algorithm import offline_alg
from online_algorithms import EDF, EDF_threshold, EDF_replacement



def randomJobs(n, T=50, seed = None):
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
        jobs = randomJobs(n, T)
        # Get optimal profit from offline algorithm
        _, _, _, optimalProfit = offline_alg(jobs, Tt=T, add_interval_cuts= False, time_limit=60)

        edf = EDF(jobs, T)
        threshold = EDF_threshold(jobs, T, a=1.0)
        replacement = EDF_replacement(jobs, T)

        results['EDF'].append(edf / optimalProfit if optimalProfit else 0)
        results['EDF Threshold'].append(threshold / optimalProfit if optimalProfit else 0)
        results['EDF Replacement'].append(replacement / optimalProfit if optimalProfit else 0)

        print(f"Jobs: {n}, Optimal: {optimalProfit:.1f}, EDF: {edf:.1f}, Threshold: {threshold:.1f}, Replacement: {replacement:.1f}")

    plt.plot(jobs_list, results['EDF'], label='EDF')
    plt.plot(jobs_list, results['EDF Threshold'], label = 'EDF Threshold')
    plt.plot(jobs_list, results['EDF Replacement'], label = 'EDF Replacement')
    plt.xlabel('Number of Jobs')
    plt.ylabel('Profit Ratio to Optimal')
    plt.title('Online Algorithms Performance')
    plt.legend()
    plt.show()
    plt.grid(True)

def evaluateAlgorithms():
    
    manualJobs = [
        {'r': 1, 'd': 9, 'p': 4, 'w': 10, 'l': 10},   
        {'r': 3, 'd': 5, 'p': 2, 'w': 10, 'l': 15},   
        {'r': 2, 'd': 7, 'p': 5, 'w': 10, 'l': 5},    
        {'r': 6, 'd': 7, 'p': 2, 'w': 1,  'l': 100},  
        {'r': 2, 'd': 3, 'p': 1, 'w': 3,  'l': 1}     
    ]
    T = 10
    # Get optimal profit from offline algorithm
    _, _, _, optimalProfit = offline_alg(manualJobs, Tt=T, add_interval_cuts= False, time_limit=60)

    edf = EDF(manualJobs, T)
    threshold = EDF_threshold(manualJobs, T, a=1.0)
    replacement = EDF_replacement(manualJobs, T)

    manualJobsLength=len(manualJobs)

    print(f"\nManual Test Case Results:")
    print(f"\n Jobs={manualJobsLength}  ")
    print(f"Jobs: {manualJobsLength}, Optimal: {optimalProfit:.1f}, EDF: {edf:.1f}, Threshold: {threshold:.1f}, Replacement: {replacement:.1f}")

    ratios = [edf/optimalProfit, threshold/optimalProfit, replacement/optimalProfit]
    labels = ['EDF', 'EDF_Threshold', 'EDF_Replacement']
    plt.bar(labels, ratios)
    plt.ylim(-6.0, 1.2)
    plt.xlabel('Jobs')
    plt.ylabel('Profit Ratio versus Optimal')
    plt.title('Online Algorithms Performance')
    plt.legend(["EDF", "EDF_Threshold", "EDF_Replacement"])
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    evaluate_algorithms()
    evaluateAlgorithms()