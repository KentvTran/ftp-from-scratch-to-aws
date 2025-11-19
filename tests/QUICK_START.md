# Quick Start Guide for Testing

## Local Testing (Server on same machine)

### Step 1: Start the Server
```bash
cd /path/to/project
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python3 server/ftp_server.py
```

The server will start on `localhost:2121`

### Step 2: Run Tests (in another terminal)
```bash
cd /path/to/project
# Server is on localhost by default
python3 tests/test_multiclient.py
```

---

## EC2/Remote Testing

### Step 1: Deploy Server on EC2
```bash
# SSH into EC2 instance
ssh -i your-key.pem ec2-user@your-ec2-ip

# On EC2, deploy the server
cd /path/to/project
./deployment/manual_deploy.sh
```

### Step 2: Run Tests from Your Machine
```bash
cd /path/to/project

# Set the EC2 IP address
export FTP_HOST=your-ec2-ip-address
export FTP_PORT=2121

# Run tests
python3 tests/test_multiclient.py
```

---

## Troubleshooting

### "Connection refused" Error

**Possible causes:**
1. Server is not running
   - **Solution**: Start the server first (see Step 1 above)

2. Wrong host/port
   - **Solution**: Check `FTP_HOST` and `FTP_PORT` environment variables
   - **Check**: Run `echo $FTP_HOST` to verify

3. Firewall blocking connection
   - **Solution**: Check EC2 security groups allow port 2121 (and 20000-21000 for data)
   - **Solution**: Check local firewall settings

4. Server host is still a placeholder
   - **Solution**: Make sure you've set `export FTP_HOST=actual-ip-address`

### Verify Server is Running

**On localhost:**
```bash
# Check if port 2121 is listening
lsof -i :2121
# or
netstat -an | grep 2121
```

**On EC2:**
```bash
# SSH into EC2 and check
ssh -i your-key.pem ec2-user@your-ec2-ip
ps aux | grep ftp_server
netstat -an | grep 2121
```

### Test Server Connection Manually

```bash
# Try connecting with the client
python3 client/ftp_client.py localhost 2121
# or
python3 client/ftp_client.py your-ec2-ip 2121
```

If this works, the server is running. If not, check the server logs.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FTP_HOST` | `localhost` | Server hostname or IP address |
| `FTP_PORT` | `2121` | Server control port |

---

## Example Session

```bash
# Terminal 1: Start server
$ cd ftp-from-scratch-to-aws-main
$ export PYTHONPATH="${PYTHONPATH}:$(pwd)"
$ python3 server/ftp_server.py
[SERVER] Listening on 127.0.0.1:2121

# Terminal 2: Run tests
$ cd ftp-from-scratch-to-aws-main
$ python3 tests/test_multiclient.py
==================================================
Multi-Client FTP Server Test Suite
Server: localhost:2121
==================================================
Checking server connectivity to localhost:2121...
✅ Server is accessible at localhost:2121

=== Test 1: Concurrent PUT ===
[Client 1] Connected to localhost:2121
[Client 2] Connected to localhost:2121
...
```

