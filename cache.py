# author-Charan
import os               # Importing necessary modules from other python files
import sys
import socket
import time
import select
import tcp_transport as tcp_t
import snw_transport as snw_t

if len(sys.argv) != 5:              #condition to check if number of arguments entered is correct
    print("Usage: python cache.py <cache_port> <server_name> <server_port> <protocol>")
    sys.exit(1)

try:
    cache_port = int(sys.argv[1])   # Reading the value of cache port.
except ValueError:
    print("Cache Port must be a valid number")
    sys.exit(1)

server_name = sys.argv[2]           # Reading the entered server name

try:
    server_port = int(sys.argv[3])  # Reading the entered server port
except ValueError:
    print("Server Port must be a valid number")
    sys.exit(1)

protocol = sys.argv[4]              # Reading the entered protocol

if protocol != "tcp" and protocol != "snw":
    print("Protocol should be 'tcp' or 'snw'.")
    sys.exit(1)    

script_directory = os.path.dirname(os.path.abspath(__file__))       
subdirectory = "cache_files"
subdirectory_path = os.path.join(script_directory, subdirectory)

if not os.path.exists(subdirectory_path):           # condition to check if directory cache_files is present at cache location
    print("No folder with name:",subdirectory,"found. Creating folder:",subdirectory,"now")  
    os.makedirs(subdirectory_path)                  # creating new directory named cache_files at cache location if not present

if protocol == "tcp":                               # Code for Cache Implementation if TCP protocol is selected
    print("TCP protocol selected")
    trans_protocol=tcp_t

    cache_server_socket = trans_protocol.create_server_socket()     #creating socket for cache server communication
    cache_server_address = ('localhost', cache_port)

    trans_protocol.bind(cache_server_socket, cache_server_address)  # binding server socket to server address
    trans_protocol.listen(cache_server_socket, 5)

    print("Cache is listening for incoming connections...")

    while True:
        client_socket, client_address = trans_protocol.accept(cache_server_socket)  # creating socket to accept connection request from client
        print(f"Received connection from {client_address}")
        while True:
            data = trans_protocol.receive_data(client_socket, 1024)                 # receiving message sent from client 
            if not data:
                break
        
            requested_data = data.decode('utf-8')
            
        
            message_parts = requested_data.split()
            if len(message_parts) == 2:
                filename = message_parts[1]
        
            if filename:                                # Module for sending data to client if file is present at cache
            

                cache_file_path = os.path.join(subdirectory_path, filename)
                
                
                if os.path.exists(cache_file_path):
                    trans_protocol.send_data(client_socket, b"CACHE")       # sending message to client that file is found at cache
                    print(f"File found in cache: Sending file '{filename}' to the client.")
                    with open(cache_file_path, 'rb') as file:               # reading the data from file and sending it to client
                        while True:
                            data = file.read(1024)
                            
                            if not data:
                                break
                            trans_protocol.send_data(client_socket, data)
                        trans_protocol.send_data(client_socket, b'FILE_TRANSFER_COMPLETE')   # sending file transfer complete msg to indicate end of file
                    print("File transfer completed from cache")      
                else:                                                                               
                    
                                                                                            # Module for requesting data from server and sending to client if file is not present at cache
                    print(f"File not found in Cache: Forwarding request to the server.")
                    
                    cache_client_socket = trans_protocol.create_client_socket()     # creating socket for cache server communication
                    server_address = (server_name, server_port) 
                    trans_protocol.connect(cache_client_socket, server_name, server_port)   # connecting from cache to server 
                    trans_protocol.send_data(cache_client_socket, requested_data.encode('utf-8'))
                    
                    server_resp = trans_protocol.receive_data(cache_client_socket, 1024)    # receiving the server response if file is present at server or not 
                    
                    cache_file_path1 = os.path.join(subdirectory_path, filename)
                    if server_resp.decode('utf-8') != "FILE_NOT_FOUND":                
                        with open(cache_file_path1, 'wb') as file:                     # receiving data from server and saving it at cache when file is present in server            
                            while True:
                                
                                data = trans_protocol.receive_data(cache_client_socket, 1024)
                                
                                if data.endswith(b'FILE_TRANSFER_COMPLETE'):
                                    file.write(data[:-len(b'FILE_TRANSFER_COMPLETE')])
                                    print(f"File '{filename}' stored in the cache.")
                                    break
                                file.write(data)
                    
                        trans_protocol.send_data(client_socket, b"SERVER")
                        
                        with open(cache_file_path1, 'rb') as file:                  # sending the file received from server to the client
                            while True:
                                data = file.read(1024)
                                if not data:
                                    break
                                trans_protocol.send_data(client_socket, data)
                            trans_protocol.send_data(client_socket, b'FILE_TRANSFER_COMPLETE')     # sending file transfer complete msg to indicate end of file
                        print("Data received from server to cache and sent to the client successfully")
                    else:
                        trans_protocol.send_data(client_socket, b"FILE_NOT_FOUND")          # sending file not found at server message to the client
                        print(f"Server Response: File '{filename}' not found on the server.\n")

                        
                    trans_protocol.close(cache_client_socket)
            
            else:
                print("Received an empty request from the client.")

        client_socket.close()

