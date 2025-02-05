import os

TEMP_DIR = "./.temp/"

def setup_temp_dir():
    os.makedirs(TEMP_DIR, exist_ok=True)

def cleanup_temp_dir():
    for file in os.listdir(TEMP_DIR):
        os.remove(TEMP_DIR + file)
    os.rmdir(TEMP_DIR)
