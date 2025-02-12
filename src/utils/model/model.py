import os
import json
import time
import logging
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder

from utils.monitoring import monitor_resources

barad_logger = logging.getLogger("barad_logger")


class ModelHandler:
    def __init__(self, model, selected_features: list, mapping: list):
        self.model = model
        self.selected_features = selected_features
        self.mapping = mapping


    @staticmethod
    def load_model_and_metadata(model_path: str):
        model = tf.keras.models.load_model(os.path.join(model_path, "model.keras"))

        with open(os.path.join(model_path, "features.json"), "r") as f:
            selected_features = json.load(f)

        with open(os.path.join(model_path, "mapping.json"), "r") as f:
            mapping = json.load(f)

        return ModelHandler(model, selected_features, mapping)


    def _read_csv(self, file):
        return pd.read_csv(file)


    def _clean_data(self, data: pd.DataFrame):
        barad_logger.info("[MDL] Cleaning data...")

        data.replace([np.inf, -np.inf], np.nan, inplace=True)
        data.drop_duplicates(inplace=True)

        float_cols = data.select_dtypes(include=['float64']).columns
        data[float_cols] = data[float_cols].round(4)

        barad_logger.info("[MDL] Data cleaning complete.")
        return data
    

    def __one_hot_encode(self, data: pd.DataFrame):
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
        barad_logger.info("[MDL] Normalizing data...")

        scaler = MinMaxScaler()
        normalized_data = scaler.fit_transform(data)
        data = pd.DataFrame(normalized_data, columns=data.columns)

        barad_logger.info("[MDL] Data normalization complete.")
        return data


    def predict(self, data: pd.DataFrame):
        if not hasattr(self, "selected_features") or not self.selected_features:
            raise ValueError("selected_features not defined or empty.")

        if not isinstance(data, pd.DataFrame):
            raise ValueError("Input must be a Pandas DataFrame.")

        missing_features = [feat for feat in self.selected_features if feat not in data.columns]
        if missing_features:
            raise ValueError(f"The following features are missing in the DataFrame: {missing_features}")

        features_data = data[self.selected_features].to_numpy()

        barad_logger.info("[MDL] Starting prediction")
        time_start = time.time()
        predictions = self.model.predict(features_data)

        for i, value_pred in enumerate(predictions):
            if value_pred >= len(self.mapping) or value_pred < 0:
                raise ValueError(f"The predicted value {value_pred} is out of range for the mapping list.")

            output_pred = self.mapping[int(value_pred)]
            if output_pred != "Benign":
                barad_logger.warning(f"\x1b[31m\x1b[1m[MDL] Alert: Potential attack detected in record {i + 1}\x1b[0m")

        barad_logger.info("[MDL] Prediction complete.")

        time_end = time.time()
        cpu_usage, memory_usage = monitor_resources()


        barad_logger.debug(f"[MDL] Prediction latency: {time_end - time_start:.3f} seconds.")
        barad_logger.debug(f"[MDL] Prediction throughput: {len(predictions) / (time_end - time_start):.3f} packets/second.")
        barad_logger.debug(f"[MDL] CPU usage: {cpu_usage:.2f}% | RAM usage: {memory_usage:.2f}%.")


    def predict_from_file(self, file):
        barad_logger.info("[MDL] Pre-processing from packet data...")
        data = self._read_csv(file)
        data = self._clean_data(data)
        data = self.__one_hot_encode(data)
        data = self.__normalize_data(data)
        barad_logger.info("[MDL] Pre-processing complete.")
        self.predict(data)