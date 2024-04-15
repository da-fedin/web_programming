"""
Changing a socket to the blocking/non-blocking mode
"""
import socket


def test_socket_modes():
    """
    Test the blocking or non-blocking mode
    """
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.setblocking(True)
    my_socket.settimeout(0.5)
    my_socket.bind(("127.0.0.1", 0))
    socket_address = my_socket.getsockname()

    print(f"Trivial Server launched on socket: {str(socket_address)}")

    while True:
        my_socket.listen(1)


test_socket_modes()
