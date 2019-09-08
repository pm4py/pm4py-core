from prefixspan import PrefixSpan
import fasttext
import tempfile

M = "m"
DEFAULT_M = 2

FINAL_LABEL_IDX = "final_label_idx"
DEFAULT_FINAL_LABEL_IDX = "@@label_index"


def apply(grouped_stream, all_labels, parameters=None):
    """
    Applies the prefix span algorithm

    Parameters
    -------------
    grouped_stream
        Grouped stream
    all_labels
        Indexed labels
    parameters
        All the parameters of the algorithm

    Returns
    --------------
    frequents
        List containing frequent itemsets as label indexes
    frequents_label
        List containing frequent itemsets as labels
    frequents_encodings
        List containing frequent itemsets as word encodings
    frequents_occurrences
        List containing all the sequences of events associated to the corresponding itemset
    """
    if parameters is None:
        parameters = {}

    final_label_idx = parameters[FINAL_LABEL_IDX] if FINAL_LABEL_IDX in parameters else DEFAULT_FINAL_LABEL_IDX

    m = parameters[M] if M in parameters else DEFAULT_M

    data = [[y[final_label_idx] for y in x] for x in grouped_stream]
    ps = PrefixSpan(data)

    frequents = [x[1] for x in ps.frequent(m)]
    frequents_label = [" ".join([all_labels[y] for y in x]) for x in frequents]

    F = tempfile.NamedTemporaryFile(suffix='.txt')
    F.close()
    F2 = open(F.name, "w")
    for label in frequents_label:
        F2.write(label+"\n")
    F2.close()

    model = fasttext.train_unsupervised(F.name)
    frequents_encodings = []
    for i in range(len(frequents)):
        phrase = [x for x in frequents_label[i].split() if x in model.words]
        v = None
        for w in phrase:
            if v is None:
                v = model.get_word_vector(w)
            else:
                v = v + model.get_word_vector(w)
        frequents_encodings.append(v)

    frequents_occurrences = []
    for f in frequents:
        frequents_occurrences.append([])
        for g in grouped_stream:
            d = [x[final_label_idx] for x in g]
            for i in range(len(d)-len(f)):
                if d[i] == f[0] and d[i+len(f)-1] == f[len(f)-1]:
                    if d[i:i+len(f)] == f:
                        frequents_occurrences[-1].append(g[i:i+len(f)])

    return frequents, frequents_label, frequents_encodings, frequents_occurrences
