#!/bin/bash
TARGET=$1
SEQUENCE=(1234 5678 9012)

echo "Knocking on $TARGET..."
for PORT in "${SEQUENCE[@]}"; do
    # Send a single SYN packet
    nmap -Pn --max-retries 0 -p $PORT $TARGET > /dev/null
done
echo "Sequence complete."