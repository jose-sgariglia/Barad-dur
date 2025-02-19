import os
import json
import logging
import numpy as np
import pandas as pd
import tensorflow as tf

from utils.monitoring import monitor_context
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder

barad_logger = logging.getLogger("barad_logger")


class ModelHandler:
    """
    Model handler class that loads a pre-trained model and metadata to make predictions.
    """

    def __init__(self, model, selected_features: list, mapping: list):
        self.model = model
        self.selected_features = selected_features
        self.mapping = mapping


    @staticmethod
    def load_model_and_metadata(model_path: str):
        """
        Load the pre-trained model and metadata from the specified path.
        """
        model = tf.keras.models.load_model(os.path.join(model_path, "model.keras"))

        with open(os.path.join(model_path, "features.json"), "r") as f:
            selected_features = json.load(f)

        with open(os.path.join(model_path, "mapping.json"), "r") as f:
            mapping = json.load(f)

        return ModelHandler(model, selected_features, mapping)


    def _read_csv(self, file):
        """
        Read the CSV file and return a Pandas DataFrame.
        """

        return pd.read_csv(file)


    def _clean_data(self, data: pd.DataFrame):
        """
        Clean the data by removing duplicates and replacing infinite values.
        """
        barad_logger.info("[MDL] Cleaning data...")

        data.replace([np.inf, -np.inf], np.nan, inplace=True)
        data.drop_duplicates(inplace=True)

        float_cols = data.select_dtypes(include=['float64']).columns
        data[float_cols] = data[float_cols].round(4)

        barad_logger.info("[MDL] Data cleaning complete.")
        return data
    

    def __one_hot_encode(self, data: pd.DataFrame):
        """
        Perform one-hot encoding on the categorical columns in the data.
        """

        barad_logger.info("[MDL] One-hot encoding data...")

        object_cols = data.select_dtypes(include=['object']).columns

        encoder = OneHotEncoder(sparse_output=False)
        encoded_array = encoder.fit_transform(data[object_cols])
        encoded_cols = encoder.get_feature_names_out(object_cols)
        encoded_df = pd.DataFrame(encoded_array, columns=encoded_cols)
        
        data = pd.concat([data.drop(columns=object_cols).reset_index(drop=True), encoded_df.reset_index(drop=True)], axis=1)

        barad_logger.info("[MDL] One-hot encoding complete.")
        return data
    

    def __normalize_data(self, data: pd.DataFrame):
        """
        Normalize the data using MinMaxScaler.
        """
        barad_logger.info("[MDL] Normalizing data...")

        scaler = MinMaxScaler()
        normalized_data = scaler.fit_transform(data)
        data = pd.DataFrame(normalized_data, columns=data.columns)

        barad_logger.info("[MDL] Data normalization complete.")
        return data


    def __check_data(self, data: pd.DataFrame):
        """
        Check if the data are in the correct format and contain the selected features.
        """
        if not hasattr(self, "selected_features") or not self.selected_features:
            raise ValueError("selected_features not defined or empty.")
        
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Input must be a Pandas DataFrame.")
        
        missing_features = [feat for feat in self.selected_features if feat not in data.columns]
        if missing_features:
            raise ValueError(f"The following features are missing in the DataFrame: {missing_features}")



    def predict(self, data: pd.DataFrame):
        """
        Make predictions on the input
        """

        self.__check_data(data)
        features_data = data[self.selected_features].to_numpy()

        barad_logger.info("[MDL] Starting prediction")
        print("Starting prediction...")

        with monitor_context("MDL") as monitor:
            predictions = self.model.predict(features_data)

            for i, value_pred in enumerate(predictions):
                if value_pred >= len(self.mapping) or value_pred < 0:
                    raise ValueError(f"The predicted value {value_pred} is out of range for the mapping list.")

                output_pred = self.mapping[int(value_pred)]
                if output_pred != "Benign":
                    print(f"\x1b[31m\x1b[1m[MDL] Alert: Potential attack detected in record {i + 1}\x1b[0m")
                    barad_logger.warning(f"\x1b[31m\x1b[1m[MDL] Alert: Potential attack detected in record {i + 1}\x1b[0m")

            barad_logger.info("[MDL] Prediction complete.")
            print("Prediction complete.")


    def run(self, file):
        barad_logger.info("[MDL] Pre-processing from packet data...")
        data = self._read_csv(file)
        data = self._clean_data(data)
        data = self.__one_hot_encode(data)
        data = self.__normalize_data(data)
        barad_logger.info("[MDL] Pre-processing complete.")
        self.predict(data)