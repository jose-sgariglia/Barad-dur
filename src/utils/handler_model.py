import os
import json
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from tensorflow.keras.models import load_model

class ModelHandler:
    @staticmethod
    def load_model_and_metadata(model_path: str):
        model = load_model(os.path.join(model_path, "model.keras"))

        with open(os.path.join(model_path, "features.json"), "r") as f:
            selected_features = json.load(f)

        with open(os.path.join(model_path, "mapping.json"), "r") as f:
            mapping = json.load(f)

        return ModelHandler(model, selected_features, mapping)

    def __init__(self, model, selected_features: list, mapping: list):
        self.model = model
        self.selected_features = selected_features
        self.mapping = mapping

    def _read_csv(self, file):
        return pd.read_csv(file)

    def _clean_data(self, data):
        data = data.dropna()
        data = data.drop_duplicates()

        float_cols = data.select_dtypes(include=['float64']).columns
        data[float_cols] = data[float_cols].round(4)
        return data

    def __one_hot_encode(self, data: pd.DataFrame):
        object_cols = data.select_dtypes(include=['object']).columns

        encoder = OneHotEncoder(sparse_output=False)
        encoded_array = encoder.fit_transform(data[object_cols])
        encoded_cols = encoder.get_feature_names_out(object_cols)
        encoded_df = pd.DataFrame(encoded_array, columns=encoded_cols)
        
        return pd.concat([data.drop(columns=object_cols).reset_index(drop=True), encoded_df.reset_index(drop=True)], axis=1)


    def __normalize_data(self, data: pd.DataFrame):
        scaler = MinMaxScaler()
        normalized_data = scaler.fit_transform(data)
        return pd.DataFrame(normalized_data, columns=data.columns)

    def predict(self, data: pd.DataFrame):
        data_array = data.to_numpy()

        print("Predicting...")
        for i, record in enumerate(data.itertuples()):
            info_packet = {
                "src_ip": record.src_ip,
                "src_port": record.src_port,
                "dest_ip": record.dest_ip,
                "dest_port": record.dest_port,
            }

            # Convert the record to a NumPy array
            record_array = data_array[i]

            # Select the features for prediction
            features = record_array[self.selected_features]

            value_pred = self.model.predict([features])[0]
            output_pred = self.mapping[value_pred]
            if output_pred != "Benign":
                print(f"Packet from {info_packet['src_ip']}:{info_packet['src_port']} to {info_packet['dest_ip']}:{info_packet['dest_port']} is classified as {output_pred}")
        
        print("Prediction complete.")


    def predict_from_file(self, file):
        data = self._read_csv(file)
        data = self._clean_data(data)
        data = self.__one_hot_encode(data)
        data = self.__normalize_data(data)
        self.predict(data)