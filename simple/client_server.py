import socket

host = "localhost"
data_payload = 2048
backlog = 5


def echo_server(port: int) -> None:
    """A simple echo server"""
    # Create a TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Enable reuse address/port
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to the port
    server_address = (host, port)
    print(f"Starting up echo server on port {server_address}")

    sock.bind(server_address)

    # Listen to clients, backlog argument specifies the max no. of queued connections
    sock.listen(backlog)

    while True:
        print("Waiting to receive message from client")

        client, address = sock.accept()

        data = client.recv(data_payload)

        if data:
            print(f"Data: {data}")

            client.send(data)

            print(f"sent {data} bytes back to {address}")

        # end connection
        client.close()


echo_server(port=8080)
