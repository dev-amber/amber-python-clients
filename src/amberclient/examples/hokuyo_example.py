import time

from amberclient.common import amber_client
from amberclient.common.listener import Listener
from amberclient.hokuyo import hokuyo


__author__ = 'paoolo'


class HokuyoListener(Listener):
    def handle(self, response):
        print str(response.get_points())


if __name__ == '__main__':
    ip = raw_input('IP (default: 127.0.0.1): ')
    ip = '127.0.0.1' if ip is None or len(ip) == 0 else ip
    client = amber_client.AmberClient(ip)
    proxy = hokuyo.HokuyoProxy(client, 0)

    for i in range(100):
        scan = proxy.get_single_scan()
        print(scan.get_points())

    proxy.subscribe(HokuyoListener())

    time.sleep(60)

    client.terminate()