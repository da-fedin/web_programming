"""Printing the current time from the internet time-server"""
import ntplib
import time


def synchronize_time(server: str) -> None:
    """Get time from server."""
    try:
        # Create an NTP client
        client = ntplib.NTPClient()

        # Request time from the server
        response = client.request(server)

        # Update system time with the received time
        ts = response.tx_time
        time.time = lambda: ts

        print(f"Time synchronized with {server} successfully.")
        print(f"Current time: {time.ctime()}")

    except Exception as e:
        print(f"Error occurred: {e}")


server_name = "pool.ntp.org"

synchronize_time(server_name)
