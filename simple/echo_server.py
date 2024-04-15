"""echo-server"""

import socket

HOST = "127.0.0.1"
PORT = 65432


def echo_server(host: str, port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))

        server_socket.listen()

        conn, addr = server_socket.accept()

        with conn:
            print(f"Connected by {addr}")

            while True:
                data = conn.recv(1024)

                if not data:
                    break

                conn.sendall(data)


echo_server(host=HOST, port=PORT)
