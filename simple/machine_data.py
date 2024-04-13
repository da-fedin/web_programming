import socket


def print_machine_info() -> None:
    """
    Retrieve a local machine's hostname and IP address
    """
    host_name = socket.gethostname()
    ip_address = socket.gethostbyname(host_name)

    print(f"Host name: {host_name}")
    print(f"IP address: {ip_address}")


print_machine_info()
