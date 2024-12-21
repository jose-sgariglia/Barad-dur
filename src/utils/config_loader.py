import logging
from NTLFlowLyzer.config_loader import ConfigLoader

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
