import redis
import json
import time
from abc import ABC, abstractmethod

class Observer(ABC):
    @abstractmethod
    def update(self, packets):
        pass


class PacketContext:
    def __init__(self, packets, metadata: dict = None):
        self.packets = packets
        self.metadata = metadata if metadata is not None else {}


class RedisPacketHandler:
    """
    Gestore dei pacchetti Redis che implementa il pattern Observer per notificare i cambiamenti.
    """

    def __init__(self, redis_host="localhost", redis_port=6379, redis_db=0, redis_key="suricata-packets", timeout=10):
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)
        self.redis_key = redis_key
        self.timeout = timeout
        self.start_time = time.time()
        self.observers = []


    def register_observer(self, observer):
        """
        Registra un observer per la notifica.
        """
        self.observers.append(observer)


    def remove_observer(self, observer):
        """
        Rimuove un observer dalla lista.
        """
        self.observers.remove(observer)


    def notify_observer(self, context):
        """
        Notifica tutti gli observer registrati.
        """
        for observer in self.observers:
            observer.update(context)


    def __check_redis_length(self):
        """
        Controlla il numero di pacchetti presenti nella lista Redis.
        """
        return self.redis_client.llen(self.redis_key)


    def __fetch_packets(self):
        """
        Legge tutti i pacchetti da Redis e li rimuove dalla lista.
        """
        packets = []
        while True:
            packet = self.redis_client.lpop(self.redis_key)
            if packet is None:
                break
            packets.append(json.loads(packet))
        return packets
    

    def process_packets(self):
        """
        Processa i pacchetti presenti nella lista Redis.
        """
        while True:
            elapsed_time = time.time() - self.start_time
            if elapsed_time >= self.timeout:
                list_length = self.__check_redis_length()
                if list_length > 0:
                    print(f"Timeout raggiunto. Trovati {list_length} pacchetti da processare.")
                    try:
                        packets = self.__fetch_packets()
                        packet_context = PacketContext(packets)
                        self.notify_observer(packet_context)
                    except Exception as e:
                        print(f"Errore durante il processamento dei pacchetti: {str(e)}")
                        break
                else:
                    print("Nessun pacchetto trovato. Attendo...")
                self.start_time = time.time()
            time.sleep(1)