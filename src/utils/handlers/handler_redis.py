import redis
import json
import time

from utils.logger import logging
from utils.handlers.packet_handler import PacketContext
from utils.handlers.packet_handler import PacketHandler 

barad_logger = logging.getLogger("barad_logger")


class RedisPacketHandler(PacketHandler):
    """
    Redis packet handler that implements the Observer pattern to notify changes.
    """

    def __init__(self, redis_host="localhost", redis_port=6379, redis_db=0, redis_key="suricata-packets", timeout=10):
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)
        self.redis_key = redis_key
        self.timeout = timeout
        self.start_time = time.time()
        self.observers = []
        barad_logger.debug("[HRS] RedisPacketHandler initialized with host: %s, port: %d, db: %d, key: %s, timeout: %d",
                          redis_host, redis_port, redis_db, redis_key, timeout)


    def register_observer(self, observer):
        """
        Registers an observer for notification.
        """
        barad_logger.debug("[HRS] Observer registered: %s", observer)
        self.observers.append(observer)


    def remove_observer(self, observer):
        """
        Removes an observer from the list.
        """
        barad_logger.debug("[HRS] Observer removed: %s", observer)
        self.observers.remove(observer)


    def notify_observer(self, context):
        """
        Notifies all registered observers.
        """
        barad_logger.debug("[HRS] Notifying observers with context: %s", context)
        for observer in self.observers:
            barad_logger.debug("[HRS] Observer %s notified", observer)
            observer.update(context)


    def __check_redis_length(self):
        """
        Checks the number of packets in the Redis list.
        """
        length = self.redis_client.llen(self.redis_key)
        barad_logger.debug("[HRS] Checked Redis list length: %d", length)
        return length


    def __fetch_packets(self):
        """
        Reads all packets from Redis and removes them from the list.
        """
        packets = []
        barad_logger.debug("[HRS] Fetching packets from Redis")
        while True:
            packet = self.redis_client.lpop(self.redis_key)
            if packet is None:
                break
            packets.append(json.loads(packet))
        barad_logger.info("[HRS] Fetched %d packets from Redis", len(packets))
        return packets
    

    def __process_packets(self):
        """
        Processes the packets in the Redis list.
        """

        try:
            packets = self.__fetch_packets()
            packet_context = PacketContext(packets)
            self.notify_observer(packet_context)

        except Exception as e:
            barad_logger.error("[HRS] Error processing packets: %s", str(e))


    def run(self):
        """
        Runs the packet processing pipeline.
        """

        barad_logger.info("[HRS] Starting packet processing")
        while True:
            elapsed_time = time.time() - self.start_time
            if elapsed_time >= self.timeout:
                list_length = self.__check_redis_length()
                if list_length > 0:
                    print(f"\x1b[34mTimeout reached.\x1b[0m Found {list_length} packets to process.")
                    barad_logger.info("[HRS] Found %d packets to process", list_length)
                    self.__process_packets()
                else:
                    print("No packets found. Waiting...")
                    barad_logger.info("[HRS] No packets found. Waiting...")

                self.start_time = time.time()
            time.sleep(1)