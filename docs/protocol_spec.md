# FTP Protocol Notes

Author: Joshua Lopez

## Goal
- Simple FTP-style flow for this project.
- Control link carries commands. Data link moves files or listings.

## Ports
- **Control Port (default): 2121**
  - Selected because ports above 1024 do not require sudo/root access on Linux.
  - Applies to both local development and AWS EC2 deployment.
  - Override by setting the `FTP_PORT` environment variable (e.g., to 21 if you have sudo).
- **Data ports:** 20000-21000 (1,000-ports window that matches the AWS Security Group rule).

## Commands (client -> server)
- `GET <name>`: download a file from `server_files/`.
- `PUT <name> SIZE <size>`: upload a file. Size is bytes; the literal `SIZE` keyword is required.
- `LS`: list files in `server_files/`.
- `EXIT`: close the session.

Commands are plain text lines ending with `\n`.

## Responses (server -> client)
- `200 OK PORT <port> [SIZE <n>] [info]`: command accepted. `SIZE` is present for GET responses.
- `226 Listing complete`: LS finished with no error.
- `226 Transfer complete`: GET finished with no error.
- `226 File stored`: PUT finished with no error.
- `550 <message>`: file problem or other user error (e.g., not found, incomplete upload).
- `500 <message>`: bad command or server error.

All responses are single lines ending with `\n`.

## Command Flow
- **GET**  
  1. Client sends `GET name`.  
  2. Server checks file. If found, replies `200 OK PORT <port> SIZE <size>`.  
  3. Client connects to `<port>` and reads `<size>` bytes.  
  4. Server closes data socket and sends `226 Transfer complete`.

- **PUT**  
  1. Client sends `PUT name SIZE size`.  
  2. Server replies `200 OK PORT <port>`.  
  3. Client connects to `<port>` and sends exactly `<size>` bytes.  
  4. Server saves the file and sends `226 File stored`.  
  5. If the byte counts do not match, server sends `550 Incomplete upload`.

- **LS**  
  1. Client sends `LS`.  
  2. Server creates listing text, replies `200 OK PORT <port>`.  
  3. Client connects to `<port>` and reads until socket close.  
  4. Server finishes with `226 Listing complete`.

- **EXIT**  
  1. Client sends `EXIT`.  
  2. Server replies `221 Goodbye` and closes the socket.

## Session Rules
- One command at a time. Wait for the final response before sending another.
- Filenames use only letters, numbers, dot, dash, underscore.
- Data sockets time out after 60 seconds.
- Server pre-creates `server_files/` and `logs/` if missing.

## Concurrency
- Server listens on the control port and starts one thread per client.
- Each transfer uses its own data socket, so clients do not step on each other.
