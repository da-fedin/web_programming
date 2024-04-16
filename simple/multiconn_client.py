"""Multi-connection client"""

import socket
import selectors
import types

selector = selectors.DefaultSelector()
messages = [b"Message 1 from client.", b"Message 2 from client."]

HOST = "127.0.0.1"
PORT = 65432


def start_connections(host: str, port: int, connections: int) -> None:
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
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read

        if recv_data:
            print(f"Received {recv_data!r} from connection {data.connid}")

            data.recv_total += len(recv_data)

        if not recv_data or data.recv_total == data.msg_total:
            print(f"Closing connection {data.connid}")

            selector.unregister(sock)

            sock.close()

    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)

        if data.outb:
            print(f"Sending {data.outb!r} to connection {data.connid}")

            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]


def multi_connection_client(
    connection_host: str, connection_port: int, number_of_connections: int
) -> None:
    start_connections(
        host=connection_host,
        port=connection_port,
        connections=number_of_connections,
    )

    try:
        while True:
            events = selector.select(
                timeout=1
            )  # list of tuples like (key, mask)

            if events:
                for key, mask in events:
                    # key - represent the registered file object along with associated metadata
                    # mask - integer representing the events that have occurred on the file object
                    service_connection(key=key, mask=mask)

            # If mappings dictionary is empty, there are no registered file objects
            # with the selector.
            if not selector.get_map():
                break

    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")

    finally:
        selector.close()


# Run script
multi_connection_client(
    connection_host=HOST, connection_port=PORT, number_of_connections=2
)
