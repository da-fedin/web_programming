import socket


def find_service_name():
    protocol_name = "tcp"

    for port in [80, 25]:
        service_name = socket.getservbyport(port, protocol_name)

        print(f"Port: {port} => service name: {service_name}")
        print(f"Port: {53} => service name: {socket.getservbyport(53, 'udp')}")


find_service_name()
