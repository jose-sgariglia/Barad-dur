import os
import json
from utils.packet_handler import PacketHandler, PacketContext
from utils.logger import logging

file_logger = logging.getLogger("barad_logger")

CAPTURE_DIR = "../suricata_env/captures/"

class FilePacketHandler(PacketHandler):
    """
    File packet handler that implements the Observer pattern to notify changes.
    """

    def __init__(self, file_path):
        self.file_path = os.path.join(CAPTURE_DIR, file_path)
        self.observers = []
        file_logger.debug("[HFS] FilePacketHandler initialized with file path: %s", file_path)

    def register_observer(self, observer):
        """
        Registers an observer for notification.
        """
        self.observers.append(observer)
        file_logger.info("[HFS] Observer registered: %s", observer)

    def remove_observer(self, observer):
        """
        Removes an observer from the list.
        """
        self.observers.remove(observer)
        file_logger.info("[HFS] Observer removed: %s", observer)

    def notify_observer(self, context=None):
        """
        Notifies all registered observers.
        """
        file_logger.debug("[HFS] Notifying observers with context: %s", context)
        for observer in self.observers:
            observer.update(context)
            file_logger.debug("[HFS] Observer %s notified", observer)

    def __fetch_packets(self):
        """
        Reads all packets from the file.
        """
        pass

    def process_packets(self):
        """
        Processes the packets in the file.
        """
        file_logger.info("[HFS] Starting packet processing")
        try:
            if os.path.exists(self.file_path):
                os.system(f"cp {self.file_path} ./.temp/output.pcap")
                self.notify_observer()
        except Exception as e:
            file_logger.error("[HFS] Error processing packets: %s", str(e))
