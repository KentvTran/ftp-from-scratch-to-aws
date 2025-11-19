# FTP Server Project - Part 2 (AWS Multi-Client Deployment)

## Team Members
* Joshua [Jlopez0627@csu.fullerton.edu]: Protocol/Architecture Lead
* Jamie [jjcastillojr21@csu.fullerton.edu]: Server Developer
* Chanho [chanho0323@csu.fullerton.edu]: Client Developer
* Kent [kentvtran@csu.fullerton.edu]: AWS/Deployment Engineer
* Sean [Sdle@csu.fullerton.edu]: Testing/Documentation Lead

## Programming Language
Python 3 (Standard Library Only)

---

## How to Run

### Local Testing

**Start Server:**
```bash
./run_server.sh
```

**Connect Client:**
```bash
./run_client.sh localhost 2121
```

**Commands:** `LS`, `GET <file>`, `PUT <file>`, `EXIT`

---

### AWS Deployment

**Start Server:**
```bash
./deployment/aws/start_server.sh
# Outputs current EC2 public IP
```

**Connect Client:**
```bash
./run_client.sh <EC2_IP> 21
```

**Stop Server:**
```bash
./deployment/aws/stop_instance.sh
```

**Check Status/IP:**
```bash
./deployment/aws/status.sh
```

---

## AWS Configuration

- **Instance:** t2.micro (Amazon Linux 2023)
- **Region:** us-east-1
- **Control Port:** 21
- **Data Ports:** 20000-21000
- **Security Group:** Ports 22, 21, 20000-21000 open

---

## Features Implemented

**FTP Commands:**
- `LS` - List server files
- `GET` - Download files
- `PUT` - Upload files
- `EXIT` - Close connection

**Multi-Client Support:**
- Threading-based concurrent client handling
- Tested with 5+ simultaneous connections
- Separate control and data connections per client

**Protocol:**
- Control connection: Port 21 (AWS) / 2121 (local)
- Data connections: Ephemeral ports 20000-21000
- Response codes: 200 (OK), 226 (Complete), 550 (Error)

---

## Testing Multi-Client Functionality

### Concurrent Operations Test
Open 3+ terminals simultaneously:

**Terminal 1:**
```bash
./run_client.sh <EC2_IP> 21
> PUT tests/test_data/small.txt
```

**Terminal 2:**
```bash
./run_client.sh <EC2_IP> 21
> LS
> GET small.txt
```

**Terminal 3:**
```bash
./run_client.sh <EC2_IP> 21
> LS
> PUT tests/test_data/medium.bin
```

All operations should complete successfully without conflicts.

---

## Project Structure
```
ftp-project/
├── server/ftp_server.py          # Multi-threaded server
├── client/ftp_client.py          # Client application
├── shared/protocol.py            # Protocol constants
├── deployment/
│   ├── aws/                      # AWS automation scripts
│   ├── manual_deploy.sh          # Runs on EC2
│   └── stop_server.sh            # Runs on EC2
├── tests/
│   ├── test_multiclient.py       # Automated tests
│   └── test_data/                # Test files
├── run_server.sh                 # Local server launcher
└── run_client.sh                 # Local client launcher
```

---

## Design Implementation

**Multi-Threading:**
```python
# Each client runs in separate thread
threading.Thread(target=handle_client, args=(socket, addr), daemon=True).start()
```

**Port Configuration:**
```python
# Environment variable for flexibility
CONTROL_PORT = int(os.environ.get('FTP_PORT', 2121))
# Local: 2121 | AWS: 21 (set via FTP_PORT=21)
```

**Connection Model:**
- Persistent control connection for commands
- Separate data connection per file transfer
- Thread-safe operations