from amber.common import amber_client
from amber.hokuyo import hokuyo

__author__ = 'paoolo'

if __name__ == '__main__':
    ip = raw_input('IP (default: 127.0.0.1): ')
    ip = '127.0.0.1' if ip is None or len(ip) == 0 else ip
    client = amber_client.AmberClient(ip)
    proxy = hokuyo.HokuyoProxy(client, 0)

    print(proxy.get_version_info())
    print(proxy.get_sensor_state())
    print(proxy.get_sensor_specs())
    scan = proxy.get_single_scan()
    print(scan.get_points())

    client.terminate()