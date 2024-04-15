"""
Manipulate the default socket buffer size using a socket object's setsockopt() method.
"""
import socket

SEND_BUF_SIZE = 4096
RECV_BUF_SIZE = 4096


def modify_buff_size() -> None:
    """
    Modify the default socket buffer.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Get the size of the socket's send buffer
    buffer_size = sock.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)

    print(f"Buffer size [Before]: {buffer_size}")

    sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, SEND_BUF_SIZE)

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, RECV_BUF_SIZE)

    buffer_size = sock.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)

    print(f"Buffer size [After]: {buffer_size}")


modify_buff_size()
