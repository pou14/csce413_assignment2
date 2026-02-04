## SSH Honeypot
### What This Honeypot Does
- Runs a fake SSH service on port 22
- Looks like a real Ubuntu SSH server
- Accepts login attempts but does not give real access
- Logs attacker behavior for analysis

### What Gets Logged
- Attacker IP address and source port
- Time of connection
- Login attempts (username and password)
- Commands typed after login
- When the attacker disconnects

All logs are saved to:

```bash
logs/honeypot.log
```

### How It Works

* Built using Python and the `paramiko` library
* Sends a realistic SSH banner
* Provides a fake shell that responds like a real system
* Runs inside a Docker container

### How to Run the Honeypot

From the root of the project:

```bash
docker-compose up honeypot
```

---

### How to Test It

From another terminal, you can connect to the honeypot:

```bash
ssh admin@localhost -p 2222
```

Or from inside the Docker network:

```bash
ssh admin@172.20.0.30 -p 22
```

Try different usernames, passwords, and commands to simulate attacks.

---

### Viewing the Logs

```bash
cat honeypot/logs/honeypot.log
```