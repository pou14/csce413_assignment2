docker stop $(docker ps -q) 2>/dev/null
docker container prune -f
docker network prune -f

# Build and start NON-conflicting services only
docker compose build
docker compose up -d database redis secret_api port_knocking
docker compose up -d webapp secret_ssh

read -p "Press Enter to try SSH BEFORE knocking..."
ssh sshuser@172.20.0.20 -p 2222
echo ""

echo "Now performing port knocking sequence..."
read -p "Press Enter to knock..."
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