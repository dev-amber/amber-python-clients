from amber.common import amber_client
from amber.hokuyo import hokuyo

__author__ = 'paoolo'

if __name__ == '__main__':
    client = amber_client.AmberClient('127.0.0.1')
    proxy = hokuyo.HokuyoProxy(client, 0)

    specs = proxy.get_sensor_specs()
    print specs.get_area_front()