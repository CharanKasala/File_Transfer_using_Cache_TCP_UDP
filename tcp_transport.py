# author-Charan
import socket                             # importing socket module


def create_server_socket():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket creation using STREAM
    return server_socket


def bind(server_socket, server_address):
    server_socket.bind(server_address)                                  # binding socket to specific address


def listen(server_socket, backlog):                                    
    server_socket.listen(backlog)                                       # listening to connection requests


def accept(server_socket):                                              
    client_socket, client_address = server_socket.accept()              # accepting connection request
    return client_socket, client_address


def create_client_socket():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # TCP socket creation using STREAM
    return client_socket


def connect(client_socket, server_name, server_port):                   
    server_address = (server_name, server_port)
    client_socket.connect(server_address)                               # establishing socket connection


def send_data(socket, data):
    socket.send(data)                                                   # sending data to socket


def receive_data(socket, buffer_size):
    data = socket.recv(buffer_size)                                      # receiving data from socket
    return data


def close(socket):
    socket.close()                                                        # closing socket
