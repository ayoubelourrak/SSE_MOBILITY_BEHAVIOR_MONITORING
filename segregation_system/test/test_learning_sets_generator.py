import sys
import pytest
sys.path.insert(0, r'../../segregation_system')
from src.learning_sets_generator import LearningSetsGenerator


@pytest.fixture
def test_config():
    return {
    "stage": "store",
    "segregation_system_ip": "0.0.0.0",
    "segregation_system_port": "6000",
    "development_system_ip": "10.8.0.2",
    "development_system_port": "6000",
    "preparation_system_ip": "10.8.0.6",
    "preparation_system_port": "5000",
    "db_name": "segregation.db",
    "max_sessions": 400,
    "train_set_size": 0.7,
    "validation_set_size": 0.2,
    "test_set_size": 0.1
}

@pytest.fixture
def test_dataset():
    return [
        {
            "_id" : "wrwewr-ewrewr-werwrew-werrwe",
            "calendar" : "shopping",
            "environment" : "slippery",
            "label" : "Regular",
            "features" : 
            {
                "maximum_pressure_ts" : 0.0,
                "minimum_pressure_ts" : 0.0,
                "median_pressure_ts" : 0.0,
                "mean_absolute_deviation_pressure_ts" : 0.0,
                "activity_and_small_scatter" : 0.0,
                "environment_and_small_scatter" : 0.0
            }
        },
        {
            "_id" : "wrwewr-ewrewr-werwrew-werrwe",
            "calendar" : "shopping",
            "environment" : "slippery",
            "label" : "Regular",
            "features" : 
            {
                "maximum_pressure_ts" : 0.0,
                "minimum_pressure_ts" : 0.0,
                "median_pressure_ts" : 0.0,
                "mean_absolute_deviation_pressure_ts" : 0.0,
                "activity_and_small_scatter" : 0.0,
                "environment_and_small_scatter" : 0.0
            }
        },
        {
            "_id" : "wrwewr-ewrewr-werwrew-werrwe",
            "calendar" : "shopping",
            "environment" : "slippery",
            "label" : "Regular",
            "features" : 
            {
                "maximum_pressure_ts" : 0.0,
                "minimum_pressure_ts" : 0.0,
                "median_pressure_ts" : 0.0,
                "mean_absolute_deviation_pressure_ts" : 0.0,
                "activity_and_small_scatter" : 0.0,
                "environment_and_small_scatter" : 0.0
            }
        },
        {
            "_id" : "wrwewr-ewrewr-werwrew-werrwe",
            "calendar" : "shopping",
            "environment" : "slippery",
            "label" : "Regular",
            "features" : 
            {
                "maximum_pressure_ts" : 0.0,
                "minimum_pressure_ts" : 0.0,
                "median_pressure_ts" : 0.0,
                "mean_absolute_deviation_pressure_ts" : 0.0,
                "activity_and_small_scatter" : 0.0,
                "environment_and_small_scatter" : 0.0
            }
        },
        {
            "_id" : "wrwewr-ewrewr-werwrew-werrwe",
            "calendar" : "shopping",
            "environment" : "slippery",
            "label" : "Regular",
            "features" : 
            {
                "maximum_pressure_ts" : 0.0,
                "minimum_pressure_ts" : 0.0,
                "median_pressure_ts" : 0.0,
                "mean_absolute_deviation_pressure_ts" : 0.0,
                "activity_and_small_scatter" : 0.0,
                "environment_and_small_scatter" : 0.0
            }
        },
        {
            "_id" : "wrwewr-ewrewr-werwrew-werrwe",
            "calendar" : "shopping",
            "environment" : "slippery",
            "label" : "Regular",
            "features" : 
            {
                "maximum_pressure_ts" : 0.0,
                "minimum_pressure_ts" : 0.0,
                "median_pressure_ts" : 0.0,
                "mean_absolute_deviation_pressure_ts" : 0.0,
                "activity_and_small_scatter" : 0.0,
                "environment_and_small_scatter" : 0.0
            }
        },
        {
            "_id" : "wrwewr-ewrewr-werwrew-werrwe",
            "calendar" : "shopping",
            "environment" : "slippery",
            "label" : "Regular",
            "features" : 
            {
                "maximum_pressure_ts" : 0.0,
                "minimum_pressure_ts" : 0.0,
                "median_pressure_ts" : 0.0,
                "mean_absolute_deviation_pressure_ts" : 0.0,
                "activity_and_small_scatter" : 0.0,
                "environment_and_small_scatter" : 0.0
            }
        },
        {
            "_id" : "wrwewr-ewrewr-werwrew-werrwe",
            "calendar" : "shopping",
            "environment" : "slippery",
            "label" : "Regular",
            "features" : 
            {
                "maximum_pressure_ts" : 0.0,
                "minimum_pressure_ts" : 0.0,
                "median_pressure_ts" : 0.0,
                "mean_absolute_deviation_pressure_ts" : 0.0,
                "activity_and_small_scatter" : 0.0,
                "environment_and_small_scatter" : 0.0
            }
        },
        {
            "_id" : "wrwewr-ewrewr-werwrew-werrwe",
            "calendar" : "shopping",
            "environment" : "slippery",
            "label" : "Regular",
            "features" : 
            {
                "maximum_pressure_ts" : 0.0,
                "minimum_pressure_ts" : 0.0,
                "median_pressure_ts" : 0.0,
                "mean_absolute_deviation_pressure_ts" : 0.0,
                "activity_and_small_scatter" : 0.0,
                "environment_and_small_scatter" : 0.0
            }
        },
        {
            "_id" : "wrwewr-ewrewr-werwrew-werrwe",
            "calendar" : "shopping",
            "environment" : "slippery",
            "label" : "Regular",
            "features" : 
            {
                "maximum_pressure_ts" : 0.0,
                "minimum_pressure_ts" : 0.0,
                "median_pressure_ts" : 0.0,
                "mean_absolute_deviation_pressure_ts" : 0.0,
                "activity_and_small_scatter" : 0.0,
                "environment_and_small_scatter" : 0.0
            }
        },
    ]


def test_generate_learning_sets(test_config, test_dataset):
    generator = LearningSetsGenerator(test_config)
    result = generator.generate_learning_sets(test_dataset)
    assert result["train"]["number_of_samples"] == 7
    assert result["validation"]["number_of_samples"] == 2
    assert result["test"]["number_of_samples"] == 1

    assert len(result["train"]["features"]) == 7
    assert len(result["validation"]["features"]) == 2
    assert len(result["test"]["features"]) == 1

    categories = ["train" , "validation" , "test"]

    for category in categories:
        for feature in result[category]["features"]:
            assert feature["maximum_pressure_ts"] == 0.0
            assert feature["minimum_pressure_ts"] == 0.0
            assert feature["median_pressure_ts"] == 0.0
            assert feature["mean_absolute_deviation_pressure_ts"] == 0.0
            assert feature["activity_and_small_scatter"] == 0.0
            assert feature["environment_and_small_scatter"] == 0.0
            assert feature["label"] == "Regular"
