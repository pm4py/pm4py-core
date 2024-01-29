import pm4py
from pm4py.algo.transformation.log_to_features import algorithm
import random
import numpy as np
from pm4py.util import ml_utils


def execute_script():
    log = pm4py.read_xes("../tests/input_data/receipt.xes", return_legacy_log_object=True)

    # train a predictor of the throughput timebased on the attributes at the case level (known at the beginning of the case)

    data, feature_names = algorithm.apply(log,
                                          parameters={"str_tr_attr": ["channel", "group", "responsible", "department"],
                                                      "str_ev_attr": [], "num_tr_attr": [], "num_ev_attr": [],
                                                      "str_evsucc_attr": []})
    data = [np.array(x) for x in data]

    throughput_time = [y[-1]["time:timestamp"].timestamp() - y[0]["time:timestamp"].timestamp() for y in log]

    # split the cases in training and test

    available_cases = [i for i in range(len(log))]
    training_cases = set(random.sample(available_cases, 500))
    data_training = [data[i] for i in range(len(log)) if i in training_cases]
    data_training = np.array(data_training)

    throughput_time_training = [throughput_time[i] for i in range(len(log)) if i in training_cases]

    # train the regressor

    regressor = ml_utils.KNeighborsRegressor(n_neighbors=3)
    regressor.fit(data_training, throughput_time_training)

    data_validation = [data[i] for i in range(len(log)) if i not in training_cases]
    throughput_time_validation = [throughput_time[i] for i in range(len(log)) if i not in training_cases]

    # apply the predictor on the validation dataset and compare it with the actual throughput time
    predicted_throughput_time = regressor.predict(data_validation)

    for i in range(len(throughput_time_validation)):
        print("case actual throughput=", throughput_time_validation[i], " predicted throughput = ",
              predicted_throughput_time[i])


if __name__ == "__main__":
    execute_script()
