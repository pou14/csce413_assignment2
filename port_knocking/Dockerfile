# Use the existing base from your assignment
FROM csce413_assignment2_secret_ssh 

# 1. Install knockd and iptables
USER root
RUN apt-get update && apt-get install -y knockd iptables && rm -rf /var/lib/apt/lists/*

# 2. Copy the config files we created
COPY knockd.conf /etc/knockd.conf
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# 3. Overwrite the original entrypoint to start knockd
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]