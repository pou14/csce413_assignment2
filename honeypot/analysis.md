## Honeypot Analysis

### Summary of Observed Attacks
During testing, the honeypot received multiple SSH connection attempts. Attackers tried different usernames and passwords, simulating brute-force login attempts. After connecting, the attackers issued basic commands in the fake shell.

---

### Notable Patterns
* Common usernames tried: `admin`, `root`
* Passwords: random guesses (like `1234`, `password`)
* Commands entered after login: `ls`, `cd ~`, and random strings
* Attackers disconnected after a few failed commands
* All activity was logged, including IP, port, timestamp, session duration, and commands

---

### Recommendations
* Continue monitoring and logging all SSH traffic
* Consider adding **failed login alerts** for repeated attempts
* Use the logs to identify suspicious IPs or automated scanning patterns
