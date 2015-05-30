import time

from amberclient.common import amber_client
from amberclient.location import location


__author__ = 'paoolo'

if __name__ == '__main__':
    ip = raw_input('IP (default: 192.168.2.210): ')
    ip = '192.168.2.210' if ip is None or len(ip) == 0 else ip

    client = amber_client.AmberClient(ip)
    proxy = location.LocationProxy(client, 0)

    while True:
        _location = proxy.get_location()
        print _location.get_location()
        time.sleep(0.2)

    proxy.terminate_proxy()
    client.terminate_client()