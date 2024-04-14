import socket

data = 1234


def convert_integer(data_to_convert: int) -> None:
    """
    Convert from a network byte order to host byte order and vice versa.
    """
    # 32-bit order
    host_long_bite_order = socket.ntohl(data)
    network_long_bite_order = socket.htonl(data)

    # 16-bit order
    host_short_bite_order = socket.ntohs(data)
    network_short_bite_order = socket.htons(data)

    print(
        f"Original: {data} => Long host byte order: {host_long_bite_order},"
        f"Network byte order: {network_long_bite_order}"
    )
    print(
        f"Original: {data} => Short host byte order: {host_short_bite_order},"
        f"Network byte order: {network_short_bite_order}"
    )


convert_integer(data)
