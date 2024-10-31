# Author- Charan
import os                        # Importing necessary modules from other python files
import sys
import socket
import time
import select

import tcp_transport as tcp_t       
import snw_transport as snw_t

if len(sys.argv) != 6:                  #condition to check if number of arguments entered is correct
    print("Usage: python client.py <server_name> <server_port> <cache_name> <cache_port> <protocol>")
    sys.exit(1)

server_name = sys.argv[1]               # Reading the entered server name

try:
    server_port = int(sys.argv[2])      # Reading the value of server port.
except ValueError:
    print("Port must be a valid number")
    sys.exit(1)



cache_name = sys.argv[3]

try:
    cache_port = int(sys.argv[4])           # Reading the value of cache port.
except ValueError:
    print("Cache Port must be a valid number")
    sys.exit(1)


protocol = sys.argv[5]                      # Reading the entered protocol

if protocol != "tcp" and protocol != "snw":             
    print("Protocol should be 'tcp' or 'snw'.")
    sys.exit(1)  

script_directory = os.path.dirname(os.path.abspath(__file__))
subdirectory = "client_files"
subdirectory_path = os.path.join(script_directory, subdirectory)

if not os.path.exists(subdirectory_path):                   # condition to check if directory client_files is present at cache location
    print("No folder with name:",subdirectory,"found. Creating folder:",subdirectory,"now")
    os.makedirs(subdirectory_path)                          # creating new directory named client_files at client location if not present

if protocol == "tcp":                                        # Code for client Implementation if TCP protocol is selected
    trans_protocol=tcp_t
    print("TCP protocol selected")

    client_socket = trans_protocol.create_client_socket()           # creating socket for client server communication

    trans_protocol.connect(client_socket, server_name, server_port)

    cache_socket = trans_protocol.create_client_socket()            # creating socket for client cache communication

    trans_protocol.connect(cache_socket, cache_name, cache_port)

    while True:

        message = input("Enter a command: ")                        # reading user input
        print("Awaiting server response.")
        if message == "quit":                                       
            print("Exiting program!")
            trans_protocol.close(client_socket)                     # closing socket if quit is entered
            
            break
        elif message.startswith("put "):                            # Code for handling put command entered by the user
            message_parts = message.split()
            if len(message_parts) == 2:
                filename = message_parts[1]
                file_path_put = os.path.join(subdirectory_path, filename)
                
                if os.path.exists(file_path_put):                   # checking filename given by the user exists in client_files folder
                    with open(file_path_put, 'rb') as file:         # reading the data from file and sending it to server
                            trans_protocol.send_data(client_socket, message.encode('utf-8'))
                            while True:             
                                data = file.read(1024)             
                                if not data:
                                    trans_protocol.send_data(client_socket, b'FILE_TRANSFER_COMPLETE')   # sending file transfer complete msg to indicate end of file
                                    break
                                trans_protocol.send_data(client_socket, data)
                            print(f"Server response:File successfully uploaded.\n")
                else:
                    print(f"File '{filename}' doesn't exist at Client.\n")         
            else:
                print("Invalid 'put' command format.")
        elif message.startswith("get "):                        # Code for handling get command entered by the user
        
            message_parts = message.split()
            if len(message_parts) == 2:
                filename = message_parts[1]
            
                trans_protocol.send_data(cache_socket, message.encode('utf-8')) # sending request to cache for file 

                data = trans_protocol.receive_data(cache_socket, 1024)

                if data.decode('utf-8') == "FILE_NOT_FOUND":                    # receiving file not found message from cache
                    print(f"File '{filename}' not found on the server.\n")
                else:
                    code_received=data.decode('utf-8')
                    file_path_get = os.path.join(subdirectory_path, filename)
                   
                    try:
                        with open(file_path_get, 'wb') as file:                 # receiving file from cache and saving it at client location
                            while True:
                                data = trans_protocol.receive_data(cache_socket, 1024)
                                
                                if data.endswith(b'FILE_TRANSFER_COMPLETE'):
                                    file.write(data[:-len(b'FILE_TRANSFER_COMPLETE')])
                                    if(code_received =="SERVER"):               # reading the file origin location i.e., if file is received from CACHE or SERVER
                                        print(f"Server response:File delivered from origin.\n")
                                    else:
                                        print(f"Server response:File delivered from cache.\n")    
                                    break
                                file.write(data)
                    except FileNotFoundError:
                        print(f"File '{filename}' could not be saved at client.")
                            
            else:
    
                print("Invalid 'get' command format.")
        else:                                                                   # message exchanges between client and server
            trans_protocol.send_data(client_socket, message.encode('utf-8'))
            response = trans_protocol.receive_data(client_socket, 1024)
            print(f"Server Response: {response.decode('utf-8')} \n")            # displaying server response

    trans_protocol.close(cache_socket)  
    trans_protocol.close(client_socket)

