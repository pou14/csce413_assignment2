#!/bin/bash

ROOT_DIR=$(pwd)

docker stop $(docker ps -q) 2>/dev/null
docker container prune -f
docker network prune -f

# Build and start NON-conflicting services only
docker compose build
docker compose up -d database redis secret_api port_knocking
docker compose up -d webapp secret_ssh

# Start secure SSH first (uses port 2222)
# docker start 2_network_secret_ssh

docker ps
echo ""

echo "======================================"
echo " CSCE413 Security Assignment Demo"
echo "======================================"
echo ""

sleep 10
#########################################
# PART 1 — Reconnaissance
#########################################

echo ""
echo "===== PART 1: RECONNAISSANCE ====="
read -p "Press Enter to run the scanner..."

cd "$ROOT_DIR/port_scanner"
echo "Starting Port scanner..."
echo ""

echo "Command used: python3 main.py 172.20.0.10 1 20000"
python3 main.py 172.20.0.10 1 20000

echo ""
echo "Port scanning finished."
read -p "Press Enter to continue..."

cd "$ROOT_DIR"

#########################################
# PART 2 — MITM DEMO
#########################################

echo ""
echo "===== PART 2: MITM ATTACK ====="
echo "Start Wireshark"
wireshark
echo ""

read -p "Press Enter after you've captured packets..."
echo "Hidden flags in http://172.20.0.21:8888/flag?token=FLAG{n3tw0rk_tr4ff1c_1s_n0t_s3cur3}"
echo ""
read -p "Press Enter to continue..."
#########################################
# PART 3 — PORT KNOCKING DEFENSE
#########################################

echo ""
echo "===== PART 3: PORT KNOCKING ====="
echo "First show SSH port blocked."

cd "$ROOT_DIR/port_knocking"
# python3 knock_client.py --target 172.20.0.20 --sequence 1234,5678,9012
read -p "Press Enter to try SSH BEFORE knocking..."
ssh sshuser@172.20.0.20 -p 2222
echo ""

echo "Now performing port knocking sequence..."
read -p "Press Enter to knock..."
cd "$ROOT_DIR/port_knocking"
echo "Command used: python3 knock_client.py --target 172.20.0.20 --sequence 1234,5678,9012"
python3 knock_client.py --target 172.20.0.20 --sequence 1234,5678,9012
echo ""

echo "Knock sent. SSH should now work."
read -p "Press Enter to try SSH again..."
ssh sshuser@172.20.0.20 -p 2222
echo ""

read -p "Press Enter to Close SSH again"
python3 knock_client.py --target 172.20.0.20 --sequence 9012,5678,1234
echo "SSH Closed, it should not now work."
echo ""

read -p "Press Enter to try SSH again..."
ssh sshuser@172.20.0.20 -p 2222
read -p "Press Enter to continue..."

cd "$ROOT_DIR"

#########################################
# PART 4 — HONEYPOT DEMO
#########################################
echo ""
echo "===== PART 4: HONEYPOT ====="
docker stop 2_network_secret_ssh
docker rm 2_network_secret_ssh
docker compose up -d honeypot
echo "Connecting to honeypot SSH service..."

read -p "Press Enter to connect..."
ssh-keygen -f "/home/pou14/.ssh/known_hosts" -R "[localhost]:2222"
ssh admin@localhost -p 2222

echo ""
read -p "Press Enter to view logs..."

cd "$ROOT_DIR/honeypot"

tail -n 20 logs/honeypot.log

cd "$ROOT_DIR"

#########################################

echo ""
echo "===== DEMO COMPLETE ====="
echo ""