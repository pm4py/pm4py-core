TIMESTAMP_COLUMN = "timestamp_column"
DEFAULT_TIMESTAMP_COLUMN = "current_timestamp"


def apply(frequents_occurrences, parameters=None):
    """
    Gives a score to each sequence

    Parameters
    ------------
    frequents_occurrences
        Occurrences of each frequent itemset

    Returns
    ------------
    score
        Score for each frequent itemset
    """
    if parameters is None:
        parameters = {}

    timestamp_column = parameters[TIMESTAMP_COLUMN] if TIMESTAMP_COLUMN in parameters else DEFAULT_TIMESTAMP_COLUMN

    frequents_score = []

    for freq in frequents_occurrences:
        summ = 0.0
        for item in freq:
            summ = summ + item[-1][timestamp_column] - item[0][timestamp_column]
        frequents_score.append(summ)

    return frequents_score
