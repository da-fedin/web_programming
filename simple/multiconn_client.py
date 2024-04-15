"""Multi-connection client"""

import socket
import selectors
import types

HOST = "127.0.0.1"
PORT = 65432

selector = selectors.DefaultSelector()
messages = [b"Message 1 from client.", b"Message 2 from client."]


def multiconn_client(host: str, port: int, num_conns: int) -> None:
    server_addr = (host, port)

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

                selector.unregister(sock)
                sock.close()

        if mask & selectors.EVENT_WRITE:
            if not data.outb and data.messages:
                data.outb = data.messages.pop(0)

            if data.outb:
                print(f"Sending {data.outb!r} to connection {data.connid}")

                sent = sock.send(data.outb)  # Should be ready to write
                data.outb = data.outb[sent:]

    for i in range(0, num_conns):
        connid = i + 1

        print(f"Starting connection {connid} to {server_addr}")

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.setblocking(False)

        sock.connect_ex(server_addr)

        events = selectors.EVENT_READ | selectors.EVENT_WRITE

        data = types.SimpleNamespace(
            connid=connid,
            msg_total=sum(len(m) for m in messages),
            recv_total=0,
            messages=messages.copy(),
            outb=b"",
        )

        selector.register(sock, events, data=data)


multiconn_client(host=HOST, port=PORT, num_conns=2)
