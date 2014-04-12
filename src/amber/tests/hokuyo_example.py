from amber.common import amber_client
from amber.hokuyo import hokuyo

__author__ = 'paoolo'

if __name__ == '__main__':
    client = amber_client.AmberClient('127.0.0.1')
    proxy = hokuyo.HokuyoProxy(client, 0)

    proxy.laser_on()
    proxy.laser_off()
    proxy.reset()
    proxy.set_motor_speed(99)
    proxy.set_high_sensitive(True)
    print(proxy.get_version_info())
    print(proxy.get_sensor_state())
    print(proxy.get_sensor_specs())
    # print(proxy.get_single_scan())