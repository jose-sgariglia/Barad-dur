import os
import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from tensorflow.keras.models import load_model


class ModelHandler:
    def __init__(self, model, selected_features: list, mapping: list):
        self.model = model
        self.selected_features = selected_features
        self.mapping = mapping


    @staticmethod
    def load_model_and_metadata(model_path: str):
        model = load_model(os.path.join(model_path, "model.keras"))

        with open(os.path.join(model_path, "features.json"), "r") as f:
            selected_features = json.load(f)

        with open(os.path.join(model_path, "mapping.json"), "r") as f:
            mapping = json.load(f)

        return ModelHandler(model, selected_features, mapping)


    def _read_csv(self, file):
        return pd.read_csv(file)


    def _clean_data(self, data: pd.DataFrame):
        print("Cleaning data...\t", end="")

        data.replace([np.inf, -np.inf], np.nan, inplace=True)
        data.drop_duplicates(inplace=True)

        float_cols = data.select_dtypes(include=['float64']).columns
        data[float_cols] = data[float_cols].round(4)

        print("Cleaning complete.")
        return data
    

    def __one_hot_encode(self, data: pd.DataFrame):
        print("One-hot encoding data...\t", end="")

        object_cols = data.select_dtypes(include=['object']).columns

        encoder = OneHotEncoder(sparse_output=False)
        encoded_array = encoder.fit_transform(data[object_cols])
        encoded_cols = encoder.get_feature_names_out(object_cols)
        encoded_df = pd.DataFrame(encoded_array, columns=encoded_cols)
        
        data = pd.concat([data.drop(columns=object_cols).reset_index(drop=True), encoded_df.reset_index(drop=True)], axis=1)

        print("One-hot encoding complete.")
        return data
    

    def __normalize_data(self, data: pd.DataFrame):
        print("Normalizing data...\t", end="")

        scaler = MinMaxScaler()
        normalized_data = scaler.fit_transform(data)
        data = pd.DataFrame(normalized_data, columns=data.columns)

        print("Normalization complete.")
        return data


    def predict(self, data: pd.DataFrame):
        if not hasattr(self, "selected_features") or not self.selected_features:
            raise ValueError("selected_features non definito o vuoto.")

        if not isinstance(data, pd.DataFrame):
            raise ValueError("L'input deve essere un DataFrame di Pandas.")

        missing_features = [feat for feat in self.selected_features if feat not in data.columns]
        if missing_features:
            raise ValueError(f"Le seguenti feature mancano nel DataFrame: {missing_features}")

        features_data = data[self.selected_features].to_numpy()

        print("Starting prediction")

        predictions = self.model.predict(features_data)

        for i, value_pred in enumerate(predictions):
            if value_pred >= len(self.mapping) or value_pred < 0:
                raise ValueError(f"Il valore predetto {value_pred} è fuori dall'intervallo valido per la lista mapping.")

            output_pred = self.mapping[int(value_pred)]
            if output_pred != "Benign":
                print(f"Alert: Potential attack detected in record {i + 1}")

        print("Prediction complete.")


    def predict_from_file(self, file):
        data = self._read_csv(file)
        data = self._clean_data(data)
        data = self.__one_hot_encode(data)
        data = self.__normalize_data(data)
        self.predict(data)