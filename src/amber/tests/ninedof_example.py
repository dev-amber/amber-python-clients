from amber.common import amber_client
from amber.ninedof import ninedof

__author__ = 'paoolo'

if __name__ == '__main__':
    client = amber_client.AmberClient('127.0.0.1')
    proxy = ninedof.NinedofProxy(client, 0)

    print(proxy.get_axes_data(True, True, True))
    # TODO: use listener

    client.terminate()