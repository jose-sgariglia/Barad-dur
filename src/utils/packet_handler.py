class PacketContext:
    def __init__(self, packets, metadata: dict = None):
        self.packets = packets
        self.metadata = metadata if metadata is not None else {}

class PacketHandler:
    def register_observer(self, observer):
        raise NotImplementedError

    def remove_observer(self, observer):
        raise NotImplementedError

    def notify_observer(self, context):
        raise NotImplementedError

    def process_packets(self):
        raise NotImplementedError
