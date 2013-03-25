import amber_client
import hokuyo

__author__ = 'paoolo'

if __name__ == '__main__':
    client = amber_client.AmberClient('127.0.0.1')
    proxy = hokuyo.HokuyoProxy(client, 0)