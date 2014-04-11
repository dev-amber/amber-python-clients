from amber.common import amber_client
from amber.roboclaw import roboclaw

__author__ = 'paoolo'

if __name__ == '__main__':
    client = amber_client.AmberClient('127.0.0.1')
    proxy = roboclaw.RoboclawProxy(client, 0)

    proxy.send_motors_command(100, 100, 100, 100)
    speeds = proxy.get_current_motors_speed()
    print speeds.get_front_left_speed()