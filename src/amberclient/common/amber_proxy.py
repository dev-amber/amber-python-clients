import logging
import logging.config
import threading
import abc

from ambercommon.common import runtime
import os

import drivermsg_pb2


__author__ = 'paoolo'

LOGGER_NAME = 'AmberClient'

pwd = os.path.dirname(os.path.abspath(__file__))
logging.config.fileConfig('%s/amber.ini' % pwd)


class AmberProxy(object):
    """
    Abstract class used to create proxies that connects to robot's devices.
    """

    def __init__(self, device_type, device_id, amber_client):
        """
        Generic proxy constructor. Must be invoked from subclasses.
        """
        self.device_type, self.device_id = device_type, device_id
        self.__amber_client = amber_client

        amber_client.register_proxy(self)

        self.__syn_num = 0
        self.__syn_num_lock = threading.Lock()

        self.__future_objs = {}
        self.__future_objs_lock = threading.Lock()

        self.__listeners = []
        self.__listeners_lock = threading.Lock()

        self.__logger = logging.getLogger(LOGGER_NAME)

        runtime.add_shutdown_hook(self.terminate_proxy)

    @abc.abstractmethod
    def handle_data_msg(self, header, message):
        pass

    def handle_ping_message(self, header, message):
        """
        Invoked to handle incoming ping message.
        """
        pass

    def handle_pong_message(self, header, message):
        """
        Invoked to handle incoming pong message.
        """
        pass

    def handle_driver_died_message(self, header, message):
        """
        Invoked to handle incoming "driver died" message.
        """
        pass

    def build_header(self):
        driver_hdr_builder = drivermsg_pb2.DriverHdr()

        driver_hdr_builder.deviceType = self.device_type
        driver_hdr_builder.deviceID = self.device_id

        return driver_hdr_builder

    def terminate_proxy(self):
        """
        Sends "amberclient died" message and terminates the proxy.
        """
        self.__logger.info("Terminating proxy.")

        driver_msg_builder = drivermsg_pb2.DriverMsg()
        driver_msg_builder.type = drivermsg_pb2.DriverMsg.CLIENT_DIED

        self.__amber_client.send_message(self.build_header(), driver_msg_builder)

    def get_next_syn_num(self):
        self.__syn_num_lock.acquire()
        try:
            self.__syn_num += 1
            return self.__syn_num
        finally:
            self.__syn_num_lock.release()

    def get_future_object(self, ack_num):
        obj = None
        self.__future_objs_lock.acquire()
        try:
            if ack_num in self.__future_objs:
                obj = self.__future_objs[ack_num]
                del self.__future_objs[ack_num]
        finally:
            self.__future_objs_lock.release()
        return obj

    def set_future_object(self, syn_num, value):
        self.__future_objs_lock.acquire()
        try:
            self.__future_objs[syn_num] = value
        finally:
            self.__future_objs_lock.release()

    def append_listener(self, listener):
        self.__listeners_lock.acquire()
        try:
            listeners_count = len(self.__listeners)
            self.__listeners.append(listener)
            return listeners_count
        finally:
            self.__listeners_lock.release()

    def remove_listener(self, listener=None):
        self.__listeners_lock.acquire()
        try:
            if listener is not None:
                self.__listeners.remove(listener)
            else:
                del self.__listeners[:]
            return len(self.__listeners)
        finally:
            self.__listeners_lock.release()

    def get_listeners(self):
        self.__listeners_lock.acquire()
        try:
            return self.__listeners[:]
        finally:
            self.__listeners_lock.release()