import logging
import logging.config

import os

from amberclient.common import amber_proxy, future_object
from amberclient.common import drivermsg_pb2
import dummy_pb2


__author__ = 'paoolo'

DEVICE_TYPE = 5

LOGGER_NAME = 'DummyProxy'
pwd = os.path.dirname(os.path.abspath(__file__))
try:
    logging.config.fileConfig('%s/dummy.ini' % pwd)
except BaseException:
    print 'Logging not set.'


class DummyProxy(amber_proxy.AmberProxy):
    def __init__(self, amber_client, device_id):
        super(DummyProxy, self).__init__(DEVICE_TYPE, device_id, amber_client)
        self.__amber_client, self.__syn_num, self.__future_objs, self.__listener = amber_client, 0, {}, None

        self.__logger = logging.getLogger(LOGGER_NAME)
        self.__logger.setLevel(logging.WARNING)

        self.__logger.info('Starting and registering DummyProxy.')

    def subscribe(self, listener):
        """
        Subscribe for data provided by remote object.

        :param listener:
        :return:
        """
        self.__listener = listener

        driver_msg = self.__build_subscribe_action()
        self.__amber_client.send_message(self.build_header(), driver_msg)

    @staticmethod
    def __build_subscribe_action():
        driver_msg = drivermsg_pb2.DriverMsg()

        driver_msg.type = drivermsg_pb2.DriverMsg.SUBSCRIBE

        return driver_msg

    def unsubscribe(self):
        """
        Disable subscription.

        :return:
        """
        driver_msg = self.__build_unsubscribe_action()
        self.__amber_client.send_message(self.build_header(), driver_msg)

    @staticmethod
    def __build_unsubscribe_action():
        driver_msg = drivermsg_pb2.DriverMsg()

        driver_msg.type = drivermsg_pb2.DriverMsg.UNSUBSCRIBE

        return driver_msg

    def handle_data_msg(self, header, message):
        """
        Handle DATA message type. Must be implemented.
        It services responses for requested operation and subscribed data.

        :param header:
        :param message:
        :return:
        """
        self.__logger.debug('Handling data message')

        if not message.HasField('ackNum') or message.ackNum == 0:
            if message.HasExtension(dummy_pb2.message):
                response = message.Extensions[dummy_pb2.message]
                if self.__listener is not None:
                    self.__listener.handle(response)

        if message.HasField('ackNum') and message.ackNum != 0:
            ack_num = message.ackNum
            if ack_num in self.__future_objs:
                obj = self.__future_objs[ack_num]
                del self.__future_objs[ack_num]

                if isinstance(obj, Status):
                    self.__fill_status(obj, message)

    def __get_next_syn_num(self):
        self.__syn_num += 1
        return self.__syn_num

    def set_enable(self, value):
        """
        Generate and send message which set enable flag on remote object.

        :param value:
        :return:
        """
        self.__logger.debug('Set enable to %s' % value)

        driver_msg = self.__build_set_enable_req_msg(value)
        self.__amber_client.send_message(self.build_header(), driver_msg)

    @staticmethod
    def __build_set_enable_req_msg(value):
        driver_msg = drivermsg_pb2.DriverMsg()

        driver_msg.type = drivermsg_pb2.DriverMsg.DATA
        driver_msg.Extensions[dummy_pb2.enable] = value

        return driver_msg

    def set_message(self, message):
        """
        Generate and send message which set message on remote object.

        :param message:
        :return:
        """
        self.__logger.debug('Set message to %s' % message)

        driver_msg = self.__build_set_message_req_msg(message)
        self.__amber_client.send_message(self.build_header(), driver_msg)

    @staticmethod
    def __build_set_message_req_msg(message):
        driver_msg = drivermsg_pb2.DriverMsg()

        driver_msg.type = drivermsg_pb2.DriverMsg.DATA
        driver_msg.Extensions[dummy_pb2.message] = message

        return driver_msg

    def get_status(self):
        """
        Generate and send message which request to get enable flag and message value.
        Return a future object bound with send request.
        Response will be serviced in handle_data_msg.

        :return:
        """
        self.__logger.debug('Get status')

        syn_num = self.__get_next_syn_num()

        driver_msg = self.__build_get_status_req_msg(syn_num)

        status = Status()
        self.__future_objs[syn_num] = status

        self.__amber_client.send_message(self.build_header(), driver_msg)

        return status

    @staticmethod
    def __build_get_status_req_msg(syn_num):
        driver_msg = drivermsg_pb2.DriverMsg()

        driver_msg.type = drivermsg_pb2.DriverMsg.DATA
        driver_msg.Extensions[dummy_pb2.get_status] = True
        driver_msg.synNum = syn_num

        return driver_msg

    @staticmethod
    def __fill_status(status, message):
        status.set_enable(message.Extensions[dummy_pb2.enable])
        status.set_message(message.Extensions[dummy_pb2.message])
        status.set_available()


class Status(future_object.FutureObject):
    def __init__(self):
        super(Status, self).__init__()
        self.__message, self.__enable = None, None

    def __str__(self):
        return "message: %s, enable: %s" % (self.__message, str(self.__enable))

    def set_message(self, message):
        self.__message = message

    def set_enable(self, enable):
        self.__enable = enable