"""
Multi-connection server.
Get defined amount of messages from client and send echo.
"""

import socket
import selectors
import types


def accept_wrapper(socket_to_wrapp: socket.socket):
    """Accept the connection from client"""
    # Set the socket as ready to read
    connection, address = socket_to_wrapp.accept()

    print(f"Accepted connection from {address}")

    # Put the socket in non-blocking mode
    connection.setblocking(False)

    # Create object to store data
    data = types.SimpleNamespace(addr=address, inb=b"", outb=b"")

    # Set event as ready to be read and write
    events = selectors.EVENT_READ | selectors.EVENT_WRITE

    # Register the socket to be monitored
    selector.register(fileobj=connection, events=events, data=data)


def service_connection(key, mask):
    """Serve the connection"""
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        # Set maximum number of bytes to receive in a single call
        max_bytes_in_call = 1024

        # Receive defined amount of data
        recv_data = sock.recv(max_bytes_in_call)  # Should be ready to read

        # Check if there is a data in call
        if recv_data:
            # Count outbound data
            data.outb += recv_data

        else:
            print(f"Closing connection to {data.addr}")

            # Unregister the socket
            selector.unregister(sock)

            # Close the socket
            sock.close()

    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"Echoing {data.outb!r} to {data.addr}")

            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]


def start_multi_connection_server(host: str, port: int) -> None:
    """Start the multi connection server"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # Associate a socket with a specific network address
        server_socket.bind((host, port))

        server_socket.listen()

        # Configure the socket in non-blocking mode
        server_socket.setblocking(False)

        # Register the socket to be monitored
        selector.register(
            fileobj=server_socket, events=selectors.EVENT_READ, data=None
        )

        # Start listening
        try:
            while True:
                # Set list of tuples like (key, mask) by invoking select() system call
                events = selector.select(
                    timeout=None
                )  # blocks until there are sockets ready for I/O

                for key, mask in events:
                    # Check if there is a data in event
                    # If No (it’s from the listening socket, you need to accept the connection)
                    if key.data is None:
                        accept_wrapper(socket_to_wrapp=key.fileobj)

                    # If Yes (it’s a client socket that’s already been accepted,
                    # and you need to service it)
                    else:
                        # Serve connection
                        service_connection(key=key, mask=mask)

        # Catch server interruption by Ctrl-C
        except KeyboardInterrupt:
            print("Caught keyboard interrupt, exiting")

        # Close
        finally:
            selector.close()


# Set address for connection
HOST = "127.0.0.1"
PORT = 65432

# Set selector for events during connection
selector = selectors.DefaultSelector()

# Run server
start_multi_connection_server(host=HOST, port=PORT)
