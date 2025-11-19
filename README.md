# FTP Server Project - Part 1

## Team Members and Contact Information:
* Joshua [Jlopez0627@csu.fullerton.edu]: Protocol/Architecture Lead
* Jamie [jjcastillojr21@csu.fullerton.edu]: Server Developer
* Chanho [chanho0323@csu.fullerton.edu]: Client Developer
* Kent [kentvtran@csu.fullerton.edu]: AWS/Deployment Engineer
* Sean [Sdle@csu.fullerton.edu]: Testing/Documentation Lead

## Programming Language:
Python 3

## How to Execute:
1.  **Start the Server (Terminal 1):**
    ```bash
    $ cd p1-[userid]
    $ export PYTHONPATH="${PYTHONPATH}:$(pwd)"
    $ python3 server/ftp_server.py
    ```
    Server will listen on `localhost:2121`
    (Note: Port 2121 is used instead of 21 to avoid requiring root privileges)

2.  **Start the Client (Terminal 2):**
    ```bash
    $ cd p1-[userid]
    $ export PYTHONPATH="${PYTHONPATH}:$(pwd)"
    $ python3 client/ftp_client.py localhost 2121
    ```

3.  **Available Commands:**
    * `LS` - List files on server
    * `PUT <filename>` - Upload file to server
    * `GET <filename>` - Download file from server
    * `EXIT` - Close connection

## Special Notes About This Submission:

1.  **Port Configuration:**
    * Control connection uses port 2121 (instead of standard port 21)
    * This avoids requiring root/administrator privileges for testing
    * Data connections use ephemeral ports in range 20000-21000

2.  **Project Structure:**
    * `server/` contains server implementation
    * `client/` contains client implementation
    * `shared/` contains protocol definitions
    * `tests/test_data/` contains test files for verification
    * `docs/` contains protocol specification

3.  **No External Dependencies:**
    * Uses only Python standard library (socket module)
    * No third-party packages required

## Testing:

Test files are located in `tests/test_data/`:
* `small.txt` (1.4KB)
* `medium.bin` (1MB)
* `large.iso` (10MB)

**Example Test Sequence:**
* LS 
* PUT tests/test_data/small.txt 
* LS 
* GET small.txt 
* GET nonexistent.txt (should show 550 error) 
* EXIT

## Features Implemented:
* Separate control (port 2121) and data (ports 20000-21000) connections
* `GET` command for downloading files
* `PUT` command for uploading files
* `LS` command for listing server files
* Error handling (550 File Not Found)
* Proper response codes:
    * 220 Welcome to Simple FTP Server
    * 200 OK (command accepted)
    * 226 Transfer complete
    * 550 File not found/error

## Technical Details:
* Server stores uploaded files in `server_files/` directory
* Client downloads files to current directory
* Data connections use ephemeral ports in range 20000-21000
* File transfers preserve data integrity
* Server uses threading to support multiple concurrent clients

## Tested and Verified:
* Small files (1.4KB) - Upload/Download working
* Medium files (1MB) - Upload/Download working
* Large files (10MB) - Upload/Download working
* Error handling - 550 errors for missing files
* File integrity - No corruption during transfers

## Protocol Specification:

**Control Connection:**
* **Port:** 2121
* **Commands:** `LS`, `GET <filename>`, `PUT <filename>`, `EXIT`
* **Responses:** 220, 200, 226, 550

**Data Connection:**
* **Port Range:** 20000-21000
* **Protocol:** Separate connection for each file transfer
* Server assigns ephemeral port and sends to client via control connection

## Implementation Notes:
1.  The server uses threading to support multiple concurrent clients (ready for Part 2)
2.  Client handles welcome banner (220) upon connection for protocol synchronization
3.  All file transfers include size verification to ensure data integrity
4.  Error codes follow FTP standard conventions
