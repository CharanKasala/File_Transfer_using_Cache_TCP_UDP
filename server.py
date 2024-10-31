# author-Charan
import os                                   # Importing necessary modules from other python files
import sys
import threading
import time
import select

import tcp_transport as tcp_t
import snw_transport as snw_t


if len(sys.argv) != 3:                          # condition to check if number of arguments entered is correct
    print("Usage: python server.py <server_port> <protocol>")
    sys.exit(1)

try:
    port = int(sys.argv[1])                     # Reading the value of server port.
except ValueError:
    print("Port must be a valid integer")
    sys.exit(1)

protocol = sys.argv[2]                                            

if protocol != "tcp" and protocol != "snw":     # Reading the entered protocol
    print("Protocol should be 'tcp' or 'snw'.")
    sys.exit(1)    

script_directory = os.path.dirname(os.path.abspath(__file__))       
subdirectory = "server_files"
subdirectory_path = os.path.join(script_directory, subdirectory)    

if not os.path.exists(subdirectory_path):                           # condition to check if directory client_files is present at server location
    print("No folder with name:",subdirectory,"found. Creating folder:",subdirectory,"now")
    os.makedirs(subdirectory_path)                                  # creating new directory named server_files at server location if not present

if protocol == "tcp":                                               # Code for client Implementation if TCP protocol is selected
    trans_protocol=tcp_t
    print("TCP protocol selected")
    server_socket = trans_protocol.create_server_socket()           # creating server socket
    server_address = ('localhost', port)

    trans_protocol.bind(server_socket, server_address)
    trans_protocol.listen(server_socket,10)

    print("Server is listening for incoming connections...")

    def handle_client(client_socket):                               # function to handle client communications
        try:
            while True:
                data = trans_protocol.receive_data(client_socket, 1024)
                if not data:
                    break

                received_data = data.decode('utf-8')
                print(f"Received data from client --> {received_data}")        # displaying the message received from client

                if received_data.strip() == "quit":
                    print("Client connection closed\n")
                    
                elif received_data.startswith("put "):                          # Code for handling put command entered by the user
                    message_parts = received_data.split()
                    if len(message_parts) == 2:
                        filename = message_parts[1]
                        
                        save_path = os.path.join(subdirectory_path, filename)
                        
                        try:
                            with open(save_path, 'wb') as file:                     # receiving file from client and saving it at server location
                                while True:
                                    file_data = trans_protocol.receive_data(client_socket, 1024)
                                    if file_data.endswith(b'FILE_TRANSFER_COMPLETE'):
                                        file.write(
                                            file_data[:-len(b'FILE_TRANSFER_COMPLETE')])
                                        print(f"Received and saved file '{filename}'.\n")
                                        break
                                    file.write(file_data)
                        except Exception as e:
                            print(f"Error while saving file '{filename}': {e}")
                    else:
                        print("Invalid 'put' command format.")
                elif received_data.startswith("get "):                          # Code for handling get command entered by the user
                    
                    message_parts = received_data.split()
                    if len(message_parts) == 2:
                        filename1 = message_parts[1]
                        
                        
                        file_path = os.path.join(subdirectory_path, filename1)
                        

                        if os.path.exists(file_path):                       # checking filename given by the user exists in server_files folder
                            trans_protocol.send_data(client_socket, b"SERVER") # reading the data from file and sending it to cache
                            with open(file_path, 'rb') as file:
                                while True:
                                    data = file.read(1024)
                                    if not data:
                                        break
                                   
                                    trans_protocol.send_data(client_socket, data)
                                trans_protocol.send_data(client_socket,b'FILE_TRANSFER_COMPLETE')       # sending file transfer complete msg to indicate end of file
                            print(f"Sent file '{filename1}' to the Cache.")
                        else:
                            trans_protocol.send_data(client_socket, b"FILE_NOT_FOUND")                  # sending file not found message if file is not present
                            print(
                                f"File '{filename1}' not found on the server. message sent to cache")
                    else:
                        print("Invalid 'get' command format.")
                else:
                    response = f"Received: {received_data}"
                    trans_protocol.send_data(client_socket, response.encode('utf-8'))                   # message exchanges between client and server
        except Exception as e:
                print(f"Error while handling the client: {e}")
        finally:            
                trans_protocol.close(client_socket) 

    while True:
        client_socket, client_address = trans_protocol.accept(server_socket)    # accepting connection request from clients
        print(f"Received connection from {client_address}")

        client_thread = threading.Thread(target=handle_client, args=(client_socket,))       # accepting multiple connections using threading
        client_thread.start()
    
    trans_protocol.close(server_socket)

