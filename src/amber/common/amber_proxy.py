import abc
import logging

import drivermsg_pb2


__author__ = 'paoolo'

LOGGER_NAME = 'Amber.Proxy'


class AmberProxy(object):
    """
    Abstract class used to create proxies that connects to robot's devices.
    """

    def __init__(self, device_type, device_id, amber_client):
        """
        Generic proxy constructor. Must be invoked from subclasses.
        """
        self.deviceType, self.deviceID = device_type, device_id
        self.__amber_client = amber_client

        self.__logger = logging.Logger(LOGGER_NAME)
        self.__logger.addHandler(logging.StreamHandler())

        amber_client.register_client(device_type, device_id, self)

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

        driver_hdr_builder.deviceType = self.deviceType
        driver_hdr_builder.deviceID = self.deviceID

        return driver_hdr_builder

    def terminate_proxy(self):
        """
        Sends "client died" message and terminates the proxy.
        """
        self.__logger.info("Terminating proxy.")

        driver_msg_builder = drivermsg_pb2.DriverMsg()
        driver_msg_builder.type = drivermsg_pb2.DriverMsg.CLIENT_DIED

        self.__amber_client.send_message(self.build_header(), driver_msg_builder)