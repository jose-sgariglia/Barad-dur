#!/bin/bash
set -e

echo "Avvio di Redis in background..."
/usr/bin/redis-server /etc/redis/redis.conf &

echo "Redis è in esecuzione."
echo "Entra nella shell per avviare manualmente gli altri servizi (ad es. SSH, Suricata)."
exec /bin/bash