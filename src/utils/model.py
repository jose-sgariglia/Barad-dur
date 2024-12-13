import os
import joblib
import pandas as pd

PATH_MODEL = '../models/'
os.makedirs(PATH_MODEL, exist_ok=True)

class Model:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = None
        self.__load_model()

    def __load_model(self):
        if os.path.exists(PATH_MODEL + self.model_name):
            self.model = joblib.load(PATH_MODEL + self.model_name)
        else:
            raise FileNotFoundError(f"Model {self.model_name} not found.")

    def get_features(self):
        if hasattr(self.model, 'feature_names_in_'):
            return self.model.feature_names_in_
        else:
            raise AttributeError("The model does not have feature names information.")

    def predict(self, data: pd.DataFrame):
        return self.model.predict(data)