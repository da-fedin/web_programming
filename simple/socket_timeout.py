"""
Manipulate the default values of certain properties of a socket
library, for example, the socket timeout.
"""
import socket


def test_socket_timeout():
    """
    Get the default timeout value and set a specific timeout value.
    """
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    default_timeout = my_socket.gettimeout()

    print(f"Default socket timeout: {default_timeout}")

    my_socket.settimeout(100)

    print(f"Current socket timeout: {my_socket.gettimeout()}")


test_socket_timeout()