elif protocol == "snw":                                                     # Code for client Implementation if SNW protocol is selected
  
    print("SNW protocol selected")
    trans_protocol=snw_t

    server_address = (server_name,server_port)
    client_socket = trans_protocol.create_client_socket()                    # creating socket for client server communication
    cache_socket = trans_protocol.create_client_socket()                     # creating socket for client cache communication

    while True:

        message = input("Enter a command: ")                                 # reading user input command
        print("Awaiting server response.")
        if message == "quit":
            print("Exiting program!")

            trans_protocol.close(client_socket)                              # closing client socket if quit is entered
            break
        elif message.startswith("put "):                                     # Code for handling put command entered by the user
            message_parts = message.split()
            if len(message_parts) == 2:
                filename = message_parts[1]
                file_path_put = os.path.join(subdirectory_path, filename)     # checking filename given by the user exists in client_files folder
                if os.path.exists(file_path_put):                             # reading the data from file and sending it to server
                    with open(file_path_put, 'rb') as file:
                        trans_protocol.send_data(client_socket, message.encode('utf-8'), server_address)    
                        data = file.read()

                    len_message = f"LEN:{len(data)}"
                   

                    trans_protocol.send_data(client_socket, len_message.encode('utf-8'), server_address)        # sending LEN message to the receiver i.e., server

                    chunk_size = 1000               # deciding the chunk size
                    start = 0

                    while start < len(data):
                        end = start + chunk_size
                        chunk = data[start:end]         # dividing the data into chunks
                        trans_protocol.send_data(client_socket, chunk, server_address)
                        start_time=time.time()
                        while True:
                            if time.time() - start_time > 1:                            # Checking for time out if no ACK is received after sending data packet
                                print("Did not receive ACK. Terminating.")
                                trans_protocol.close(client_socket)
                                sys.exit(1)
                            readable, _, _ = select.select([client_socket], [], [], 0.1)    
                            if readable:    
                                ack = trans_protocol.receive_ack(client_socket, 1024)       # receiving ACK from the receiver for each chunk
                                
                                break
                        start = end
                    confirm_msg, _ = trans_protocol.receive_data(client_socket, 1024)       # receiving FIN message from receiver if file transfer is successful
                    if confirm_msg.decode('utf-8') == "FIN":        
                        print("Server response: File successfully uploaded.\n")
                    elif confirm_msg.decode('utf-8') == "INCOMPLETE":
                        print("Error in file transmission. Incomplete file received at server\n")
                        
                else:
                    print(f"File '{filename}' doesn't exist at Client.\n")
                     
            else:
                print("Invalid 'put' command format.")
        elif message.startswith("get "):
            message_parts = message.split()
            if len(message_parts) == 2:
                filename = message_parts[1]
                cache_server_address = (cache_name, cache_port)
                trans_protocol.send_data(cache_socket,message.encode('utf-8'),cache_server_address)

                file_origin_loc,_=trans_protocol.receive_data(cache_socket, 1024)       # reading the file origin location
                
                if(file_origin_loc.decode('utf-8') == "FILE_NOT_FOUND_AT_SERVER"):      # displaying message that requested file is not present at server
                    print(f"File '{filename}' not found on the server.\n")
                else:
                    rcvd_message,_=trans_protocol.receive_data(cache_socket, 1024)
                    parts = rcvd_message.split()
                    if len(parts) == 2:
                        filename = parts[1].decode('utf-8')
                        
                    
                        len_message, _ = trans_protocol.receive_data(cache_socket, 1024)                # receiving the LEN message from sender
                        len_timeout=time.time()
                        len_parts = len_message.decode('utf-8').split(':')

                        if len(len_parts) == 2 and len_parts[0] == "LEN":
                            expected_bytes = int(len_parts[1])                                          # Storing the expected number of bytes to be received from sender
                            received_data = b""
                            

                            file_path_get = os.path.join(subdirectory_path, filename) 
                               
                            try:    
                                with open(file_path_get, 'wb') as file:                                 # writing the received data from sender to file at client location
                                    received_bytes = 0
                                    ack_timeout = time.time()
                                    while received_bytes < expected_bytes:
                                        
                                        if time.time() - len_timeout > 1:                               # checking for timeout if no data is received after LEN msg
                                            print("Did not receive data. Terminating.\n")
                                            trans_protocol.close(cache_socket)
                                            sys.exit(1)
                                        chunk, _ = trans_protocol.receive_data(cache_socket, 1024)
                                        received_bytes += len(chunk)
                                        file.write(chunk)
                                        trans_protocol.send_ack(cache_socket, cache_server_address, b'ACK') # sending  ACK to sender that chunk is received
                                    
                                        if time.time() - ack_timeout > 1:                                 # checking for timeout if no data is received after ACK is sent
                                            print("Data transmission terminated prematurely.\n")
                                            trans_protocol.close(cache_socket)
                                            sys.exit(1)
                                    
                                    if received_bytes == expected_bytes:
                                        trans_protocol.send_data(cache_socket, b'FIN', cache_server_address)        # sending FIN message to sender that file transfer is complete
                                        if(file_origin_loc.decode('utf-8') == "SERVER"):                 # reading the file origin location i.e., if file is received from CACHE or SERVER
                                            print(f"Server response: File delivered from origin.\n")
                                        else:
                                            print(f"Server response: File delivered from Cache.\n")
                                    else:
                                        print("Error receiving file at Client")
                                        trans_protocol.send_data(cache_socket, b'INCOMPLETE', cache_server_address)
                            except Exception as e:
                                        print(f"Error while saving file '{filename}': {e}")
                        else:
                            print("Invalid 'LEN' message format") 
                    
        else:                                                                       # message exchanges between client and server
            trans_protocol.send_data(client_socket, message.encode('utf-8'),server_address)     
            response1, _ = trans_protocol.receive_data(client_socket, 1024)                     
            print(f"Server Response: {response1.decode('utf-8')} \n")
            
    trans_protocol.close(client_socket)                                            
else:
    print("Invalid protocol selected")