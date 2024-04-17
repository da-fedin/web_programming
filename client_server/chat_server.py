"""Chat server that can handle several hundred or a large number
of client connections."""
import argparse
import select
import socket
import sys
import signal
import pickle
import struct

SERVER_HOST = "localhost"
CHAT_SERVER_NAME = "server"


def send(channel, *args):
    """Send data over a network channel"""
    # Serialize the variable-length arguments passed to the function
    buffer = pickle.dumps(args)

    # Calculate serialized data size and convert to network byte order
    value = socket.htonl(len(buffer))

    # Pack message size into a binary representation suitable for network transmission
    size = struct.pack("L", value)

    # Send packed message size over the network channel
    channel.send(size)

    # Send serialized data over the network channel
    channel.send(buffer)


def receive(channel):
    """Receive a message from a network channel"""
    # Calculate the size of the message size field in bytes as unsigned long integer
    size = struct.calcsize("L")

    # Receive the message size field from the network channel
    size = channel.recv(size)

    try:
        # Unpack received message size field, convert the size from network byte order to host one
        size = socket.ntohl(struct.unpack("L", size)[0])

    except struct.error:  # as error:
        return ""

    # Store the received message data
    buf = ""

    # Loop that continues until the length of the received data equals expected message size
    while len(buf) < size:
        buf = channel.recv(size - len(buf))

    return pickle.loads(buf)[0]


class ChatServer:
    """An example chat server using select"""

    def __init__(self, port, backlog=5):
        self.clients = 0
        self.client_map = {}
        # List output sockets
        self.outputs = []
        # Create socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allow reusing local addresses for new socket connections even if the previous connection
        # on that address is still in the TIME_WAIT state
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Associate a socket with a specific network address
        self.server.bind((SERVER_HOST, port))

        print(f"Server listening to port: {port} ...")

        # Start listening maximum number of incoming connections
        self.server.listen(backlog)

        # Set up a signal handler to catch keyboard interrupts
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signum, frame):
        """Clean up client outputs"""
        # Close the server
        print("Shutting down server...")

        # Close existing client sockets
        for output in self.outputs:
            output.close()

        # Close server
        self.server.close()

    def get_client_name(self, client):
        """Return the name of the client"""
        info = self.client_map[client]

        host, name = info[0][0], info[1]

        return "@".join((name, host))

    def run(self):
        inputs = [self.server, sys.stdin]

        self.outputs = []

        running = True

        while running:
            try:
                readable, writeable, exceptional = select.select(
                    inputs, self.outputs, []
                )

            except OSError:
                break

        for sock in readable:
            if sock == self.server:
                # handle the server socket
                client, address = self.server.accept()

                print(
                    f"Chat server: got connection {client.fileno()} from {address}"
                )

                # Read the login name
                cname = receive(client).split("NAME: ")[1]

                # Compute client name and send back
                self.clients += 1

                send(client, "CLIENT: " + str(address[0]))

                inputs.append(client)

                self.clientmap[client] = (address, cname)

                # Send joining information to other clients
                msg = (
                    f"\n(Connected: New client {int(self.clients)}"
                    f" from {self.get_client_name(client)})"
                )

                for output in self.outputs:
                    send(output, msg)

                self.outputs.append(client)

            elif sock == sys.stdin:
                # handle standard input
                pass
                # junk = sys.stdin.readline()
                #
                # running = False

            else:
                # handle all other sockets
                try:
                    data = receive(sock)

                    if data:
                        # Send as new client's message...
                        msg = "\n#[" + self.get_client_name(sock) + "]>>" + data

                        # Send data to all except ourselves
                        for output in self.outputs:
                            if output != sock:
                                send(output, msg)

                    else:
                        print(f"Chat server: {int(sock.fileno())} hung up")

                        self.clients -= 1

                        sock.close()

                        inputs.remove(sock)

                        self.outputs.remove(sock)

                        # Sending client leaving information to others
                        msg = f"\n(Now hung up: Client from {self.get_client_name(sock)})"

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

            print(f"Now connected to chat server@ port {int(self.port)}")

            self.connected = True

            # Send my name...
            send(self.sock, "NAME: " + self.name)

            data = receive(self.sock)

            # Contains client address, set it
            addr = data.split("CLIENT: ")[1]

            self.prompt = "[" + "@".join((self.name, addr)) + "]> "

        except OSError:
            print(f"Failed to connect to chat server @ port {int(self.port)}")

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
                print(" Client interrupted.")

                self.sock.close()

                break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Socket ServerExample with Select"
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
        sys.stdout.write("Starting client server")
        client.run()
