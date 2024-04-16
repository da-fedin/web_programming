"""
Multi-connection client.
Send defined amount of messages to server and receive echo.
"""

import socket
import selectors
import types


def start_connections(host: str, port: int, connections: int) -> None:
    """Start connections"""
    # Set address to connect with
    server_addr = (host, port)

    # Iterate through connection number
    for i in range(0, connections):
        # Set id to current connection
        connection_id = i + 1

        print(f"Starting connection {connection_id} to {server_addr}")

        # Create socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Set a socket to non-blocking mode (not block execution by send/recv ... operations)
        client_socket.setblocking(False)

        # Initiate a connection to a remote address
        client_socket.connect_ex(server_addr)

        # Set combination of events for a socket connection
        connection_events = selectors.EVENT_READ | selectors.EVENT_WRITE

        # Set data to send
        data = types.SimpleNamespace(
            connid=connection_id,
            msg_total=sum(len(_) for _ in messages),
            recv_total=0,
            messages=messages.copy(),
            outb=b"",
        )

        selector.register(client_socket, connection_events, data=data)


def service_connection(key, mask: int) -> None:
    """Service connection"""
    sock = key.fileobj
    data = key.data

    # Check if there is a read event for socket
    if mask & selectors.EVENT_READ:
        # Set maximum number of bytes to receive in a single call
        max_bytes_in_call = 1024

        # Receive defined amount of data
        recv_data = sock.recv(max_bytes_in_call)

        # Check if there is a data in call
        if recv_data:
            print(f"Received {recv_data!r} from connection {data.connid}")

            # Count requests
            data.recv_total += len(recv_data)

        # Check if there is no data or
        # amount of data received is equal to the total expected message size
        if not recv_data or data.recv_total == data.msg_total:
            print(f"Closing connection {data.connid}")

            # Unregister socket from selector
            selector.unregister(sock)

            # Close socket
            sock.close()

    # Check if there is a write event for socket
    if mask & selectors.EVENT_WRITE:
        # Check if there is no messages yet
        if not data.outb and data.messages:
            # Remove first item of 'messages' list and assign its value to 'data.outb' field
            data.outb = data.messages.pop(0)

        # Check if there is some message to send
        if data.outb:
            print(f"Sending {data.outb!r} to connection {data.connid}")

            # Send message to server
            sent = sock.send(data.outb)

            # Add message sent to list of sent messages
            data.outb = data.outb[sent:]


def start_multi_connection_client(
    connection_host: str, connection_port: int, number_of_connections: int
) -> None:
    """Start the multi-connection client"""
    start_connections(
        host=connection_host,
        port=connection_port,
        connections=number_of_connections,
    )

    # Start listening
    try:
        while True:
            # Set list of tuples like (key, mask) by invoking select() system call
            events = selector.select(timeout=1)

            # Check for event
            if events:
                for key, mask in events:
                    # key - represent the registered file object along with associated metadata
                    # mask - integer representing the events that have occurred on the file object

                    # Serve connection
                    service_connection(key=key, mask=mask)

            # If mappings dictionary is empty, there are no registered file objects
            # with the selector.
            if not selector.get_map():
                break

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

# Set message list to be sent to server (as a sequence of bytes)
messages = [b"Message 1 from client.", b"Message 2 from client."]

# Run client
start_multi_connection_client(
    connection_host=HOST,
    connection_port=PORT,
    number_of_connections=len(messages),
)
