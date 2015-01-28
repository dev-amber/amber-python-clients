import time

from amberclient.common import amber_client
from amberclient.common.listener import Listener
from amberclient.hokuyo import hokuyo


__author__ = 'paoolo'


class HokuyoListener(Listener):
    def handle(self, response):
        print '%f: %s, %s...' % (time.time(), str(scan.get_timestamp()), str(response.get_points())[:50])


if __name__ == '__main__':
    ip = raw_input('IP (default: 127.0.0.1): ')
    ip = '127.0.0.1' if ip is None or len(ip) == 0 else ip

    client = amber_client.AmberClient(ip)
    proxy = hokuyo.HokuyoProxy(client, 0)

    proxy.enable_scanning(True)

    time.sleep(10)

    for i in range(10):
        scan = proxy.get_single_scan()
        print '%f: %s, %s...' % (time.time(), str(scan.get_timestamp()), str(scan.get_points())[:50])

    proxy.subscribe(HokuyoListener())

    time.sleep(10)

    proxy.enable_scanning(False)

    proxy.terminate_proxy()
    client.terminate_client()