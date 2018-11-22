import random
import numpy as np


def split(data, target, percentage=0.8):
    """
    Split 'data' and 'target' in training and test set
    according to the specified percentage

    Parameters
    -------------
    data
        Representation of the event log
    target
        Target class
    percentage
        Percentage of data to include in training

    Returns
    -------------
    data1
        Training X
    target1
        Training Y
    data2
        Test X
    target2
        Test Y
    """
    data1 = []
    target1 = []
    data2 = []
    target2 = []

    for i in range(len(data)):
        r = random.random()
        if r <= percentage:
            data1.append(data[i])
            target1.append(target[i])
        else:
            data2.append(data[i])
            target2.append(target[i])

    return data1, target1, data2, target2

    data1 = np.asarray(data1)
    target1 = np.asarray(target1)
    data2 = np.asarray(data2)
    target2 = np.asarray(target2)

    return data1, target1, data2, target2