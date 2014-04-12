from amber.common import amber_client
from amber.dummy import dummy

__author__ = 'paoolo'

if __name__ == '__main__':
    client = amber_client.AmberClient('127.0.0.1')
    proxy = dummy.DummyProxy(client, 0)

    print(proxy.get_status())

    proxy.set_enable(True)
    proxy.set_message('Hello')

    print(proxy.get_status())