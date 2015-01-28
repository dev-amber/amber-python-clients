import logging
import logging.config

import abc
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

        self.__logger = logging.getLogger(LOGGER_NAME)

        amber_client.register_proxy(device_type, device_id, self)

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