"""
Module containing network-related functions for Statz
"""
import speedtest
import socket


def internet_speed_test(roundResult=True):
    """
    Run an internet speed test using the speedtest-cli library.\n

    Args:
     roundResult: whether or not to round the result. defaults to True.
    
    ## Returns
     **download_speed**\n the download speed in mbps

     **upload_speed**\n the upload speed in mbps

     **ping**\n the ping in ms
    """
    # set up the speedtest and get the best server and stuff
    st = speedtest.Speedtest(secure=True)

    st.get_best_server()

    # run the tests
    download_speed = st.download() / 1_000_000
    upload_speed = st.upload() / 1_000_000

    ping = st.results.ping

    # return the results
    if roundResult:
        return round(download_speed, 2), round(upload_speed, 2), round(ping, 1)
    else:
        return download_speed, upload_speed, ping

def scan_open_ports(starting=1, ending=1024, targetIP="127.0.0.1"):
    """
    Scan to find all open ports on the targetIP.
    Args:
     starting (int): Port to start scanning at. (default is 1)
     ending (int): Port to stop scanning at. (default is 1024)
     targetIP (str): The target IP to scan. (default is 127.0.0.1)
    Returns:
     open_ports (list): A list of all open ports found in the range on the target IP.
    """

    open_ports = []
    for port in (starting, ending):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)

        result = sock.connect_ex((targetIP, port))

        if result == 0:
            open_ports.append(port)
        
        sock.close()

    return open_ports


if __name__ == "__main__":
    # print("internet speed test")
    # print("=" * 50)

    # print("not rounded")
    # print(internet_speed_test(False))
    # print("rounded")
    # print(internet_speed_test(True))

    # print("")

    print("port scanner")
    print("=" * 50)

    print("scanning open ports between 1 and 1024 on 127.0.0.1")
    print(scan_open_ports())