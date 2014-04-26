from amber.common import amber_proxy, future_object
from amber.common import drivermsg_pb2
import dummy_pb2

__author__ = 'paoolo'

DEVICE_TYPE = 5


class DummyProxy(amber_proxy.AmberProxy):
    def __init__(self, amber_client, device_id):
        super(DummyProxy, self).__init__(DEVICE_TYPE, device_id, amber_client)
        self.__amber_client, self.__syn_num, self.__future_objs = amber_client, 0, {}

        print('Starting and registering DummyProxy.')

    def handle_data_msg(self, header, message):
        print('Handling data message')

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
        print('Set enable to %s' % value)

        driver_msg = self.__build_set_enable_req_msg(value)
        self.__amber_client.send_message(self.build_header(), driver_msg)

    def __build_set_enable_req_msg(self, value):
        driver_msg = drivermsg_pb2.DriverMsg()

        driver_msg.type = drivermsg_pb2.DriverMsg.DATA
        driver_msg.Extensions[dummy_pb2.enable] = value

        return driver_msg

    def set_message(self, message):
        print('Set message to %s' % message)

        driver_msg = self.__build_set_message_req_msg(message)
        self.__amber_client.send_message(self.build_header(), driver_msg)

    def __build_set_message_req_msg(self, message):
        driver_msg = drivermsg_pb2.DriverMsg()

        driver_msg.type = drivermsg_pb2.DriverMsg.DATA
        driver_msg.Extensions[dummy_pb2.message] = message

        return driver_msg

    def get_status(self):
        print('Get status')

        syn_num = self.__get_next_syn_num()

        driver_msg = self.__build_get_status_req_msg(syn_num)

        status = Status()
        self.__future_objs[syn_num] = status

        self.__amber_client.send_message(self.build_header(), driver_msg)

        return status

    def __build_get_status_req_msg(self, syn_num):
        driver_msg = drivermsg_pb2.DriverMsg()

        driver_msg.type = drivermsg_pb2.DriverMsg.DATA
        driver_msg.Extensions[dummy_pb2.get_status] = True
        driver_msg.synNum = syn_num

        return driver_msg

    def __fill_status(self, status, message):
        status.set_enable(message.Extensions[dummy_pb2.enable])
        status.set_message(message.Extensions[dummy_pb2.message])
        status.set_available()


class Status(future_object.FutureObject):
    def __init__(self):
        super(Status, self).__init__()
        self.__message, self.__enable = None, None

    def __str__(self):
        if not self.is_available():
            self.wait_available()
        return "message: %s, enable: %s" % (self.__message, str(self.__enable))

    def set_message(self, message):
        self.__message = message

    def set_enable(self, enable):
        self.__enable = enable