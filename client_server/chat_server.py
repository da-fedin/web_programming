"""Chat server that can handle several hundred or a large number
of client connections."""
import select  # Support asynchronous I/O on multiple file descriptors
import socket  # Provide socket operations and some related functions
import sys  # Key sensitivity
import signal  # Set handlers for asynchronous events
import pickle  # Serialization
import struct  # Interpret bytes as packed binary data
import argparse  # Parse arguments
from typing import Any

SERVER_HOST = "localhost"
CHAT_SERVER_NAME = "server"


# Some utilities
def send(channel: socket.socket, *args) -> None:
    """send pickled data over a network channel"""
    # Pickle the passed arguments into a byte string
    buffer = pickle.dumps(args)

    # Calculates the length of the pickled data and convert it to network byte order
    value = socket.htonl(len(buffer))

    # Pack the converted length into a binary string
    size = struct.pack("L", value)

    # Send the packed size information over the network channel
    channel.send(size)

    # Send the packed data over the network channel
    channel.send(buffer)


def receive(channel: socket.socket) -> str | Any:
    """Receive pickled data over a network channel"""
    # Return size in bytes of the struct described by the format string
    size = struct.calcsize("L")

    # Receive a fixed number of bytes from the network channel
    size = channel.recv(size)

    try:
        # Convert a 32-bit integer from network to host byte order
        size = socket.ntohl(struct.unpack("L", size)[0])

    except struct.error:
        return ""

    buf = ""

    # Start a loop that continues until the length of the accumulated data
    while len(buf) < size:
        # Receives additional bytes of data from the network channel
        buf = channel.recv(size - len(buf))

    # Unpickle the received data
    return pickle.loads(buf)[0]


class ChatServer:
    """An example chat server using select"""

    def __init__(self, port, backlog=5):
        self.clients = 0  # Number of clients
        self.client_map = (
            {}
        )  # Dict, mapping of client socket objects to information about those clients
        self.outputs = []  # List of client sockets
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((SERVER_HOST, port))
        print(f"Server listening to port: {port} ...")
        self.server.listen(backlog)

        # Set a signal handler for a specific signal
        signal.signal(
            signal.SIGINT, lambda signum, frame: self.signal_handler()
        )

    def signal_handler(self):
        """Handle a shutdown signal received by the server"""
        print("Shutting down server...")

        # Iterate client sockets that the server is currently communicating with
        for output in self.outputs:
            # Close each socket
            output.close()

        # Close the sever socket
        self.server.close()

    def get_client_name(self, connected_client: socket.socket) -> str:
        """Return the name of the client connected to the server"""
        # Retrieve information about the client
        info = self.client_map[connected_client]

        # Unpack the information about the client
        connected_host, connected_name = info[0][0], info[1]

        # Create a unique identifier for the client (name@host)
        return "@".join((connected_name, connected_host))

    def run(self):
        """Run the server"""
        inputs = [self.server, sys.stdin]

        self.outputs = []

        running = True

        while running:
            try:
                # Monitor a list of inputs for readability, outputs for writability and
                # an empty list ([]) for exceptional conditions
                readable, writeable, exceptional = select.select(
                    inputs, self.outputs, []
                )

            # Handle I/O related errors
            except OSError:
                break

            # Iterate a list of inputs
            for sock in readable:
                if sock == self.server:
                    # handle the server socket
                    client, address = self.server.accept()

                    print(
                        "Chat server: got connection %d from %s"
                        % (client.fileno(), address)
                    )

                    # Read the login name
                    cname = receive(client).split("NAME: ")[1]

                    # Compute client name and send back
                    self.clients += 1

                    send(client, "CLIENT: " + str(address[0]))

                    inputs.append(client)

                    self.client_map[client] = (address, cname)

                    # Send joining information to other clients
                    msg = "\n(Connected: New client (%d) from %s)" % (
                        self.clients,
                        self.get_client_name(client),
                    )

                    for output in self.outputs:
                        send(output, msg)

                    self.outputs.append(client)

                elif sock == sys.stdin:
                    # handle standard input
                    running = False

                else:
                    # handle all other sockets
                    try:
                        data = receive(sock)
                        if data:
                            # Send as new client's message...
                            msg = (
                                "\n#["
                                + self.get_client_name(sock)
                                + "]>>"
                                + data
                            )

                            # Send data to all except ourselves
                            for output in self.outputs:
                                if output != sock:
                                    send(output, msg)

                        else:
                            print("Chat server: %d hung up" % sock.fileno())

                            self.clients -= 1

                            sock.close()

                            inputs.remove(sock)

                            self.outputs.remove(sock)

                            # Sending client leaving information to others
                            msg = (
                                "\n(Now hung up: Client from %s)"
                                % self.get_client_name(sock)
                            )

                            for output in self.outputs:
                                send(output, msg)

                    except OSError:
                        # Remove
                        inputs.remove(sock)

                        self.outputs.remove(sock)

        self.server.close()


class ChatClient:
    """A command line chat client using select"""

    def __init__(self, name, port, host=SERVER_HOST):
        self.name = name
        self.connected = False
        self.host = host
        self.port = port
        # Initial prompt
        self.prompt = (
            "[" + "@".join((name, socket.gethostname().split(".")[0])) + "]> "
        )

        # Connect to server at port
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            self.sock.connect((host, self.port))

            print("Now connected to chat server@ port %d" % self.port)

            self.connected = True

            # Send my name...
            send(self.sock, "NAME: " + self.name)

            data = receive(self.sock)

            # Contains client address, set it
            addr = data.split("CLIENT: ")[1]

            self.prompt = "[" + "@".join((self.name, addr)) + "]> "

        except OSError:
            print("Failed to connect to chat server @ port %d" % self.port)

            sys.exit(1)

    def run(self):
        """Chat client main loop"""
        while self.connected:
            try:
                sys.stdout.write(self.prompt)

                sys.stdout.flush()

                # Wait for input from stdin and socket
                readable, writeable, exceptional = select.select(
                    [0, self.sock], [], []
                )

                for sock in readable:
                    if sock == 0:
                        data = sys.stdin.readline().strip()

                        if data:
                            send(self.sock, data)

                    elif sock == self.sock:
                        data = receive(self.sock)

                        if not data:
                            print("Client shutting down.")
                            self.connected = False

                            break

                        else:
                            sys.stdout.write(data + "\n")

                            sys.stdout.flush()

            except KeyboardInterrupt:
                print(" Client interrupted. " "")

                self.sock.close()

                break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Socket Server Example with Select"
    )
    parser.add_argument("--name", action="store", dest="name", required=True)

    parser.add_argument(
        "--port", action="store", dest="port", type=int, required=True
    )

    given_args = parser.parse_args()

    port = given_args.port

    name = given_args.name

    if name == CHAT_SERVER_NAME:
        server = ChatServer(port)

        server.run()

    else:
        client = ChatClient(name=name, port=port)

        client.run()
