import os
from utils.handler_redis import RedisPacketHandler
from utils.eve2pcap import PcapConverter

TEMP_DIR = ".temp/"
os.makedirs(TEMP_DIR, exist_ok=True)

if __name__ == "__main__":
    redis_handler = RedisPacketHandler(
        redis_key="suricata-packets",
        timeout=10
    )

    pcap_converter = PcapConverter(output_filename=TEMP_DIR + "output.pcap", dlt="DN10MB", payload=False)

    redis_handler.register_callback(pcap_converter.run)


    print("Listening for packets...")
    redis_handler.process_packets()