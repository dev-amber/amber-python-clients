import time

from amberclient.common import amber_client
from amberclient.drive_to_point import drive_to_point


__author__ = 'paoolo'

if __name__ == '__main__':
    ip = raw_input('IP (default: 127.0.0.1): ')
    ip = '127.0.0.1' if ip is None or len(ip) == 0 else ip
    client = amber_client.AmberClient(ip)
    proxy = drive_to_point.DriveToPointProxy(client, 0)

    targets = [drive_to_point.Point(2.44725, 4.22125, 0.25),
               drive_to_point.Point(1.46706, 4.14285, 0.25),
               drive_to_point.Point(0.67388, 3.76964, 0.25),
               drive_to_point.Point(0.47339, 2.96781, 0.25)]
    proxy.set_targets(targets)

    alive = True
    while alive:
        result_next_targets = proxy.get_next_targets()
        result_visited_targets = proxy.get_visited_targets()
        next_targets = result_next_targets.get_result()
        visited_targets = result_visited_targets.get_result()
        print "next targets: %s, visited targets: %s" % (next_targets, visited_targets)
        time.sleep(1)
        alive = len(next_targets) > 0

    client.terminate()