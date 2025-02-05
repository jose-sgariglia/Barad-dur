import os
import argparse

MODELS_DIR = "../models"
FILE_DIR = "../suricata_env/captures"

class ValidateModelPath(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        model_path = os.path.join(MODELS_DIR, values) 
        
        if not os.path.exists(model_path):
            raise argparse.ArgumentTypeError(f"The model '{values}' doesn't exist at '{model_path}'.")

        setattr(namespace, self.dest, model_path)


class ValidateFilePath(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        file_path = os.path.join(FILE_DIR, values) 
        
        if not os.path.exists(file_path):
            raise argparse.ArgumentTypeError(f"The file '{values}' doesn't exist at '{file_path}'.")

        setattr(namespace, self.dest, file_path)