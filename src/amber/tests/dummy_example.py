import time

from amber.common import amber_client
from amber.common.listener import Listener
from amber.dummy import dummy


__author__ = 'paoolo'


class DummyListener(Listener):
    def handle(self, response):
        print str(response)


if __name__ == '__main__':
    ip = raw_input('IP (default: 127.0.0.1): ')
    ip = '127.0.0.1' if ip is None or len(ip) == 0 else ip
    client = amber_client.AmberClient(ip)
    proxy = dummy.DummyProxy(client, 0)

    proxy.subscribe(DummyListener())

    print(proxy.get_status())

    proxy.set_enable(True)
    proxy.set_message('Hello')

    print(proxy.get_status())

    time.sleep(30)

    proxy.unsubscribe()

    time.sleep(3)

    client.terminate()