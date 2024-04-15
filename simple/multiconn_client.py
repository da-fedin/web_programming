"""Multi-connection client"""

import socket
import selectors
import types

sel = selectors.DefaultSelector()
messages = [b"Message 1 from client.", b"Message 2 from client."]

HOST = "127.0.0.1"
PORT = 65432


def multi_connection_client(
    connection_host: str, connection_port: int, number_of_connections: int
):
    def start_connections(host, port, connections):
        server_addr = (host, port)

        for i in range(0, connections):
            connection_id = i + 1

            print(f"Starting connection {connection_id} to {server_addr}")

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            sock.setblocking(False)

            sock.connect_ex(server_addr)

            connection_events = selectors.EVENT_READ | selectors.EVENT_WRITE

            data = types.SimpleNamespace(
                connid=connection_id,
                msg_total=sum(len(m) for m in messages),
                recv_total=0,
                messages=messages.copy(),
                outb=b"",
            )

            sel.register(sock, connection_events, data=data)

    def service_connection(key, mask):
        sock = key.fileobj
        data = key.data

        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)  # Should be ready to read

            if recv_data:
                print(f"Received {recv_data!r} from connection {data.connid}")

                data.recv_total += len(recv_data)

            if not recv_data or data.recv_total == data.msg_total:
                print(f"Closing connection {data.connid}")

                sel.unregister(sock)

                sock.close()

        if mask & selectors.EVENT_WRITE:
            if not data.outb and data.messages:
                data.outb = data.messages.pop(0)

            if data.outb:
                print(f"Sending {data.outb!r} to connection {data.connid}")

                sent = sock.send(data.outb)  # Should be ready to write
                data.outb = data.outb[sent:]

    start_connections(connection_host, connection_port, number_of_connections)

    try:
        while True:
            events = sel.select(timeout=1)

            if events:
                for key, mask in events:
                    service_connection(key, mask)

            # Check for a socket being monitored to continue.
            if not sel.get_map():
                break

    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
        sel.close()


multi_connection_client(
    connection_host=HOST, connection_port=PORT, number_of_connections=2
)
