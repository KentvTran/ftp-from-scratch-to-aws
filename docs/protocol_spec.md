# FTP Protocol Notes

Author: Joshua Lopez

## Goal
- Simple FTP-style flow for this project.
- Control link carries commands. Data link moves files or listings.

## Ports
- Control port: 21. Use 2121 if 21 is blocked.
- Data ports: 20000-21000. Server picks one per transfer and tells the client.

## Commands (client -> server)
- `GET <name>`: download a file from `server_files/`.
- `PUT <name> <size>`: upload a file. Size is bytes.
- `LS`: list files in `server_files/`.
- `EXIT`: close the session.

Commands are plain text lines ending with `\n`.

## Responses (server -> client)
- `200 OK <port> [size] [info]`: command accepted. `<port>` is always present when a data socket is needed. `[size]` is bytes expected. `[info]` is optional text.
- `226 Transfer Complete`: work finished with no error.
- `550 <message>`: file problem or other user error.
- `500 <message>`: bad command or server error.

All responses are single lines ending with `\n`.

## Command Flow
- **GET**  
  1. Client sends `GET name`.  
  2. Server checks file. If found, replies `200 OK <port> <size> name`.  
  3. Client connects to `<port>` and reads `<size>` bytes.  
  4. Server closes data socket and sends `226 Transfer Complete`.

- **PUT**  
  1. Client sends `PUT name size`.  
  2. Server replies `200 OK <port> <size> name`.  
  3. Client connects to `<port>` and sends exactly `<size>` bytes.  
  4. Server saves the file and sends `226 Transfer Complete`.  
  5. If the byte counts do not match, server sends `550 Transfer Aborted`.

- **LS**  
  1. Client sends `LS`.  
  2. Server creates listing text, replies `200 OK <port> <size> listing`.  
  3. Client connects to `<port>` and reads `<size>` bytes.  
  4. Server finishes with `226 Transfer Complete`.

- **EXIT**  
  1. Client sends `EXIT`.  
  2. Server replies `226 Transfer Complete Goodbye` and closes the socket.

## Session Rules
- One command at a time. Wait for the final response before sending another.
- Filenames use only letters, numbers, dot, dash, underscore.
- Data sockets time out after 60 seconds.
- Server pre-creates `server_files/` and `logs/` if missing.

## Concurrency
- Server listens on the control port and starts one thread per client.
- Each transfer uses its own data socket, so clients do not step on each other.
