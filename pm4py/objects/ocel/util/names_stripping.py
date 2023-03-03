import re


match = re.compile(r'[^0-9a-zA-Z]+')


def apply(x: str, max_len: int = 100) -> str:
    stru = match.sub('', x)
    if len(stru) > max_len:
        stru = stru[:100]
    return stru