elif protocol == "snw":                             # Code for Cache Implementation if SNW UDP protocol is selected
    print("SNW protocol selected")
    trans_protocol=snw_t

    cache_server_socket = trans_protocol.create_server_socket() #creating socket for cache client communication
    cache_server_address = ('localhost', cache_port)

    trans_protocol.bind(cache_server_socket, cache_server_address) # binding server socket to server address

    print("Cache is listening for incoming connections...")

    while True:
            message,client_address=trans_protocol.receive_data(cache_server_socket, 1024)
            print("\n")
            print("Connection received from Client-->",client_address,"\n")
                        

            if not message:
                break
            
            requested_data = message.decode('utf-8')
            print("At cache requested message from client is ", requested_data)
        
            message_parts = requested_data.split()
            if len(message_parts) == 2:
                filename = message_parts[1]
        
            if filename:        # Module for sending data to client if file is present at cache
            
                cache_file_path = os.path.join(subdirectory_path, filename)
                

                if os.path.exists(cache_file_path):
                    trans_protocol.send_data(cache_server_socket, b"CACHE",client_address)   # sending message to client that file is found at cache
                    print(f"File found in cache: Sending file '{filename}' to the client.")

                    try:
                        with open(cache_file_path, 'rb') as file:           # reading the data from file and sending it to client
                            trans_protocol.send_data(cache_server_socket, requested_data.encode('utf-8'), client_address)    
                            data = file.read()

                        len_message = f"LEN:{len(data)}"
                    

                        trans_protocol.send_data(cache_server_socket, len_message.encode('utf-8'), client_address)      # sending LEN message to the receiver i.e., client

                        chunk_size = 1000               # deciding the chunk size
                        start = 0

                        while start < len(data):
                            end = start + chunk_size
                            chunk = data[start:end]     # dividing the data into chunks
                            trans_protocol.send_data(cache_server_socket, chunk, client_address)
                            start_time=time.time()
                            while True:
                                if time.time() - start_time > 1:                       # Checking for time out if no ACK is received after sending data packet
                                    print("Did not receive ACK. Terminating.")
                                    trans_protocol.close(cache_server_socket)
                                    sys.exit(1)
                                readable, _, _ = select.select([cache_server_socket], [], [], 0.1)  
                                if readable:    
                                    ack = trans_protocol.receive_ack(cache_server_socket, 1024)     # receiving ACK from the receiver for each chunk
                                    
                                    break
                            start = end
                        confirm_msg, _ = trans_protocol.receive_data(cache_server_socket, 1024)  # receiving FIN message from receiver if file transfer is successful
                        if confirm_msg.decode('utf-8') == "FIN":                               
                            print("File successfully sent to the client from cache.")
                        elif confirm_msg.decode('utf-8') == "INCOMPLETE":
                            print("Error in file transmission. Incomplete file received at client")
                    except Exception as e:
                                    print(f"Error {e}")
                               
                else:                                                               # Module for requesting data from server and sending to client if file is not present at cache
                    
                    cache_client_socket=trans_protocol.create_client_socket()       # creating socket for cache server communication
                    print(f"File not found in Cache: Forwarding request to the server.")
                    server_address = (server_name, server_port)
                    trans_protocol.send_data(cache_client_socket, message, server_address) # sending request from cache to server
                    file_origin_loc,_=trans_protocol.receive_data(cache_client_socket, 1024)    # receiving the server response if file is present at server or not 
                    
                    if(file_origin_loc.decode('utf-8') == "FILE_NOT_FOUND_AT_SERVER"):  

                        trans_protocol.send_data(cache_server_socket, b"FILE_NOT_FOUND_AT_SERVER",client_address)       # sending message to the client if file is not found on server
                        print(f"File Not found in Server: Sending this message to the client.")
                    else:
                         
                        rcvd_message,_=trans_protocol.receive_data(cache_client_socket, 1024)           # receiving data from server and saving it at cache when file is present in server
                        parts = rcvd_message.split()
                        if len(parts) == 2:
                            filename = parts[1].decode('utf-8')
                            print(f"Receiving file '{filename}' from server ")

                            len_message, _ = trans_protocol.receive_data(cache_client_socket, 1024)     # receiving the LEN message from sender i.e., Server
                            len_timeout=time.time()
                            len_parts = len_message.decode('utf-8').split(':')

                            if len(len_parts) == 2 and len_parts[0] == "LEN":                       
                                expected_bytes = int(len_parts[1])                                      # Storing the expected number of bytes to be received from sender
                                received_data = b""
                                

                            file_path_cache= os.path.join(subdirectory_path, filename)
                            try:    
                                with open(file_path_cache, 'wb') as file:                               # writing the received data from server to file at cache location
                                    received_bytes = 0
                                    ack_timeout = time.time()
                                    while received_bytes < expected_bytes:
                                        if time.time() - len_timeout > 1:                               # checking for timeout if no data is received after LEN msg
                                            print("Did not receive data. Terminating.")
                                            trans_protocol.close(cache_client_socket)
                                            sys.exit(1)
                                        chunk, _ = trans_protocol.receive_data(cache_client_socket, 1024)
                                        received_bytes += len(chunk)
                                        file.write(chunk)
                                        trans_protocol.send_ack(cache_client_socket, server_address, b'ACK')  # sending  ACK to sender that chunk is received   
                                        if time.time() - ack_timeout > 1:                               # checking for timeout if no data is received after ACK is sent
                                            print("Data transmission terminated prematurely.")
                                            trans_protocol.close(cache_client_socket)
                                            sys.exit(1)
                                     
                                    if received_bytes == expected_bytes:
                                        print("File received at the Cache Successfully")
                                        trans_protocol.send_data(cache_client_socket, b'FIN', server_address)       # sending FIN message to sender i.e., server
                                    else:
                                        print("Error receiving file at Cache")
                                        trans_protocol.send_data(cache_client_socket, b'INCOMPLETE', server_address)
                            except Exception as e:
                                        print(f"Error while saving file '{filename}': {e}")
                        else:
                            print("Invalid 'LEN' message format") 

                        trans_protocol.close(cache_client_socket)
                        cache_file_path_to_client = os.path.join(subdirectory_path, filename)
                        if os.path.exists(cache_file_path):
                            trans_protocol.send_data(cache_server_socket, b"SERVER",client_address)                 # sending the file received from server to the client
                            print(f"File found after receiving from server in cache: Sending file '{filename}' to the client.")
                                        
                            try:
                                with open(cache_file_path, 'rb') as file:
                                    trans_protocol.send_data(cache_server_socket, requested_data.encode('utf-8'), client_address)    
                                    data = file.read()

                                len_message = f"LEN:{len(data)}"                                                    


                                trans_protocol.send_data(cache_server_socket, len_message.encode('utf-8'), client_address)      # sending LEN message to the receiver i.e., client

                                chunk_size = 1000                # deciding the chunk size
                                start = 0

                                while start < len(data):
                                    end = start + chunk_size
                                    chunk = data[start:end]          # dividing the data into chunks
                                    trans_protocol.send_data(cache_server_socket, chunk, client_address)
                                    start_time=time.time()
                                    while True:
                                        if time.time() - start_time > 1:  # Checking for time out if no ACK is received after sending data packet
                                            print("Did not receive ACK. Terminating.")
                                            trans_protocol.close(cache_server_socket)
                                            sys.exit(1)
                                        readable, _, _ = select.select([cache_server_socket], [], [], 0.1) 
                                        if readable:    
                                            ack = trans_protocol.receive_ack(cache_server_socket, 1024)         # receiving ACK from the receiver for each chunk
                                            
                                            break
                                    start = end
                                confirm_msg, _ = trans_protocol.receive_data(cache_server_socket, 1024)         # receiving FIN message from receiver i.e., client if file transfer is successful
                                if confirm_msg.decode('utf-8') == "FIN":
                                    print("File successfully sent to the client from cache.")
                                elif confirm_msg.decode('utf-8') == "INCOMPLETE":
                                    print("Error in file transmission. Incomplete file received at client")
                            except Exception as e:
                                            print(f"Error {e}")
else:
     print("Invalid protocol selected")                                     # Invalid protocol