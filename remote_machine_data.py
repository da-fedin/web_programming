import socket

remote_host = 'www.python.org'
# remote_host = 'SEGmbu'


def get_remote_machine_info(host: str) -> None:
    """
    Retrieve a remote machine's hostname and IP address
    """
    try:
        print(f"IP address of {remote_host}: {socket.gethostbyname(remote_host)}")

    except socket.error as e:
        print(f"Error: {e}")


get_remote_machine_info(remote_host)
