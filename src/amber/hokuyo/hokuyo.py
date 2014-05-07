import logging
import logging.config
import os

from amber.common import amber_proxy, future_object
from amber.common import drivermsg_pb2
import hokuyo_pb2


__author__ = 'paoolo'

DEVICE_TYPE = 4

LOGGER_NAME = 'HokuyoProxy'
pwd = os.path.dirname(os.path.abspath(__file__))
try:
    logging.config.fileConfig('%s/hokuyo.ini' % pwd)
except BaseException:
    print 'Logging not set.'


class HokuyoProxy(amber_proxy.AmberProxy):
    def __init__(self, amber_client, device_id):
        super(HokuyoProxy, self).__init__(DEVICE_TYPE, device_id, amber_client)
        self.__amber_client, self.__syn_num, self.__future_objs, self.__listeners = amber_client, 0, {}, []

        self.__logger = logging.getLogger(LOGGER_NAME)
        self.__logger.setLevel(logging.WARNING)

        self.__logger.info('Starting and registering HokuyoProxy.')

    def subscribe(self, listener):
        self.__logger.debug('Subscribe')

        listeners_count = len(self.__listeners)
        self.__listeners.append(listener)
        if listeners_count == 0:
            driver_msg = self.__build_subscribe_action_msg()
            self.__amber_client.send_message(self.build_header(), driver_msg)

    def __build_subscribe_action_msg(self):
        driver_msg = drivermsg_pb2.DriverMsg()
        driver_msg.type = drivermsg_pb2.DriverMsg.SUBSCRIBE
        return driver_msg

    def unsubscribe(self, listener=None):
        self.__logger.debug('Unsubscribe')

        if listener is not None:
            self.__listeners.remove(listener)
        if len(self.__listeners) == 0:
            driver_msg = self.__build_unsubscribe_action_msg()
            self.__amber_client.send_message(self.build_header(), driver_msg)

    def __build_unsubscribe_action_msg(self):
        driver_msg = drivermsg_pb2.DriverMsg()
        driver_msg.type = drivermsg_pb2.DriverMsg.UNSUBSCRIBE
        return driver_msg

    def handle_data_msg(self, header, message):
        self.__logger.debug('Handling data message')

        if not message.HasField('ackNum') or message.ackNum == 0:
            if message.HasExtension(hokuyo_pb2.scan):
                scan = Scan()
                self.__fill_scan(scan, message)
                scan.set_available()
                for listener in self.__listeners:
                    listener.handle(scan)

        elif message.HasField('ackNum') and message.ackNum != 0:
            ack_num = message.ackNum
            if ack_num in self.__future_objs:
                obj = self.__future_objs[ack_num]
                del self.__future_objs[ack_num]

                if isinstance(obj, Scan):
                    self.__fill_scan(obj, message)

    def __get_next_syn_num(self):
        self.__syn_num += 1
        return self.__syn_num

    def get_single_scan(self):
        self.__logger.debug('Get single scan')

        syn_num = self.__get_next_syn_num()

        driver_msg = self.__build_get_single_scan_req_msg(syn_num)

        scan = Scan()
        self.__future_objs[syn_num] = scan

        self.__amber_client.send_message(self.build_header(), driver_msg)

        return scan

    def __build_get_single_scan_req_msg(self, syn_num):
        driver_msg = drivermsg_pb2.DriverMsg()

        driver_msg.type = drivermsg_pb2.DriverMsg.DATA
        driver_msg.Extensions[hokuyo_pb2.get_single_scan] = True
        driver_msg.synNum = syn_num

        return driver_msg

    def __fill_scan(self, scan, message):
        _scan = message.Extensions[hokuyo_pb2.scan]

        scan.set_points(_scan.angles, _scan.distances)

        scan.set_available()


class Scan(future_object.FutureObject):
    def __init__(self):
        super(Scan, self).__init__()
        self.__points = None

    def set_points(self, angles, distances):
        self.__points = zip(angles, distances)

    def get_points(self):
        if not self.is_available():
            self.wait_available()
        return self.__points