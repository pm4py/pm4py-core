def translate_infix_to_regex(infix):
    regex = "^"
    for i, act in enumerate(infix):
        is_last_activity = i == (len(infix) - 1)
        if act == "...":
            if is_last_activity:
                regex = f"{regex[:-1]}(,[^,]*)*"
            else:
                regex = f"{regex}([^,]*,)*"
        else:
            if is_last_activity:
                regex = f"{regex}{act}"
            else:
                regex = f"{regex}{act},"

    regex = f"{regex}$"
    return regex
