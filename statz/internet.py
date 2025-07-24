"""
Internet speed testing module
Tests ping and upload/download speed
"""
import speedtest


def internet_speed_test(round=True):
    """
    Run an internet speed test using the speedtest-cli library.\n

    Args:
     round: whether or not to round the result. defaults to True.
    
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
    if round:
        return round(download_speed, 2), round(upload_speed, 2), round(ping, 1)
    else:
        return download_speed, upload_speed, ping

if __name__ == "__main__":
    print("not rounded")
    print(internet_speed_test(False))
    print("rounded")
    print(internet_speed_test(True))