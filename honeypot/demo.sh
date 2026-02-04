#!/bin/bash

HONEYPOT_HOST="localhost"
HONEYPOT_PORT="2222"

USERS=("admin" "root" "test" "ubuntu")
PASSWORDS=("admin" "123456" "password" "root")

COMMANDS=("whoami" "ls" "uname -a" "cat /etc/passwd" "exit")

for user in "${USERS[@]}"; do
  for pass in "${PASSWORDS[@]}"; do
    echo "[*] Trying $user:$pass"

    sshpass -p "$pass" ssh \
      -o StrictHostKeyChecking=no \
      -o UserKnownHostsFile=/dev/null \
      -p $HONEYPOT_PORT \
      $user@$HONEYPOT_HOST << EOF
${COMMANDS[0]}
${COMMANDS[1]}
${COMMANDS[2]}
exit
EOF

    sleep 1
  done
done
