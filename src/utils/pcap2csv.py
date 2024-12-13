import logging
import glob
from NTLFlowLyzer.config_loader import ConfigLoader
from NTLFlowLyzer.network_flow_analyzer import NTLFlowLyzer

# Configura il logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ConfigLoaderFromDict(ConfigLoader):
    def __init__(self, config_dict: dict):
        self.config_dict = config_dict
        super().__init__(config_file_address=None)

    def read_config_file(self):
        try:
            if not isinstance(self.config_dict, dict):
                raise ValueError("Configuration must be a valid dictionary.")
            for key, value in self.config_dict.items():
                setattr(self, key, value)
            if self.pcap_file_address is None and self.batch_address is None and self.continues_batch_address is None:
                raise Exception("Please specify at least one of 'pcap_file_address', 'batch_address', or 'continues_batch_address' in the configuration.")
        except Exception as error:
            logging.error(f"Error occurred while reading the configuration: {str(error)}. Default values will be applied.")
            exit(-1)

class CSVConversionError(Exception):
    pass


def find_pcap_files(directory):
    file_pattern = directory + '/*'
    pcap_files = glob.glob(file_pattern)
    return pcap_files


def run(config_dict: dict, online_capturig: bool=False, batch_mode: bool=False, continues_batch_mode: bool=False):
    """
    Converts a pcap file to a CSV file using the NTLFlowLyzer tool.

    :param config_dict: Dictionary containing the configuration parameters.
    :param online_capturig: If True, captures network traffic online.
    :param batch_mode: If True, processes multiple pcap files in batch mode.
    :param continues_batch_mode: If True, processes multiple pcap files in continuous batch mode.
    """
    try:
        config = ConfigLoaderFromDict(config_dict)
        network_flow_analyzer = NTLFlowLyzer(config, online_capturig, continues_batch_mode)
        if not batch_mode:
            network_flow_analyzer.run()
            return

        logging.info("Batch mode is on!")
        batch_address = config.batch_address
        batch_address_output = config.batch_address_output
        pcap_files = find_pcap_files(batch_address)
        logging.info(f"{len(pcap_files)} files detected. Let's analyze them!")
        for file in pcap_files:
            logging.info(100 * "#")
            output_file_name = file.split('/')[-1]
            config.pcap_file_address = file
            config.output_file_address = f"{batch_address_output}/{output_file_name}.csv"
            network_flow_analyzer = NTLFlowLyzer(config, online_capturig, continues_batch_mode)
            network_flow_analyzer.run()
    except Exception as e:
        raise CSVConversionError(f"An error occurred: {str(e)}")
