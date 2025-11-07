import os
import socket
from shared.protocol import OK, DONE, ERR

class CommandHandler:
    def __init__(self, control_socket, server_files_dir="server_files"):
        self.control_socket = control_socket
        self.server_files_dir = server_files_dir
        self.data_port_range = range(20000, 21000)
        
    def _create_data_socket(self):
        """Creates and binds a data socket on an available port"""
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Try ports in range until one works
        for port in self.data_port_range:
            try:
                data_socket.bind(('', port))
                data_socket.listen(1)
                return data_socket, port
            except OSError:
                continue
                
        raise Exception("No available data ports")

    def _send_response(self, code, *args):
        """Sends a response to the control socket"""
        response = f"{code} {' '.join(map(str, args))}\n"
        self.control_socket.send(response.encode())

    def handle_get(self, filename):
        """Handle GET command - send file to client"""
        filepath = os.path.join(self.server_files_dir, filename)
        
        # Check if file exists
        if not os.path.exists(filepath):
            self._send_response(ERR, f"File {filename} not found")
            return
            
        try:
            # Get file size
            file_size = os.path.getsize(filepath)
            
            # Create data socket
            data_socket, port = self._create_data_socket()
            
            # Send OK with port and size
            self._send_response(OK, port, file_size, filename)
            
            # Accept client connection
            client_socket, _ = data_socket.accept()
            
            # Send file
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(8192)  # 8KB chunks
                    if not chunk:
                        break
                    client_socket.send(chunk)
                    
            # Clean up
            client_socket.close()
            data_socket.close()
            
            # Send completion
            self._send_response(DONE, "Transfer Complete")
            
        except Exception as e:
            self._send_response(ERR, f"Error sending file: {str(e)}")

    def handle_put(self, filename, size):
        """Handle PUT command - receive file from client"""
        try:
            size = int(size)
            filepath = os.path.join(self.server_files_dir, filename)
            
            # Create data socket
            data_socket, port = self._create_data_socket()
            
            # Send OK with port and size
            self._send_response(OK, port, size, filename)
            
            # Accept client connection
            client_socket, _ = data_socket.accept()
            
            # Receive and save file
            received_size = 0
            with open(filepath, 'wb') as f:
                while received_size < size:
                    chunk = client_socket.recv(min(8192, size - received_size))
                    if not chunk:
                        break
                    f.write(chunk)
                    received_size += len(chunk)
            
            # Clean up
            client_socket.close()
            data_socket.close()
            
            # Verify size
            if received_size == size:
                self._send_response(DONE, "Transfer Complete")
            else:
                os.remove(filepath)  # Delete incomplete file
                self._send_response(ERR, "Transfer Aborted - Size mismatch")
                
        except Exception as e:
            self._send_response(ERR, f"Error receiving file: {str(e)}")

    def handle_ls(self):
        """Handle LS command - send directory listing"""
        try:
            # Get directory listing
            files = os.listdir(self.server_files_dir)
            listing = '\n'.join(files) + '\n'
            listing_bytes = listing.encode()
            
            # Create data socket
            data_socket, port = self._create_data_socket()
            
            # Send OK with port and size
            self._send_response(OK, port, len(listing_bytes), "listing")
            
            # Accept client connection
            client_socket, _ = data_socket.accept()
            
            # Send listing
            client_socket.send(listing_bytes)
            
            # Clean up
            client_socket.close()
            data_socket.close()
            
            # Send completion
            self._send_response(DONE, "Transfer Complete")
            
        except Exception as e:
            self._send_response(ERR, f"Error listing directory: {str(e)}")

    def handle_exit(self):
        """Handle EXIT command"""
        self._send_response(DONE, "Transfer Complete Goodbye")
        self.control_socket.close()
