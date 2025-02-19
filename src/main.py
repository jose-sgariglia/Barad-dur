import argparse
from utils.validators import ValidateModelPath, ValidateFilePath
from utils.logger import logger, init_logger, logging
from utils.handlers.handler_redis import RedisPacketHandler
from utils.handlers.handler_temp import TEMP_DIR, setup_temp_dir, cleanup_temp_dir
from utils.observer import PcapConverterObserver, CsvConverterObserver, ModelHandlerObserver
from utils.handlers.handler_file import FilePacketHandler  # Import the new handler


def display_banner(model: str, redis_key: str, timeout: int, file_path: str):
    banner = """
      ____                      _                _            
     |  _ \\                    | |              | |           
     | |_) | __ _ _ __ __ _  __| |  ______    __| |_   _ _ __ 
     |  _ < / _` | '__/ _` |/ _` | |______|  / _` | | | | '__|
     | |_) | (_| | | | (_| | (_| |          | (_| | |_| | |   
     |____/ \\__,_|_|  \\__,_|\\__,_|           \\__,_|\\__,_|_|   


Barad-dur is a packet processing pipeline that uses a deep learning model to detect malicious packets.
    Developed by: Suga   

Information:                                      
    """

    if file_path is not None:
        print(banner)
        print(f"\tModel: {model}")
        print(f"\tReading packets from file: {file_path}")

    else:
        print(banner)
        print(f"\tModel: {model}")
        print(f"\tReading packets from Redis key: {redis_key}")
        print(f"\tTimeout: {timeout} seconds")

    print("\n-----------------------------------------------------------\n")


def main(redis_key, timeout, model_path, file_path):
    try:
        logger.debug("Starting packet processing pipeline...")


        pcap_conv = PcapConverterObserver(output_filename=TEMP_DIR + "output.pcap")
        csv_conv = CsvConverterObserver({
                "pcap_file_address": TEMP_DIR + "output.pcap",
                "output_file_address": TEMP_DIR + "output.csv"
            })
        model_node = ModelHandlerObserver(model_path)

        if file_path is None:
            packet_handler = RedisPacketHandler(
                redis_key=redis_key,
                timeout=timeout
            )
            logger.debug("Redis handler initialized.")
            packet_handler.register_observer(pcap_conv)
            packet_handler.register_observer(csv_conv)
            packet_handler.register_observer(model_node)


        else:
            packet_handler = FilePacketHandler(
                file_path=file_path 
            )
            logger.debug("File handler initialized.")
            packet_handler.register_observer(csv_conv)
            packet_handler.register_observer(model_node)
            

        logger.debug("Observers registered.")

        logger.debug("Starting packet processing.")
        logger.debug("Processing packets...")
        packet_handler.run()

    except KeyboardInterrupt:
        logger.info("Exiting...")

    finally:
        cleanup_temp_dir()
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the IDS-AI packet processing pipeline.")

    parser.add_argument(
        "--model-path", "-m", 
        type=str, 
        required=True, 
        help="Path to the model directory.", 
        action=ValidateModelPath
    )

    parser.add_argument(
        "--read-file", "-f", 
        type=str,
        metavar="FILE_PATH",
        help="Path to the file to read packets from. If not provided, packets are read from the stream.",
        action=ValidateFilePath
    )

    parser.add_argument(
        "--redis-key", "-k",
        type=str, 
        default="suricata-packets", 
        help="Redis key for packet data if reading from stream."
    )

    parser.add_argument(
        "--timeout", 
        type=int, 
        default=10, 
        help="Timeout for processing packets if reading from stream."
    )

    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Enable verbose logging."
    )

    parser.add_argument(
        "--verbose-debug", "-vv", 
        action="store_true", 
        help="Enable debug logging."
    )

    args = parser.parse_args()

    if args.verbose or args.verbose_debug:
       init_logger(logging.DEBUG if args.verbose_debug else logging.INFO)
                
    display_banner(args.model_path, args.redis_key, args.timeout, args.read_file)
    main(args.redis_key, args.timeout, args.model_path, args.read_file)
