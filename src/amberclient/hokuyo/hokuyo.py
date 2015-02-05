import logging
import logging.config

import os

from amberclient.common import amber_proxy, future_object
from amberclient.common import drivermsg_pb2
import hokuyo_pb2


__author__ = 'paoolo'

DEVICE_TYPE = 4

LOGGER_NAME = 'Hokuyo'

pwd = os.path.dirname(os.path.abspath(__file__))
logging.config.fileConfig('%s/hokuyo.ini' % pwd)


class HokuyoProxy(amber_proxy.AmberProxy):
    def __init__(self, amber_client, device_id):
        super(HokuyoProxy, self).__init__(DEVICE_TYPE, device_id, amber_client)
        self.__amber_client = amber_client
        self.__logger = logging.getLogger(LOGGER_NAME)
        self.__logger.info('Starting and registering HokuyoProxy.')

    def subscribe(self, listener):
        self.__logger.debug('Subscribe')
        listeners_count = self.append_listener(listener)
        if listeners_count == 0:
            driver_msg = HokuyoProxy.__build_subscribe_action_msg()
            self.__amber_client.send_message(self.build_header(), driver_msg)

    @staticmethod
    def __build_subscribe_action_msg():
        driver_msg = drivermsg_pb2.DriverMsg()
        driver_msg.type = drivermsg_pb2.DriverMsg.SUBSCRIBE
        return driver_msg

    def unsubscribe(self, listener=None):
        self.__logger.debug('Unsubscribe')
        listeners_length = self.remove_listener(listener)
        if listeners_length == 0:
            driver_msg = HokuyoProxy.__build_unsubscribe_action_msg()
            self.__amber_client.send_message(self.build_header(), driver_msg)

    @staticmethod
    def __build_unsubscribe_action_msg():
        driver_msg = drivermsg_pb2.DriverMsg()
        driver_msg.type = drivermsg_pb2.DriverMsg.UNSUBSCRIBE
        return driver_msg

    def handle_data_msg(self, header, message):
        self.__logger.debug('Handling data message')

        if not message.HasField('ackNum') or message.ackNum == 0:
            if message.HasExtension(hokuyo_pb2.scan):
                scan = Scan()
                HokuyoProxy.__fill_scan(scan, message)
                listeners = self.get_listeners()
                for listener in listeners:
                    listener.handle(scan)

        elif message.HasField('ackNum') and message.ackNum != 0:
            obj = self.get_future_object(message.ackNum)
            if isinstance(obj, Scan):
                HokuyoProxy.__fill_scan(obj, message)

    def get_single_scan(self):
        self.__logger.debug('Get single scan')
        syn_num = self.get_next_syn_num()
        driver_msg = HokuyoProxy.__build_get_single_scan_req_msg(syn_num)
        scan = Scan()
        self.set_future_object(syn_num, scan)
        self.__amber_client.send_message(self.build_header(), driver_msg)
        return scan

    @staticmethod
    def __build_get_single_scan_req_msg(syn_num):
        driver_msg = drivermsg_pb2.DriverMsg()
        driver_msg.type = drivermsg_pb2.DriverMsg.DATA
        driver_msg.Extensions[hokuyo_pb2.get_single_scan] = True
        driver_msg.synNum = syn_num
        return driver_msg

    def enable_scanning(self, enable_scanning=True):
        self.__logger.debug('Enable scanning, set to %s', str(enable_scanning))
        syn_num = self.get_next_syn_num()
        driver_msg = HokuyoProxy.__build_enable_scanning_req_msg(syn_num, enable_scanning)
        self.__amber_client.send_message(self.build_header(), driver_msg)

    @staticmethod
    def __build_enable_scanning_req_msg(syn_num, enable_scanning):
        driver_msg = drivermsg_pb2.DriverMsg()
        driver_msg.type = drivermsg_pb2.DriverMsg.DATA
        driver_msg.Extensions[hokuyo_pb2.enable_scanning] = enable_scanning
        driver_msg.synNum = syn_num
        return driver_msg

    @staticmethod
    def __fill_scan(scan, message):
        _scan = message.Extensions[hokuyo_pb2.scan]
        _timestamp = message.Extensions[hokuyo_pb2.timestamp]
        scan.set_values(_scan.angles, _scan.distances, _timestamp)
        scan.set_available()


class Scan(future_object.FutureObject):
    def __init__(self):
        super(Scan, self).__init__()
        self.__points, self.__timestamp = None, None

    def set_values(self, angles, distances, timestamp):
        self.__points = zip(angles, distances)
        self.__timestamp = timestamp

    def get_points(self):
        if not self.is_available():
            self.wait_available()
        return self.__points

    def get_timestamp(self):
        if not self.is_available():
            self.wait_available()
        return self.__timestamp