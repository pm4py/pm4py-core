

def fetch_labels(log, key):
    labels = []
    for t in log:
        for e in t:
            if e[key] not in labels:
                labels.append(e[key])
    return labels
