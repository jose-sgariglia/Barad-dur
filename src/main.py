import os
import json 
import redis
import logging
import pandas as pd
from hashlib import sha1

# Custom package
from utils import pcap2csv
from utils.eve2pcap import eve2pcap
from utils.model import Model

logging.basicConfig(level=logging.WARNING)

PATH_ALERTS = "../alerts/"
os.makedirs(PATH_ALERTS, exist_ok=True)

PATH_CSV = "../csv/"
os.makedirs(PATH_CSV, exist_ok=True)


r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

pubsub = r.pubsub()
pubsub.subscribe('suricata:alert')

model_name = "RandomForestClassifier.joblib"

if __name__ == "__main__":
    print("In ascolto degli alert...")

    for message in pubsub.listen():
        if message['type'] == 'message':
            data = json.loads(message['data'])
            if data.get('alert', {}).get('signature') not in ["TCP", "HTTP"]:
                continue

            # Convert the eve.json to pcap
            eve_name = sha1(data['timestamp'].encode()).hexdigest()
            pcap_path = PATH_ALERTS + eve_name + ".pcap"
            try:
                eve2pcap.run(output_filename=pcap_path, eves=[data])
                print(f"Scritto {pcap_path}")
            except Exception as e:
                print(f"Errore: {e}")


            # Convert the pcap to csv
            csv_name = eve_name + ".csv"
            csv_path = PATH_CSV + csv_name

            try:
                config_ntl = {
                    "pcap_file_address": pcap_path,
                    "output_file_address": csv_path,
                    "pippo": "pluto"
                }
                pcap2csv.run(config_ntl)
            except Exception as e:
                print(f"Errore: {e}")
            
            
            # Predict using the Daniele's model
            # model = Model(model_name)
            # print(f"Features: {model.get_features()}")

            