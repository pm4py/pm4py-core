

def fetch_labels(log, key):
    labels = []
    for t in log:
        for e in t:
            if key in e and e[key] not in labels:
                labels.append(e[key])
    return labels
