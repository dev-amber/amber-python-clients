import time
import sys

from amberclient.common import amber_client
from amberclient.drive_to_point import drive_to_point

__author__ = 'paoolo'


def get_path(file_name):
    targets = []
    file_handler = open(file_name)
    for line in file_handler:
        values = line.split(';')
        x, y, r = map(lambda v: float(v), values)
        targets.append(drive_to_point.Point(x, y, r))
    return targets


if __name__ == '__main__':
    ip = raw_input('IP (default: 192.168.2.210): ')
    ip = '192.168.2.210' if ip is None or len(ip) == 0 else ip

    if len(sys.argv) <= 1:
        print 'Usage: cmd <path_to_file_with_track>'
        exit()

    client = amber_client.AmberClient(ip)
    proxy = drive_to_point.DriveToPointProxy(client, 0)

    targets = get_path(sys.argv[1])
    print 'set path: %s' % str(targets)

    proxy.set_targets(targets)

    alive = True
    while alive:
        result_next_targets = proxy.get_next_targets()
        result_visited_targets = proxy.get_visited_targets()
        next_targets = result_next_targets.get_result()
        visited_targets = result_visited_targets.get_result()
        print 'next targets: %s, visited targets: %s' % (next_targets, visited_targets)
        time.sleep(1)
        alive = next_targets is not None and len(next_targets) > 0

    proxy.terminate_proxy()
    client.terminate_client()
