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
logging.config.fileConfig('%s/dummy.ini' % pwd)


class DummyProxy(amber_proxy.AmberProxy):
    def __init__(self, amber_client, device_id):
        super(DummyProxy, self).__init__(DEVICE_TYPE, device_id, amber_client)
        self.__amber_client = amber_client
        self.__logger = logging.getLogger(LOGGER_NAME)
        self.__logger.info('Starting and registering DummyProxy.')

    def subscribe(self, listener):
        """
        Subscribe for data provided by remote object.

        :param listener:
        :return:
        """
        self.__logger.debug('Subscribe')
        listeners_count = self.append_listener(listener)
        if listeners_count == 0:
            driver_msg = DummyProxy.__build_subscribe_action_msg()
            self.__amber_client.send_message(self.build_header(), driver_msg)

    @staticmethod
    def __build_subscribe_action_msg():
        driver_msg = drivermsg_pb2.DriverMsg()
        driver_msg.type = drivermsg_pb2.DriverMsg.SUBSCRIBE
        return driver_msg

    def unsubscribe(self, listener=None):
        """
        Disable subscription.

        :return:
        """
        self.__logger.debug('Unsubscribe')
        listeners_length = self.remove_listener(listener)
        if listeners_length == 0:
            driver_msg = DummyProxy.__build_unsubscribe_action_msg()
            self.__amber_client.send_message(self.build_header(), driver_msg)

    @staticmethod
    def __build_unsubscribe_action_msg():
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
                listeners = self.get_listeners()
                for listener in listeners:
                    listener.handle(response)

        elif message.HasField('ackNum') and message.ackNum != 0:
            obj = self.get_future_object(message.ackNum)
            if isinstance(obj, Status):
                DummyProxy.__fill_status(obj, message)

    def set_enable(self, value):
        """
        Generate and send message which set enable flag on remote object.

        :param value:
        :return:
        """
        self.__logger.debug('Set enable to %s', value)
        driver_msg = DummyProxy.__build_set_enable_req_msg(value)
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
        self.__logger.debug('Set message to %s', message)
        driver_msg = DummyProxy.__build_set_message_req_msg(message)
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
        syn_num = self.get_next_syn_num()
        driver_msg = DummyProxy.__build_get_status_req_msg(syn_num)
        status = Status()
        self.set_future_object(syn_num, status)
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

    def get_message(self):
        if not self.is_available():
            self.wait_available()
        return self.__message

    def set_message(self, message):
        self.__message = message

    def get_enable(self):
        if not self.is_available():
            self.wait_available()
        return self.__enable

    def set_enable(self, enable):
        self.__enable = enable