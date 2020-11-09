import datetime


def apply(dt):
    if dt.endswith("Z"):
        # Z at the end of date means UTC, but that is not ISO format.
        # Replace "Z" with "+00:00" that is also UTC
        dt = dt[:-1] + "+00:00"
    dt0 = dt.split("T")
    datepart = dt0[0].split("-")
    dt2 = dt0[1].split("+")
    hourpart = dt2[0].split(":")
    year = int(datepart[0])
    month = int(datepart[1])
    day = int(datepart[2])
    hour = int(hourpart[0])
    minute = int(hourpart[1])
    sms = hourpart[2].split(".")
    second = int(sms[0])
    if len(sms) > 1:
        microseconds = int(sms[1])*1000
    else:
        microseconds = 0

    return datetime.datetime(year, month, day, hour, minute, second, microseconds)
