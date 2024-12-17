import redis
import json
import time

class RedisPacketHandler:
    def __init__(self, redis_host="localhost", redis_port=6379, redis_db=0, redis_key="suricata-packets", timeout=10):
        """
        Inizializza la connessione a Redis e le impostazioni del gestore.
        """
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)
        self.redis_key = redis_key
        self.timeout = timeout
        self.start_time = time.time()
        self.callbacks = []


    def register_callback(self, callback):
        """
        Registra una funzione di callback.
        """
        self.callbacks.append(callback)


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
        Processo principale: controlla, raccoglie e salva i pacchetti ogni timeout.
        """
        while True:
            elapsed_time = time.time() - self.start_time
            if elapsed_time >= self.timeout:
                list_length = self.__check_redis_length()
                if list_length > 0:
                    print(f"Timeout raggiunto. Trovati {list_length} pacchetti da processare.")
                    packets = self.__fetch_packets()

                    for callback in self.callbacks:
                        callback(packets)

                else:
                    print("Nessun pacchetto trovato. Attendo...")
                self.start_time = time.time()
            time.sleep(1)