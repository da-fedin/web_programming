import socket
import struct
import time


def sntp_client(ntp_server: str, stp_port: int) -> None:
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    data = "\x1b" + 47 * "\0"

    client.sendto(data.encode("utf-8"), (ntp_server, stp_port))

    data, address = client.recvfrom(1024)

    if data:
        print("Response received from:", address)

    t = struct.unpack("!12I", data)[10]

    t -= TIME1970

    print(f"\tTime={time.ctime(t)}")


NTP_SERVER = "0.uk.pool.ntp.org"
TIME1970 = 2208988800

sntp_client(NTP_SERVER, 123)
