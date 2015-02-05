import logging
import logging.config

import os

from amberclient.common import amber_proxy, future_object
from amberclient.common import drivermsg_pb2
import location_pb2


__author__ = 'paoolo'

DEVICE_TYPE = 6

LOGGER_NAME = 'Location'

pwd = os.path.dirname(os.path.abspath(__file__))
logging.config.fileConfig('%s/location.ini' % pwd)


class LocationProxy(amber_proxy.AmberProxy):
    def __init__(self, amber_client, device_id):
        super(LocationProxy, self).__init__(DEVICE_TYPE, device_id, amber_client)
        self.__amber_client = amber_client
        self.__logger = logging.getLogger(LOGGER_NAME)
        self.__logger.info('Starting and registering LocationProxy.')

    def handle_data_msg(self, header, message):
        self.__logger.debug('Handling data message')
        if message.HasField('ackNum') and message.ackNum != 0:
            obj = self.get_future_object(message.ackNum)
            if isinstance(obj, Location):
                LocationProxy.__fill_location(obj, message)

    def get_location(self):
        self.__logger.debug('Get location')
        syn_num = self.get_next_syn_num()
        driver_msg = LocationProxy.__build_get_location_req_msg(syn_num)
        location = Location()
        self.set_future_object(syn_num, location)
        self.__amber_client.send_message(self.build_header(), driver_msg)
        return location

    @staticmethod
    def __build_get_location_req_msg(syn_num):
        driver_msg = drivermsg_pb2.DriverMsg()
        driver_msg.type = drivermsg_pb2.DriverMsg.DATA
        driver_msg.Extensions[location_pb2.get_location] = True
        driver_msg.synNum = syn_num
        return driver_msg

    @staticmethod
    def __fill_location(location, message):
        current_location = message.Extensions[location_pb2.currentLocation]
        x = current_location.x
        y = current_location.y
        p = current_location.p
        alfa = current_location.alfa
        timestamp = current_location.timeStamp
        location.set_location(x, y, p, alfa, timestamp)
        location.set_available()


class Location(future_object.FutureObject):
    def __init__(self):
        super(Location, self).__init__()
        self.__x, self.__y, self.__p, self.__alfa, self.__timestamp = None, None, None, None, None

    def set_location(self, x, y, p, alfa, timestamp):
        self.__x, self.__y, self.__p, self.__alfa, self.__timestamp = x, y, p, alfa, timestamp

    def get_location(self):
        if not self.is_available():
            self.wait_available()
        return self.__x, self.__y, self.__p, self.__alfa, self.__timestamp