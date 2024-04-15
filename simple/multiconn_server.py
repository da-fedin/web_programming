"""Multi-connection server"""

import socket
import selectors
import types

HOST = "127.0.0.1"
PORT = 65432

selector = selectors.DefaultSelector()


def multiconn_server(host: str, port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))

        server_socket.listen()

        # Configure the socket in non-blocking mode
        server_socket.setblocking(False)

        # Register the socket to be monitored
        selector.register(server_socket, selectors.EVENT_READ, data=None)

        def accept_wrapper(sock):
            conn, addr = sock.accept()  # Should be ready to read

            print(f"Accepted connection from {addr}")

            conn.setblocking(False)

            data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")

            events = selectors.EVENT_READ | selectors.EVENT_WRITE

            selector.register(conn, events, data=data)

        def service_connection(key, mask):
            sock = key.fileobj
            data = key.data

            if mask & selectors.EVENT_READ:
                recv_data = sock.recv(1024)  # Should be ready to read

                if recv_data:
                    data.outb += recv_data

                else:
                    print(f"Closing connection to {data.addr}")

                    selector.unregister(sock)

                    sock.close()

            if mask & selectors.EVENT_WRITE:
                if data.outb:
                    print(f"Echoing {data.outb!r} to {data.addr}")

                    sent = sock.send(data.outb)  # Should be ready to write
                    data.outb = data.outb[sent:]

        # Start event loop
        try:
            while True:
                # Get tuple for sockets (key, mask)
                events = selector.select(timeout=None)

                for key, mask in events:
                    if key.data is None:
                        accept_wrapper(key.fileobj)

                    else:
                        service_connection(key, mask)

        except KeyboardInterrupt:
            print("Caught keyboard interrupt, exiting")

        finally:
            selector.close()


multiconn_server(host=HOST, port=PORT)
