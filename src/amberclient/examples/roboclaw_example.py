import time

from amberclient.common import amber_client
from amberclient.roboclaw import roboclaw

__author__ = 'paoolo'

if __name__ == '__main__':
    ip = raw_input('IP (default: 127.0.0.1): ')
    ip = '127.0.0.1' if ip is None or len(ip) == 0 else ip

    client = amber_client.AmberClient(ip)
    proxy = roboclaw.RoboclawProxy(client, 0)

    for p in range(50):
        proxy.send_motors_command(100, 100, 100, 100)
        cms = proxy.get_current_motors_speed()
        print cms.get_front_left_speed(), cms.get_front_right_speed(), cms.get_rear_left_speed(), cms.get_rear_right_speed()
        time.sleep(0.1)

    proxy.terminate_proxy()
    client.terminate_client()