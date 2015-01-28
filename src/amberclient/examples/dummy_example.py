import time

from amberclient.common import amber_client
from amberclient.common.listener import Listener
from amberclient.dummy import dummy


__author__ = 'paoolo'


class DummyListener(Listener):
    def handle(self, response):
        print str(response)


if __name__ == '__main__':
    ip = raw_input('IP (default: 127.0.0.1): ')
    ip = '127.0.0.1' if ip is None or len(ip) == 0 else ip

    client = amber_client.AmberClient(ip)
    proxy = dummy.DummyProxy(client, 0)

    status = proxy.get_status()
    status.wait_available()
    print(status)

    proxy.set_enable(True)
    proxy.set_message('Hello')

    status = proxy.get_status()
    status.wait_available()
    print(status)

    time.sleep(1)

    proxy.subscribe(DummyListener())

    time.sleep(1)

    proxy.unsubscribe()

    proxy.terminate_proxy()
    client.terminate_client()