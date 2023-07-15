import pm4py
import numpy as np
import scipy.stats as stats


def check_exponential_distribution(name, your_data):
    print("\n\n### Testing exponential distribution for: "+name+"\n\n")

    your_data = np.array(your_data)

    lambda_ = 1. / your_data.mean()

    # KS test
    D, p_value = stats.kstest(your_data, "expon", args=(0, 1. / lambda_))
    print(f"KS test statistic: {D}")
    print(f"p-value: {p_value}")

    # Anderson-Darling test
    result = stats.anderson(your_data, dist='expon')
    print(f"AD test statistic: {result.statistic}")
    for i in range(len(result.critical_values)):
        sl, cv = result.significance_level[i], result.critical_values[i]
        if result.statistic < cv:
            print(f"Significance level: {sl} : data looks like an exponential distribution (fail to reject H0)")
        else:
            print(f"Significance level: {sl} : data does not look like an exponential distribution (reject H0)")


def execute_script():
    epsilon = 0.0001
    log = pm4py.read_xes('../tests/input_data/receipt.xes', return_legacy_log_object=True)
    time_intervals = pm4py.convert_log_to_time_intervals(log, ('Confirmation of receipt', 'T02 Check confirmation of receipt'))
    service_times = [min(x[1]-x[0], epsilon) for x in time_intervals]
    arrival_diffs = []
    i = 0
    while i < len(time_intervals)-1:
        arrival_diffs.append(max(time_intervals[i+1][0]-time_intervals[i][0], epsilon))
        i = i + 1

    check_exponential_distribution("service_times", service_times)
    check_exponential_distribution("arrival_diffs", arrival_diffs)


if __name__ == "__main__":
    execute_script()
