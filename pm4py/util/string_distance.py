import stringdist


def levenshtein(stru1, stru2):
    """
    Measures the Levenshtein distance between two strings

    Parameters
    ---------------
    stru1
        First string
    stru2
        Second string

    Returns
    ---------------
    levens_dist
        Levenshtein distance
    """
    return stringdist.levenshtein(stru1, stru2)
