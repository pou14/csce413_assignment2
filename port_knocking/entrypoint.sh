#!/bin/bash

# 1. Flush ALL existing rules to clear that 172.20.0.1 ACCEPT rule
iptables -F

# 2. Add the REJECT rule. 
# Since we flushed everything, this will now be the first rule.
iptables -A INPUT -p tcp --dport 2222 -j REJECT

# 3. Start the original service (e.g., SSH) in the background
/usr/sbin/sshd &

# 4. Start knockd
knockd -d -i eth0 -c /etc/knockd.conf

# Keep the container running
tail -f /dev/null