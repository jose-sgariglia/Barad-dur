import argparse
from utils.logger import logger, init_logger, logging
from utils.handler_redis import RedisPacketHandler
from utils.handler_temp import TEMP_DIR, setup_temp_dir, cleanup_temp_dir
from utils.observer import PcapConverterObserver, CsvConverterObserver, ModelHandlerObserver
from utils.handler_file import FilePacketHandler  # Import the new handler


# Set up logging and temp directory
init_logger(logging.INFO)
setup_temp_dir()


def main(redis_key, timeout, model_path, input_type):
    try:
        logger.info("Starting packet processing pipeline...")


        pcap_conv = PcapConverterObserver(output_filename=TEMP_DIR + "output.pcap")
        csv_conv = CsvConverterObserver({
                "pcap_file_address": TEMP_DIR + "output.pcap",
                "output_file_address": TEMP_DIR + "output.csv"
            })
        model_node = ModelHandlerObserver(model_path)

        if input_type == "redis":
            packet_handler = RedisPacketHandler(
                redis_key=redis_key,
                timeout=timeout
            )
            logger.info("Redis handler initialized.")
            packet_handler.register_observer(pcap_conv)
            packet_handler.register_observer(csv_conv)
            packet_handler.register_observer(model_node)


        elif input_type == "file":
            packet_handler = FilePacketHandler(
                file_path=redis_key  # Using redis_key argument to pass file path for simplicity
            )
            logger.info("File handler initialized.")
            packet_handler.register_observer(csv_conv)
            packet_handler.register_observer(model_node)


        else:
            logger.error("Invalid input type specified. Use 'redis' or 'file'.")
            return
            

        logger.info("Observers registered.")

        logger.info("Starting packet processing.")
        logger.info("Processing packets...")
        packet_handler.process_packets()

    except KeyboardInterrupt:
        logger.info("\n\nExiting...")

    finally:
        cleanup_temp_dir()
        pass


if __name__ == "__main__":
    logger.info("Starting Barad-dur packet processing pipeline.")

    parser = argparse.ArgumentParser(description="Run the IDS-AI packet processing pipeline.")
    parser.add_argument("--redis-key", type=str, default="suricata-packets", help="Redis key for packet data or file path.")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout for processing packets.")
    parser.add_argument("--model-path", type=str, required=True, help="Path to the model directory.")
    parser.add_argument("--input-type", type=str, choices=["redis", "file"], required=True, help="Type of input source (redis or file).")

    args = parser.parse_args()
    main(args.redis_key, args.timeout, args.model_path, args.input_type)
