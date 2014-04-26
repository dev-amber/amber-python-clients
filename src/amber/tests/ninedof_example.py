from amber.common import amber_client
from amber.ninedof import ninedof

__author__ = 'paoolo'

if __name__ == '__main__':
    ip = raw_input('IP (default: 127.0.0.1): ')
    ip = '127.0.0.1' if ip is None or len(ip) == 0 else ip
    client = amber_client.AmberClient(ip)
    proxy = ninedof.NinedofProxy(client, 0)

    print(proxy.get_axes_data(True, True, True))
    # TODO: use listener

    client.terminate()