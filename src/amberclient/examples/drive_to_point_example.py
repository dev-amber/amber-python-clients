import time

from amberclient.common import amber_client
from amberclient.drive_to_point import drive_to_point


__author__ = 'paoolo'

if __name__ == '__main__':
    ip = raw_input('IP (default: 127.0.0.1): ')
    ip = '127.0.0.1' if ip is None or len(ip) == 0 else ip
    client = amber_client.AmberClient(ip)
    proxy = drive_to_point.DriveToPointProxy(client, 0)

    targets = [drive_to_point.Point(2447.25, 4221.25, 100.0),
               drive_to_point.Point(1467.06, 4142.85, 100.0),
               drive_to_point.Point(673.888, 3769.64, 100.0),
               drive_to_point.Point(473.391, 2967.81, 100.0)]
    proxy.set_targets(targets)

    while True:
        result_next_targets = proxy.get_next_targets()
        result_visited_targets = proxy.get_visited_targets()
        next_targets = result_next_targets.get_result()
        visited_targets = result_visited_targets.get_result()
        print "next targets: %s, visited targets: %s" % (next_targets, visited_targets)
        time.sleep(1)