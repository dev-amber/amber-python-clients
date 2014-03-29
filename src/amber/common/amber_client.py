import socket
import thread

import bitstring

import drivermsg_pb2


__author__ = 'paoolo'

RECEIVING_BUFFER_SIZE = 4096
DEFAULT_PORT = 26233


class AmberClient(object):
    """
    Class used to communicate with robot.
    """

    def __init__(self, hostname, port=DEFAULT_PORT):
        """
        Instantiates AmberClient object.
        """
        self.__terminated, self.__proxy_map = False, {}
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__hostname, self.__port = hostname, port

        self.__receiving_thread = thread.start_new_thread(self.message_receiving_loop, ())
        # runtime.add_shutdown_hook(self.terminate)

    def register_client(self, device_type, device_id, proxy):
        """
        Registers AmberProxy in client.
        """
        self.__proxy_map[(device_type, device_id)] = proxy

    def send_message(self, header, message):
        """
        Sends message to the robot.
        """
        stream = bitstring.BitStream()

        length = header.getSerializedSize()
        stream.append("int:16=%d" % length)
        stream.append(header.toByteArray())

        length = message.getSerializedSize()
        stream.append("int:16=%d" % length)
        stream.append(message.toByteArray())

        print "Sending an UDP packet for (%d: %d)." % \
              (header.getDeviceType(), header.getDeviceID())

        self.__socket.send(stream.bytes)

    def terminate(self):
        """
        Terminates client.
        """
        if not self.__terminated:
            self.__terminated = True
            print "Terminating"
            self.terminate_proxies()
            self.__socket.close()
            # self.__receiving_thread.interrupt()

    def terminate_proxies(self):
        """
        Terminates all registered proxies.
        """
        for proxy in self.__proxy_map.items():
            proxy.terminate_proxy()

    def message_receiving_loop(self):
        while True:
            print "Entering socket.receive()."
            packet, _ = self.__socket.recvfrom(RECEIVING_BUFFER_SIZE)

    def __handle_message_from_mediator(self, header, message):
        msg_type = message.type
        if msg_type == drivermsg_pb2.DriverMsg.MsgType.DATA:
            print "DATA message came, but device details not set, ignoring."

        elif msg_type == drivermsg_pb2.DriverMsg.MsgType.PING:
            print "PING message came, handling."
            self.__handle_ping_message(header, message)

        elif msg_type == drivermsg_pb2.DriverMsg.MsgType.PONG:
            print "PONG message came, handling."
            self.__handle_pong_message(header, message)

        elif msg_type == drivermsg_pb2.DriverMsg.MsgType.DRIVER_DIED:
            print "DRIVER_DIED message came, but device details not set, ignoring."

        else:
            print "Unexpected message came: %s, ignoring." % (str(message.get_type()))

    def __handle_message_from_driver(self, header, message, client_proxy):
        msg_type = message.get_type()
        if msg_type == drivermsg_pb2.DriverMsg.MsgType.DATA:
            print "DATA message came for (%d: %d), handling." % \
                  (client_proxy.device_type, client_proxy.device_id)

        elif msg_type == drivermsg_pb2.DriverMsg.MsgType.PING:
            print "PING message came for (%d: %d), handling." % \
                  (client_proxy.device_type, client_proxy.device_id)

        elif msg_type == drivermsg_pb2.DriverMsg.MsgType.PONG:
            print "PONG message came for (%d: %d), handling." % \
                  (client_proxy.device_type, client_proxy.device_id)

        elif msg_type == drivermsg_pb2.DriverMsg.MsgType.DRIVER_DIED:
            print "DRIVER_DIED message came dor (%d: %d), handling." % \
                  (client_proxy.device_type, client_proxy.device_id)
            client_proxy.handle_driver_died_message(header, message)

        else:
            print "Unexpected message came %s for (%d: %d), ignoring." % \
                  (str(message.get_type()), client_proxy.device_type, client_proxy.device_id)

    def __handle_ping_message(self, header, message):
        pass

    def __handle_pong_message(self, header, message):
        pass