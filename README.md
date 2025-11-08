FTP Server Project - Part 1
===========================

Team Members:
- Joshua: Protocol/Architecture Lead
- Jamie: Server Developer
- Chanho: Client Developer
- Kent: AWS/Deployment Engineer (Gatekeeper)
- Sean: Testing/Documentation Lead

How to Run:
-----------

1. Start the Server (Terminal 1):
   $ cd /path/to/ftp-from-scratch-to-aws
   $ export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   $ python3 server/ftp_server.py
   
   Server listens on localhost:2121
   (Note: Port 2121 is used instead of 21 to avoid requiring root privileges)

2. Start the Client (Terminal 2):
   $ cd /path/to/ftp-from-scratch-to-aws
   $ export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   $ python3 client/ftp_client.py localhost 2121

3. Available Commands:
   > LS                    - List files on server
   > PUT <filename>        - Upload file to server
   > GET <filename>        - Download file from server
   > EXIT                  - Close connection

Testing:
--------
Test files are located in tests/test_data/:
- small.txt (1.4KB)
- medium.bin (1MB)
- large.iso (10MB)

Example Test Sequence:
> LS
> PUT tests/test_data/small.txt
> LS
> GET small.txt
> GET nonexistent.txt    (should show 550 error)
> EXIT

Features Implemented:
---------------------
✓ Separate control (port 2121) and data (ports 20000-21000) connections
✓ GET command for downloading files
✓ PUT command for uploading files
✓ LS command for listing server files
✓ Error handling (550 File Not Found)
✓ Proper response codes:
  - 220 Welcome to Simple FTP Server
  - 200 OK (command accepted)
  - 226 Transfer complete
  - 550 File not found/error

Technical Details:
------------------
- Server stores uploaded files in server_files/ directory
- Client downloads files to current directory
- Data connections use ephemeral ports in range 20000-21000
- File transfers preserve data integrity

Tested and Verified:
--------------------
✓ Small files (1.4KB) - Upload/Download working
✓ Medium files (1MB) - Upload/Download working
✓ Large files (10MB) - Upload/Download working
✓ Error handling - 550 errors for missing files
✓ File integrity - No corruption during transfers