import numpy as np
import pm4py
from pm4py.algo.transformation.log_to_features.variants import event_based
from pm4py.algo.transformation.log_to_target.variants import next_activity
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, TimeDistributed


def execute_script():
    log = pm4py.read_xes("../tests/input_data/running-example.xes", return_legacy_log_object=True)

    data, feature_names = event_based.apply(log)
    target, classes = next_activity.apply(log, parameters={"enable_padding": True})
    target = np.array(target)

    model = Sequential()
    model.add(LSTM(50, input_shape=(data.shape[1], data.shape[2]), return_sequences=True))
    model.add(TimeDistributed(Dense(len(classes), activation='softmax')))

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    model.summary()

    # train the model
    model.fit(data, target, epochs=100)

    # test the model on an event log (in this case the same)

    # re-extract the features
    data, feature_names = event_based.apply(log, parameters={"feature_names": feature_names})

    # perform the prediction
    predictions = model.predict(data)
    predictions = [[classes[np.argmax(y)] for y in x] for x in predictions]

    print(predictions)


if __name__ == "__main__":
    execute_script()
