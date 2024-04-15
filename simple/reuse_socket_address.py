"""run a socket server always on a specific port even after it is closed intentionally
or unexpectedly."""
import socket


def reuse_socket_addr(local_port: int) -> None:
    """Reuse a socket server always on a specific port"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Get the old state of the SO_REUSEADDR option
    old_state = sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR)

    print("Old sock state: %s" % old_state)

    # Enable the SO_REUSEADDR option
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    new_state = sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR)

    print("New sock state: %s" % new_state)

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    srv.bind(("", local_port))

    srv.listen(1)

    print(f"Listening on port: {local_port}")

    while True:
        try:
            connection, addr = srv.accept()

            print(f"Connected by {addr[0]}:{addr[1]}")

        except KeyboardInterrupt:
            break

        except OSError as msg:
            print(f"{msg}")


reuse_socket_addr(local_port=8282)
