import random
import time

from amberclient.common import amber_client
from amberclient.roboclaw import roboclaw

__author__ = 'paoolo'

if __name__ == '__main__':
    ip = raw_input('IP (default: 127.0.0.1): ')
    ip = '127.0.0.1' if ip is None or len(ip) == 0 else ip

    client = amber_client.AmberClient(ip)
    proxy = roboclaw.RoboclawProxy(client, 0)

    for _ in range(100):
        proxy.send_motors_command(300 + int(random.random() * 20 - 10),
                                  300 + int(random.random() * 20 - 10),
                                  300 + int(random.random() * 20 - 10),
                                  300 + int(random.random() * 20 - 10))
        cms = proxy.get_current_motors_speed()
        print '%s, %s, %s, %s' % (str(cms.get_front_left_speed()), str(cms.get_front_right_speed()),
                                  str(cms.get_rear_left_speed()), str(cms.get_rear_right_speed()))
        time.sleep(0.5)

    proxy.terminate_proxy()
    client.terminate_client()