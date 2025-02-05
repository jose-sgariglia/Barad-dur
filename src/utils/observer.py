from abc import ABC, abstractmethod
from utils.eve2pcap import PcapConverter
from utils.pcap2csv import CsvConverter
from utils.model import ModelHandler
from utils.handlers.packet_handler import PacketContext
from utils.handlers.handler_temp import TEMP_DIR


class Observer(ABC):
    @abstractmethod
    def update(self, packets):
        pass


class PcapConverterObserver(Observer):
    def __init__(self, output_filename, dlt=None, payload=False):
        self.pcap_converter = PcapConverter(output_filename, dlt, payload)

    def update(self, context: PacketContext):
        self.pcap_converter.run(context.packets)


class CsvConverterObserver(Observer):
    def __init__(self, config_ntl, online_capturing: bool = False, batch_mode: bool = False, continuous_mode: bool = False):
        self.csv_converter = CsvConverter(config_ntl, online_capturing, batch_mode, continuous_mode)

    def update(self, context: PacketContext = None):
        self.csv_converter.run()


class ModelHandlerObserver(Observer):
    def __init__(self, model_path: str):
        self.model_handler = ModelHandler.load_model_and_metadata(model_path)

    def update(self, context: PacketContext = None):
        self.model_handler.predict_from_file(TEMP_DIR + "output.csv")