"""
Create a few try-except code blocks and put one potential error type in each block.
"""
import sys
import socket


# import argparse

# # setup argument parsing
# parser = argparse.ArgumentParser(description="Socket Error Examples")
# parser.add_argument("--host", action="store", dest="host", required=False)
# parser.add_argument(
#     "--port", action="store", dest="port", type=int, required=False
# )
# parser.add_argument("--file", action="store", dest="file", required=False)
#
# given_args = parser.parse_args()
#
# host = given_args.host
# port = given_args.port
# filename = given_args.file


# Create socket
def create_socket() -> socket.socket:
    try:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    except OSError as error:
        print(f"Error creating socket: {error}")
        sys.exit(1)

    return my_socket


# Connect to given host/port
def connect_socket(
    my_socket: socket.socket, host_name: str, port_number: int
) -> None:
    try:
        my_socket.connect((host_name, port_number))

    except socket.gaierror as e:
        print(f"Address-related error connecting to server: {e}")
        sys.exit(1)

    except OSError as error:
        print(f"Connection error: {error}")
        sys.exit(1)


# Sending data
def send_data_to_socket(my_socket: socket.socket, filename: str) -> None:
    try:
        msg = f"GET {filename} HTTP/1.0\r\n\r\n"
        my_socket.sendall(msg.encode("utf-8"))

    except OSError as error:
        print("Error sending data: %s" % error)
        sys.exit(1)


# Receive data
def receive_data_from_socket(my_socket: socket, chunk_size: int) -> None:
    while True:
        # Waiting to receive data from remote host
        try:
            buf = my_socket.recv(chunk_size)

        except OSError as e:
            print("Error receiving data: %s" % e)
            sys.exit(1)

        if not len(buf):
            break

        # write the received data
        sys.stdout.write(buf.decode("utf-8"))


chunk_size = 2048
local_host = "localhost"
local_port = 8080

created_socket = create_socket()

connect_socket(
    created_socket, local_host, local_port
)  # :TODO: connection refused error

receive_data_from_socket(created_socket, chunk_size)
