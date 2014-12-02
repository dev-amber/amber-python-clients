import time

from amberclient.common import amber_client
from amberclient.common.listener import Listener
from amberclient.ninedof import ninedof


__author__ = 'paoolo'


class NinedofListener(Listener):
    def handle(self, response):
        print str(response)


if __name__ == '__main__':
    ip = raw_input('IP (default: 127.0.0.1): ')
    ip = '127.0.0.1' if ip is None or len(ip) == 0 else ip
    client = amber_client.AmberClient(ip)
    proxy = ninedof.NinedofProxy(client, 0)

    print(proxy.get_axes_data(True, True, True))
    proxy.register_ninedof_data_listener(1, True, True, True, NinedofListener())

    time.sleep(10)

    client.terminate()