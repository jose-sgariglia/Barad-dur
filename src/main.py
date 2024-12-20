import os
from utils.handler_redis import RedisPacketHandler, Observer, PacketContext
from utils.eve2pcap import PcapConverter
from utils.pcap2csv import CsvConverter
from utils.handler_model import ModelHandler

TEMP_DIR = ".temp/"
os.makedirs(TEMP_DIR, exist_ok=True)


class PcapConverterObserver(Observer):
    def __init__(self, output_filename, dlt=None, payload=False):
        self.pcap_converter = PcapConverter(output_filename, dlt, payload)

    def update(self, context: PacketContext):
        self.pcap_converter.run(context.packets)


class CsvConverterObserver(Observer):
    def __init__(self, config_ntl):
        self.csv_converter = CsvConverter(config_ntl)

    def update(self, context: PacketContext):
        self.csv_converter.run()


class ModelHandlerObserver(Observer):
    def __init__(self, path: str):
        self.model_handler = ModelHandler.load_model_and_metadata(path)

    def update(self, context: PacketContext):
        self.model_handler.predict_from_file("output.csv")

if __name__ == "__main__":
    try:
        redis_handler = RedisPacketHandler(
            redis_key="suricata-packets",
            timeout=10
        )


        # Convert the packets to a pcap file
        pcap_conv = PcapConverterObserver(output_filename=TEMP_DIR + "output.pcap")
        redis_handler.register_observer(pcap_conv)


        # Convert the pcap file to a CSV file
        config_ntl = {
            "pcap_file_address": TEMP_DIR + "output.pcap",
            "output_file_address": TEMP_DIR + "output.csv"
        }
        csv_conv = CsvConverterObserver(config_ntl)
        redis_handler.register_observer(csv_conv)

        # Load the model
        model_node = ModelHandlerObserver("../models/v2/")
        redis_handler.register_observer(model_node)


        print("Listening for packets...")
        redis_handler.process_packets()

    except KeyboardInterrupt:
        print("\n\nExiting...")

    finally:
        # for file in os.listdir(TEMP_DIR):
        #     os.remove(TEMP_DIR + file)
        # os.rmdir(TEMP_DIR)