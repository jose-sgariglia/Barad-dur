import logging
import argparse
from utils.handler_redis import RedisPacketHandler
from utils.handler_temp import TEMP_DIR, setup_temp_dir, cleanup_temp_dir
from utils.observer import PcapConverterObserver, CsvConverterObserver, ModelHandlerObserver


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
setup_temp_dir()


def main(redis_key, timeout, model_path):
    try:
        redis_handler = RedisPacketHandler(
            redis_key=redis_key,
            timeout=timeout
        )

        pcap_conv = PcapConverterObserver(output_filename=TEMP_DIR + "output.pcap")
        csv_conv = CsvConverterObserver({
                "pcap_file_address": TEMP_DIR + "output.pcap",
                "output_file_address": TEMP_DIR + "output.csv"
            })
        model_node = ModelHandlerObserver(model_path)


        redis_handler.register_observer(pcap_conv)
        redis_handler.register_observer(csv_conv)
        redis_handler.register_observer(model_node)

        logging.info("Listening for packets...")
        redis_handler.process_packets()

    except KeyboardInterrupt:
        logging.info("\n\nExiting...")

    finally:
        cleanup_temp_dir()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the IDS-AI packet processing pipeline.")
    parser.add_argument("--redis-key", type=str, default="suricata-packets", help="Redis key for packet data.")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout for processing packets.")
    parser.add_argument("--model-path", type=str, required=True, help="Path to the model directory.")

    args = parser.parse_args()
    main(args.redis_key, args.timeout, args.model_path)
