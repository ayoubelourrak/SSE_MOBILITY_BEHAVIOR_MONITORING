import os
import math
from model.classifier import Classifier
from model.classifier_configuration import ClassifierConfiguration
from model.dataset import Dataset
from utils.json_reader import JsonReader
from generator.learning_report_generator import LearningReportGenerator
from config.constants import HYPER_PARAMS_FILE_PATH

class TrainingManager:

    def __init__(self):
        self._classifier = Classifier()
        self._train_data = None
        self._iterations_number = 0
        self._hidden_layer_sizes = []

    def set_average_hyperparameters(self):
        read_result , file_content = JsonReader.read_json_file(HYPER_PARAMS_FILE_PATH)
        if not read_result:
            return
        #iterations_number = file_content["iterations-number"]
        hidden_layer_size_range = list(map(int,os.getenv("LAYER_RANGE").split(",")))
        hidden_neuron_range = list(map(int,os.getenv("NEURON_RANGE").split(",")))

        # get the average hyperparameters
        average_layers = int((hidden_layer_size_range[1] + hidden_layer_size_range[0]) / 2)
        average_neurons = int((hidden_neuron_range[1] + hidden_neuron_range[0]) / 2)

        # get the sizes of hidden layers with descending logarithmic number of neurons
        self._hidden_layer_sizes = tuple([math.ceil(average_neurons / (2 ** i)) for i in range(average_layers)])
        print(f'The Early Training Network has this hidden layer sizes: {self._hidden_layer_sizes}')
        self._classifier.update_configuration(ClassifierConfiguration(hidden_layer_sizes=self._hidden_layer_sizes))

    def update_iterations_number(self, iterations):
        self._iterations_number = iterations
        self._classifier.update_configuration(ClassifierConfiguration(self._iterations_number , self._hidden_layer_sizes))

    def train_classifier(self):
        self._train_data = Dataset.get_data("train")
        self._classifier.train_classifier(
                    self._train_data["data"],
                    self._train_data["labels"],
        )
    def get_classifier_losses(self):
        return self._classifier.get_losses()

    def generate_learning_report(self):
        LearningReportGenerator(self.get_classifier_losses())