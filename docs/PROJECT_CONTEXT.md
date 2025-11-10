# FTP SERVER PROJECT - TECHNICAL SPEC

## 1. Project Goal
Build a multi-threaded FTP server in Python using only standard libraries.
- **Part 1 (Local):** Single-client server on `localhost`.
- **Part 2 (Cloud):** Multi-threaded server for 3+ clients, manually deployed on AWS EC2.

## 2. Tech Stack
- **Language:** Python 3
- **Libraries (Standard Only):** `socket`, `threading`, `os`, `sys`
- **Cloud:** AWS EC2 `t2.micro`

## 3. Protocol Definition
- **Control Port:** `21`
- **Data Port Range:** `20000` - `21000`
- **Connection Flow:**
    1.  Client connects to Server on Control Port (`21`).
    2.  Client sends a command (e.g., `GET file.txt`).
    3.  Server picks a free port from the Data Port Range (e.g., `20001`).
    4.  Server sends an "OK" response + the new data port back to the client on the Control Port (e.g., `200 OK 20001`).
    5.  Client opens a *new, separate* TCP connection to the Server on the specified Data Port (`20001`).
    6.  Server sends/receives the file data on the Data Port.
    7.  The Data Port connection is closed.
    8.  Server sends a final "Complete" message on the Control Port (e.g., `226 Transfer Complete`).
- **Commands (Client -> Server):**
    - `GET <filename>`
    - `PUT <filename> <filesize>`
    - `LS`
    - `EXIT`
- **Response Codes (Server -> Client):**
    - `200 OK [data]`: Command valid, proceeding. (e.g., `200 OK 20001`)
    - `226 Transfer Complete`: File transfer or LS finished.
    - `550 File Not Found / Error`: Action failed.

## 4. AWS "Gatekeeper" Strategy (CRITICAL)
- **NO CI/CD:** We are NOT using GitHub Actions for deployment.
- **NO IAM USERS:** Only one person (Kent, the Gatekeeper) has AWS credentials.
- **MANUAL DEPLOY:** Deployment is done by Kent SSH-ing into the EC2 instance, running `git pull`, and manually starting the Python server.
- **COST CONTROL:** Kent manually starts and stops the `t2.micro` instance for specific "Testing Windows" to stay under a $5 budget.
- **Security Group:**
    - Port `22` (SSH): Open to `0.0.0.0/0`
    - Port `21` (Control): Open to `0.0.0.0/0`
    - Ports `20000-21000` (Data): Open to `0.0.0.0/0`

## 5. File Structure
ftp-project/
├── server/
│   ├── ftp_server.py         # Main server: socket listen, thread spawning
│   ├── command_handler.py    # Logic for GET, PUT, LS (runs in a thread)
│   └── config.py
├── client/
│   ├── ftp_client.py         # Main client: UI, connect, send commands
│   ├── command_parser.py     # Logic for handling data connections
│   └── config.py
├── shared/
│   └── protocol.py           # Shared constants (ports, codes)
├── tests/
│   ├── test_multiclient.py
│   └── test_data/            # small.txt, medium.bin, large.iso
├── docs/
│   └── protocol_spec.md
├── deployment/
│   └── stop_server.sh        # Script for Kent to stop the server
├── logs/                     # (gitignored)
├── server_files/             # (gitignored)
├── .gitignore
└── README.txt