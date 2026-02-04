#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

TARGET_IP="172.20.0.20"

echo -e "${GREEN}=== Deploying Security Patch ===${NC}"

# # Go to the directory containing docker-compose.yml
# cd ..

# # USE 'docker compose' WITHOUT THE HYPHEN
# # This is much more stable and avoids the 'ContainerConfig' error
# docker compose up -d --build port_knocking

# # Return to your directory
# cd port_knocking

echo "Waiting for knockd to initialize..."
# sleep 3

echo "---------------------------------------"

# 3. Prove it's LOCKED
echo -e "${GREEN}[Step 1] Testing port 2222 BEFORE knocking...${NC}"
# Use a shorter timeout to be sure
if nc -zv -w 1 $TARGET_IP 2222; then
    echo -e "${RED}[!] FAILURE: Port 2222 is still exposed!${NC}"
    echo "Current Container Firewall Rules:"
    docker exec 2_network_port_knocking iptables -L -n
    exit 1
else
    echo -e "${GREEN}[RESULT] Port 2222 is LOCKED (Expected).${NC}"
fi

echo "---------------------------------------"

# 4. Perform the Knock
echo -e "${GREEN}[Step 2] Executing knock sequence: 1234, 5678, 9012...${NC}"
python3 knock_client.py --target $TARGET_IP --sequence 1234,5678,9012
sleep 1 

echo "---------------------------------------"

# 5. Prove it's OPEN
echo -e "${GREEN}[Step 3] Testing port 2222 AFTER knocking...${NC}"
nc -zv -w 3 $TARGET_IP 2222
if [ $? -eq 0 ]; then
    echo -e "${GREEN}[RESULT] SUCCESS! Port 2222 is now OPEN.${NC}"
else
    echo -e "${RED}[RESULT] FAILURE: Port 2222 remained locked.${NC}"
    docker logs 2_network_secret_ssh | tail -n 10
fi
sleep 10

echo "---------------------------------------"
echo -e "${GREEN}[Step 4] Resetting security state (Closing port)...${NC}"
# Send the reverse sequence to trigger [closeSSH]
python3 knock_client.py --target $TARGET_IP --sequence 9012,5678,1234
sleep 1

# Final check to prove it's locked again
nc -zv -w 1 $TARGET_IP 2222 2>&1 | grep -q "succeeded"
if [ $? -ne 0 ]; then
    echo -e "${GREEN}[RESULT] Reset Successful: Port is LOCKED again.${NC}"
else
    echo -e "${RED}[!] WARNING: Port failed to close. Check knockd logs.${NC}"
fi
