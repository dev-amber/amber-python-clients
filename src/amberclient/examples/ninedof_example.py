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

    sensor_data = proxy.get_sensor_data(accel=True, gyro=True, magnet=True)
    print sensor_data.get_accel(), sensor_data.get_gyro(), sensor_data.get_magnet()
    proxy.subscribe(NinedofListener(), accel=True, gyro=True, magnet=True, freq=100)

    time.sleep(10)

    proxy.terminate_proxy()
    client.terminate_client()