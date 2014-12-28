import logging
import logging.config
import socket
import struct
import threading
import traceback
import select

import os

from amberclient.common import runtime
import drivermsg_pb2


__author__ = 'paoolo'

LOGGER_NAME = 'AmberClient'
pwd = os.path.dirname(os.path.abspath(__file__))
try:
    logging.config.fileConfig('%s/amber.ini' % pwd)
except BaseException:
    print 'Logging not set.'

RECEIVING_BUFFER_SIZE = 16384
DEFAULT_PORT = 26233


class AmberClient(object):
    """
    Class used to communicate with robot.
    """

    def __init__(self, hostname, port=DEFAULT_PORT, name=None):
        """
        Instantiates AmberClient object.
        """
        self.__logger = logging.Logger(LOGGER_NAME)

        self.__terminated, self.__proxy_map = False, {}
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__hostname, self.__port = hostname, port

        self.__alive = True
        self.__receiving_thread = threading.Thread(target=self.message_receiving_loop,
                                                   name="receiving-thread-%s" % str(name))
        self.__receiving_thread.start()

        runtime.add_shutdown_hook(self.terminate)

    def register_client(self, device_type, device_id, proxy):
        """
        Registers AmberProxy in amberclient.
        """
        self.__proxy_map[(device_type, device_id)] = proxy

    @staticmethod
    def __serialize_data(data):
        data = data.SerializeToString()
        data = struct.pack('!h', len(data)) + data
        return data

    def send_message(self, header, message):
        """
        Sends message to the robot.
        """
        self.__logger.debug("Sending message for (%d: %d):\nheader=%s.\nmessage=%s." %
                            (header.deviceType, header.deviceID, str(header), str(message)))

        data_header = AmberClient.__serialize_data(header)
        data_message = AmberClient.__serialize_data(message)

        stream = data_header + data_message
        self.__socket.sendto(stream, (self.__hostname, self.__port))

    def terminate(self, *args, **kwargs):
        """
        Terminates amberclient.
        """
        if not self.__terminated:
            self.__logger.info("Terminate amberclient.")

            self.__terminated = True
            self.terminate_proxies()

            self.__alive = False
            try:
                self.__socket.shutdown(socket.SHUT_RDWR)
            except socket.error:
                # .. silent pass ..
                pass
            self.__socket.close()

    def terminate_proxies(self):
        """
        Terminates all registered proxies.
        """
        for proxy in self.__proxy_map.itervalues():
            proxy.terminate_proxy()

    @staticmethod
    def __deserialize_data(packet):
        # TODO: make it better

        header = drivermsg_pb2.DriverHdr()
        message = drivermsg_pb2.DriverMsg()

        header_len = struct.unpack('!h', packet[:2])[0]
        header_start = 2

        message_offset = header_len + 2
        message_len = struct.unpack('!h', packet[message_offset:message_offset + 2])[0]
        message_start = message_offset + 2

        header.ParseFromString(packet[header_start:header_len + header_start])
        message.ParseFromString(packet[message_start:message_len + message_start])

        return header, message

    def message_receiving_loop(self):
        # noinspection PyBroadException
        while self.__alive:
            try:
                self.__logger.debug('Waiting for message from mediator.')
                r, _, _ = select.select([self.__socket], [], [])
                if r:
                    packet, _ = self.__socket.recvfrom(RECEIVING_BUFFER_SIZE)
                    header, message = AmberClient.__deserialize_data(packet)

                    if not header.HasField('deviceType') \
                            or not header.HasField('deviceID') \
                            or header.HasField('deviceType') == 0:
                        self.__handle_message_from_mediator(header, message)

                    else:
                        key = (header.deviceType, header.deviceID)
                        client_proxy = self.__proxy_map[key] if key in self.__proxy_map else None
                        if client_proxy is not None:
                            self.__handle_message_from_driver(header, message, client_proxy)
                        else:
                            self.__logger.warn('Cannot find amberclient proxy for device type %d and device ID %d' %
                                               (header.deviceType, header.deviceID))

            except Exception as e:
                traceback.print_exc()
                self.__logger.warn('Unknown error: %s' % str(e))

    def __handle_message_from_mediator(self, header, message):
        msg_type = message.type
        if msg_type == drivermsg_pb2.DriverMsg.DATA:
            self.__logger.warning('DATA message came, but device details not set, ignoring.')

        elif msg_type == drivermsg_pb2.DriverMsg.PING:
            self.__logger.debug('PING message came, handling.')
            self.__handle_ping_message(header, message)

        elif msg_type == drivermsg_pb2.DriverMsg.PONG:
            self.__logger.debug('PONG message came, handling.')
            self.__handle_pong_message(header, message)

        elif msg_type == drivermsg_pb2.DriverMsg.DRIVER_DIED:
            self.__logger.warning('DRIVER_DIED message came, but device details not set, ignoring.')

        else:
            self.__logger.warn('Unexpected message came: %s, ignoring.' % str(msg_type))

    def __handle_message_from_driver(self, header, message, client_proxy):
        msg_type = message.type
        if msg_type == drivermsg_pb2.DriverMsg.DATA:
            self.__logger.debug('DATA message came for device type %d and device ID %d' %
                                (client_proxy.deviceType, client_proxy.deviceID))
            client_proxy.handle_data_msg(header, message)

        elif msg_type == drivermsg_pb2.DriverMsg.PING:
            self.__logger.debug('PING message came for device type %d and device ID %d' %
                                (client_proxy.deviceType, client_proxy.deviceID))
            client_proxy.handle_ping_message(header, message)

        elif msg_type == drivermsg_pb2.DriverMsg.PONG:
            self.__logger.debug('PONG message came for device type %d and device ID %d' %
                                (client_proxy.deviceType, client_proxy.deviceID))
            client_proxy.handle_pong_message(header, message)

        elif msg_type == drivermsg_pb2.DriverMsg.DRIVER_DIED:
            self.__logger.info('DRIVER_DIED message came for device type %d and device ID %d' %
                               (client_proxy.deviceType, client_proxy.deviceID))
            client_proxy.handle_driver_died_message(header, message)

        else:
            self.__logger.warning('Unexpected message came %s for (%d: %d), ignoring.' %
                                  (str(msg_type), client_proxy.deviceType, client_proxy.deviceID))

    def __handle_ping_message(self, header, message):
        self.__logger.info('Handle PING message from (%s: %s), nothing to do.' %
                           (str(header.deviceType), str(header.deviceID)))

    def __handle_pong_message(self, header, message):
        self.__logger.info('Handle PONG message from (%s: %s), nothing to do.' %
                           (str(header.deviceType), str(header.deviceID)))