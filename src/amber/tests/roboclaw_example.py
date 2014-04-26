import time
from amber.common import amber_client
from amber.roboclaw import roboclaw

__author__ = 'paoolo'

if __name__ == '__main__':
    ip = raw_input('IP (default: 127.0.0.1): ')
    ip = '127.0.0.1' if ip is None or len(ip) == 0 else ip
    client = amber_client.AmberClient(ip)
    proxy = roboclaw.RoboclawProxy(client, 0)

    proxy.send_motors_command(100, 100, 100, 100)
    print(proxy.get_current_motors_speed())

    time.sleep(10)

    client.terminate()