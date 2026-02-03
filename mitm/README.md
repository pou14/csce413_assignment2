### Discovery
The Traffic between the web application and the MySQL database was captured using Wireshark by applying the filter of tcp.port == 3306. While interacting with the web application, There are database queries that got intercepted.

The SQL queries were not encrypted at all. By inspecting the captured packets, the following SQL query was clearly visible in plaintext within the TCP stream:
```sql
SELECT id, username, email, role FROM users ORDER BY id
```
In addition to the query itself, the database response was not encrypted as well. The returned data included sensitive user information such as usernames, email addresses, and user roles.

### Impact

Because the database communication is unencrypted, an attacker with access to the same network could perform a MITM attack to capture database traffic. Which then allows the attackers to
- Read SQL queries and database responses
- Extract sensitive user data and PII
- Identify privileged accounts such as administrators
- Steal authentication tokens transmitted over the same connection

This is a serious security risk and shows how important it is of using encrypted connections between the web application and the database.

### Captured Flag
After intercepting network traffic while clicking through the web application, Wireshark successfully captured sensitive data transmitted from the `api/secret` route. By using the captured authentication token, access to the protected service was obtained and the final flag was successfully retrieved.
```bash
FLAG{p0rt_kn0ck1ng_4nd_h0n3yp0ts_s4v3_th3_d4y}
```
This confirms that sensitive authentication data transmitted over an unencrypted connection can be intercepted and reused in a MITM attack to gain unauthorized access to protected resources.