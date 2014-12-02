from amberclient.common import amber_client
from amberclient.location import location

__author__ = 'paoolo'

if __name__ == '__main__':
    ip = raw_input('IP (default: 127.0.0.1): ')
    ip = '127.0.0.1' if ip is None or len(ip) == 0 else ip
    client = amber_client.AmberClient(ip)
    proxy = location.LocationProxy(client, 0)

    _location = proxy.get_location()
    print _location.get_location()