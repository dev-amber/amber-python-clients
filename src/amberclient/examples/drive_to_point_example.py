from amberclient.common import amber_client
from amberclient.drive_to_point import drive_to_point

__author__ = 'paoolo'

if __name__ == '__main__':
    ip = raw_input('IP (default: 127.0.0.1): ')
    ip = '127.0.0.1' if ip is None or len(ip) == 0 else ip
    client = amber_client.AmberClient(ip)
    proxy = drive_to_point.DriveToPointProxy(client, 0)

    targets = [drive_to_point.Point(500.0, 500.0, 10.0),
               drive_to_point.Point(1000.0, 0.0, 10.0)]
    proxy.set_targets(targets)

    result = proxy.get_next_target()
    next_target = result.get_result()
    print next_target

    result = proxy.get_next_targets()
    next_targets = result.get_result()
    print next_targets

    result = proxy.get_visited_target()
    visited_target = result.get_result()
    print visited_target

    result = proxy.get_visited_targets()
    visited_targets = result.get_result()
    print visited_targets