elif protocol == "snw":                      # Code for server Implementation if SNW protocol is selected
  
    print("SNW protocol selected")
    trans_protocol=snw_t


    server_address = ('localhost', port)

    server_socket = trans_protocol.create_server_socket()       # creating server socket
    trans_protocol.bind(server_socket, server_address)
    print("Server is listening for incoming connections...")

    while True:
        try:
            
            message,client_address=trans_protocol.receive_data(server_socket, 1024)
            
            received_msg=message.decode('utf-8')
            
            print("Connection received from Client",client_address)
            if received_msg.strip() == "quit":
                print("Client connection closed\n")
                    
            elif received_msg.startswith("put "):               # Code for handling put command entered by the user
               
               
                parts = received_msg.split()
                if len(parts) == 2:
                    filename = parts[1]
                
                
                    len_message, _ = trans_protocol.receive_data(server_socket, 1024)       # receiving the LEN message from sender
                    len_timeout=time.time()
                    len_parts = len_message.decode('utf-8').split(':')

                    if len(len_parts) == 2 and len_parts[0] == "LEN":
                        expected_bytes = int(len_parts[1])                              # Storing the expected number of bytes to be received from sender
                        received_data = b""
                        
                        save_path = os.path.join(subdirectory_path, filename)
                            
                        try:    
                            with open(save_path, 'wb') as file:                          # writing the received data from sender to file at server location
                                received_bytes = 0
                                ack_timeout = time.time()
                                while received_bytes < expected_bytes:
                                    
                                    if time.time() - len_timeout > 1:                      #checking for timeout if no data is received after LEN msg
                                        print("Did not receive data. Terminating.")
                                        trans_protocol.close(server_socket)
                                        sys.exit(1)
                                    chunk, _ = trans_protocol.receive_data(server_socket, 1024)
                                    received_bytes += len(chunk)
                                    file.write(chunk)
                                    trans_protocol.send_ack(server_socket, client_address, b'ACK')          # sending  ACK to sender that chunk is received
                                
                                    if time.time() - ack_timeout > 1:                       # checking for timeout if no data is received after ACK is sent
                                        print("Data transmission terminated prematurely.")
                                        trans_protocol.close(server_socket)
                                        sys.exit(1)
                                
                                if received_bytes == expected_bytes:
                                   print(f"Received and saved file '{filename}'.\n")
                                   trans_protocol.send_data(server_socket, b'FIN', client_address)      # sending FIN message to sender that file transfer is complete
                                else:
                                    trans_protocol.send_data(server_socket, b'INCOMPLETE', client_address)
                        except Exception as e:
                                    print(f"Error while saving file '{filename}': {e}")
                    else:
                        print("Invalid 'LEN' message format")                 
                else:
                        print("Invalid 'put' command format.")

            elif received_msg.startswith("get "):                   # Code for handling get command entered by the user
                
                if not message:
                    break
            
                requested_data = message.decode('utf-8')
                print("At Server requested command from cache is ", requested_data)
            
                message_parts = requested_data.split()
                if len(message_parts) == 2:
                    filename = message_parts[1]
            
                if filename:
                
                    server_file_path = os.path.join(subdirectory_path, filename)
                    

                    if os.path.exists(server_file_path):                            # checking filename given by the user exists in server_files folder
                        trans_protocol.send_data(server_socket, b"SERVER",client_address)   # sending file origin location to receiver
                        print(f"File found in Server: Sending file '{filename}' to the Cache.")

                        try:
                            with open(server_file_path, 'rb') as file:
                                trans_protocol.send_data(server_socket, requested_data.encode('utf-8'), client_address)    
                                data = file.read()

                            len_message = f"LEN:{len(data)}"
                           

                            trans_protocol.send_data(server_socket, len_message.encode('utf-8'), client_address)    # sending LEN message to the receiver i.e., cache

                            chunk_size = 1000            # deciding the chunk size
                            start = 0

                            while start < len(data):
                                end = start + chunk_size
                                chunk = data[start:end]     # dividing the data into chunks
                                trans_protocol.send_data(server_socket, chunk, client_address)
                                start_time=time.time()
                                while True:
                                    if time.time() - start_time > 1:                    # Checking for time out if no ACK is received after sending data packet
                                        print("Did not receive ACK. Terminating.")
                                        trans_protocol.close(server_socket)
                                        sys.exit(1)
                                    readable, _, _ = select.select([server_socket], [], [], 0.1)
                                    if readable:    
                                        ack = trans_protocol.receive_ack(server_socket, 1024)       # receiving ACK from the receiver for each chunk
                                        
                                        break
                                start = end 
                            confirm_msg, _ = trans_protocol.receive_data(server_socket, 1024)       # receiving FIN message from receiver if file transfer is successful
                            if confirm_msg.decode('utf-8') == "FIN":
                                print("File successfully sent to the cache from server.")
                            elif confirm_msg.decode('utf-8') == "INCOMPLETE":
                                print("Error in file transmission. Incomplete file received at client")    
                        except Exception as e:
                                    print(f"Error {e}")
                    else:                                               # sending message that requested file is not present at server location
                        trans_protocol.send_data(server_socket, "FILE_NOT_FOUND_AT_SERVER".encode('utf-8'),client_address)      # sending message that requested file is not present at server location
                

            else:
                print(f"Received message at server--> {received_msg} \n")           # message exchanges between client and server
                response = f"Received: {received_msg}"
                trans_protocol.send_data(server_socket, response.encode('utf-8'),client_address)
 
            
        except ConnectionResetError:
            print("Client disconnected abruptly.")
        except Exception as e:
            print(f"An error occurred: {e}")  

else:
    print("Invalid protocol selected")
