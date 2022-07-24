# This algorithm was copied at 16/Nov/2018 from
# https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python and applied to activity
# sequences
delimiter = "@"


def length(s):
    return s.count(delimiter) + 1


def enumerateSequence(s):
    list = s.split(delimiter)
    return enumerate(list, 0)


def trace_levenshtein(s1, s2):
    if length(s1) < length(s2):
        return trace_levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if length(s2) == 0:
        return length(s1)

    previous_row = range(length(s2) + 1)
    for i, c1 in enumerateSequence(s1):
        current_row = [i + 1]
        for j, c2 in enumerateSequence(s2):
            insertions = previous_row[
                             j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]
