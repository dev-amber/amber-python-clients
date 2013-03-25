import abc

import drivermsg_pb2


__author__ = 'paoolo'

RECEIVING_BUFFER_SIZE = 4096
DEFAULT_PORT = 26233


class AmberProxy(object):
    """
    Abstract class used to create proxies that connects to robot's devices.
    """

    def __init__(self, device_type, device_id, amber_client, logger):
        """
        Generic proxy constructor. Must be invoked from subclasses.
        """
        self.__device_type, self.__device_id = device_type, device_id
        self.__amber_client, self.__logger = amber_client, logger

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
        driver_hdr_builder = drivermsg_pb2.DriverMsg()
        driver_hdr_builder.deviceType = self.__device_type
        driver_hdr_builder.deviceID = self.__device_id
        return driver_hdr_builder

    def terminate_proxy(self):
        """
        Sends "client died" message and terminates the proxy.
        """
        print "Terminating proxy."

        driver_msg_builder = drivermsg_pb2.DriverMsg
        driver_msg_builder.type = drivermsg_pb2.DriverMsg.MsgType.CLIENT_DIED

        self.__amber_client.send_message(self.build_header(), driver_msg_builder)