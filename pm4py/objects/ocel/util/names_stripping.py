import re


match = re.compile(r'[^0-9a-zA-Z]+')


def apply(X: str, max_len: int = 100) -> str:
    X = X.split(" ")
    i = 0
    while i < len(X):
        X[i] = X[i].capitalize()
        i = i + 1
    X = "".join(X)
    stru = match.sub('', X).strip()
    if len(stru) > max_len:
        stru = stru[:100]
    return stru
