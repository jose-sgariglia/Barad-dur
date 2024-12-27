import logging
import glob
from .config_loader import ConfigLoaderFromDict
from NTLFlowLyzer.network_flow_analyzer import NTLFlowLyzer

# Configure the logger
barad_logger = logging.getLogger("barad_logger")

class CSVConversionError(Exception):
    pass

def find_pcap_files(directory):
    file_pattern = directory + '/*'
    pcap_files = glob.glob(file_pattern)
    return pcap_files

class CsvConverter:
    def __init__(self, config_dict: dict, online_capturig: bool=False, batch_mode: bool=False, continues_batch_mode: bool=False):
        self.config_dict = config_dict
        self.online_capturig = online_capturig
        self.batch_mode = batch_mode
        self.continues_batch_mode = continues_batch_mode

    def run(self):
        try:
            config = ConfigLoaderFromDict(self.config_dict)
            network_flow_analyzer = NTLFlowLyzer(config, self.online_capturig, self.continues_batch_mode)
            if not self.batch_mode:
                network_flow_analyzer.run()
                return

            barad_logger.info("[P2C] Batch mode is on!")
            batch_address = config.batch_address
            batch_address_output = config.batch_address_output
            pcap_files = find_pcap_files(batch_address)
            barad_logger.info(f"[P2C] {len(pcap_files)} files detected. Let's analyze them!")
            for file in pcap_files:
                barad_logger.info(100 * "#")
                output_file_name = file.split('/')[-1]
                config.pcap_file_address = file
                config.output_file_address = f"{batch_address_output}/{output_file_name}.csv"
                network_flow_analyzer = NTLFlowLyzer(config, self.online_capturig, self.continues_batch_mode)

                barad_logger.info(f"[P2C] Converting {file} to {config.output_file_address}")
                barad_logger.info("[P2C] Nexts are the logs from NTLFlowLyzer:")
                network_flow_analyzer.run()
        except Exception as e:
            raise CSVConversionError(f"[P2C] An error occurred: {str(e)}")
