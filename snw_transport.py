# author-Charan
import socket               # importing socket module

def create_server_socket():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    # UDP socket initialization using DATAGRAM
    return server_socket

def bind(server_socket, server_address):        
    server_socket.bind(server_address)                                  # binding socket to specified address

def create_client_socket():                                         
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    # UDP socket initialization using DATAGRAM
    return client_socket

def send_data(socket, data, address):
    socket.sendto(data, address)                                        # sending data to specific address through socket

def receive_data(socket, buffer_size):
    data, address = socket.recvfrom(buffer_size)                        # receive data from socket
    return data, address

def send_ack(socket, address, ack_message):                             # sending ACK
    socket.sendto(ack_message, address)

def receive_ack(socket, buffer_size):
    ack, _ = socket.recvfrom(buffer_size)                               # receiving ACK
    return ack

def close(socket):          
    socket.close()                                                      # closing socket
