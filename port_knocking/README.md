## Port Knocking Implementation
This implementation fulfills the requirement to secure a protected service via a stateful port knocking sequence. It specifically patches the secret_ssh service at 172.20.0.20 to demonstrate defense-in-depth within the existing assignment network.

### Implementation Details
Protected Service: SSH on Port 2222.
Knock Sequence: 1234, 5678, 9012.
Validation Logic: Handled by knockd listening at the link layer.
Action: Dynamically manipulates iptables to insert/delete ACCEPT rules for the specific source IP.

### Components
1. Server Logic (`knockd.conf` & `entrypoint.sh`)
Instead of a standalone Python server, we use the industry-standard knockd.
    - `entrypoint.sh`: Flushes the default Docker allow-rules and sets the port to REJECT. This ensures the port is locked immediately upon container start.
    - `knockd.conf`: Implements the sequence validation and the iptables interface commands.

2. Client Logic (`knock_client.py`)
A custom Python script using low-level sockets to send a sequence of TCP packets to the target IP. It supports customizable sequences and targets.

3. Automated Demo (`demo.sh`)
The demo script automates the entire verification lifecycle.
    - Deployment: Uses docker compose to build and launch the patched container.
    - Pre-Knock Test: Proves port 2222 is LOCKED.
    - The Knock: Executes the Python client.
    - Post-Knock Test: Proves port 2222 is now OPEN.
    - Reset: Sends the reverse sequence to re-lock the port.
    
### Example usage
**Run the demonstration**: From the port_knocking directory, run:

```Bash
./demo.sh
```
Within the `demo.sh`:
```Bash
#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

TARGET_IP="172.20.0.20"

# 1. Prove it's LOCKED
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

# 2. Perform the Knock
echo -e "${GREEN}[Step 2] Executing knock sequence: 1234, 5678, 9012...${NC}"
python3 knock_client.py --target $TARGET_IP --sequence 1234,5678,9012
sleep 1 

echo "---------------------------------------"

# 3. Prove it's OPEN
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
```

**Manual Knock Example**:
```Bash
python3 knock_client.py --target 172.20.0.20 --sequence 1234,5678,9012
```
