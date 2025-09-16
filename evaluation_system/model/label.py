class Label:

    def __init__(self, data):
        self.uuid = data["uuid"]
        self.label = data["label"]
        self.label_source = data["label_source"]

    def to_json(self):
        return {
            "uuid": self.uuid,
            "label": self.label,
            "label_source": self.label_source
        }