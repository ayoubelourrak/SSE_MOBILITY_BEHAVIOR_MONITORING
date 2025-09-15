from model.classifier import Classifier


class ClassifyController:
    labels_int_to_human = {
        "0.0" : "Regular",
        "1.0" : "Anomalous"
    }

    def __init__(self):
        self._prepared_session = None
        self._classifier = Classifier.get_instance()

    def load_classifier(self):
        self._classifier.load()
        print(self._classifier)

    def to_string(self):
        return self._classifier.to_string()

    def load_prepared_session(self, prepared_session):
        self._prepared_session = prepared_session

    def classify(self):
        classify_raw_result = self._classifier.predict_label(self._prepared_session.to_dataset())
        print(f"[DEBUG] classify_raw_result: {classify_raw_result}")
        #human_label = self.labels_int_to_human[str(classify_raw_result[0])]
        self._prepared_session.add_human_output(classify_raw_result[0])
        return self._prepared_session.to_json()
