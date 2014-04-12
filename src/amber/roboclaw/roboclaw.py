from amber.common import amber_proxy, future_object
from amber.common import drivermsg_pb2
import roboclaw_pb2

__author__ = 'paoolo'

DEVICE_TYPE = 3


class RoboclawProxy(amber_proxy.AmberProxy):
    def __init__(self, amber_client, device_id):
        super(RoboclawProxy, self).__init__(DEVICE_TYPE, device_id, amber_client)
        self.__amber_client, self.__syn_num, self.__future_objs = amber_client, 0, {}

        print('Starting and registering RoboclawProxy.')

    def send_motors_command(self, front_left, front_right, rear_left, rear_right):
        print('Sending MotorsCommand: %d %d %d %d.' % (front_left, front_right, rear_left, rear_right))

        driver_msg = drivermsg_pb2.DriverMsg()

        driver_msg.type = drivermsg_pb2.DriverMsg.DATA
        driver_msg.Extensions[roboclaw_pb2.motorsCommand].frontLeftSpeed = 0
        driver_msg.Extensions[roboclaw_pb2.motorsCommand].frontRightSpeed = 0
        driver_msg.Extensions[roboclaw_pb2.motorsCommand].rearLeftSpeed = 0
        driver_msg.Extensions[roboclaw_pb2.motorsCommand].rearRightSpeed = 0
        driver_msg.synNum = self.__get_next_syn_num()

        self.__amber_client.send_message(self.build_header(), driver_msg)

    def get_current_motors_speed(self):
        print('Getting current motors speed.')

        syn_num = self.__get_next_syn_num()

        current_speed_req_msg = self.__build_current_speed_request_msg(syn_num)

        motors_current_speed = MotorsCurrentSpeed()
        self.__future_objs[syn_num] = motors_current_speed

        self.__amber_client.send_message(self.build_header(), current_speed_req_msg)

        return motors_current_speed

    def handle_data_msg(self, header, message):
        print('Handling data message.')

        if message.HasField('ackNum') and message.ackNum != 0:
            ack_num = message.ackNum
            if ack_num in self.__future_objs:
                obj = self.__future_objs[ack_num]
                del self.__future_objs[ack_num]
                if isinstance(obj, MotorsCurrentSpeed):
                    self.__fill_motors_current_speed(obj, message)

    def __get_next_syn_num(self):
        self.__syn_num += 1
        return self.__syn_num

    def __fill_motors_current_speed(self, msc, message):
        input_msc = message.Extensions[roboclaw_pb2.currentSpeed]

        msc.set_front_left_speed(input_msc.frontLeftSpeed)
        msc.set_front_right_speed(input_msc.frontRightSpeed)
        msc.set_rear_left_speed(input_msc.rearLeftSpeed)
        msc.set_rear_right_speed(input_msc.rearRightSpeed)

        msc.set_available()

    def __build_current_speed_request_msg(self, syn_num):
        driver_msg_builder = drivermsg_pb2.DriverMsg()

        driver_msg_builder.type = drivermsg_pb2.DriverMsg.DATA
        driver_msg_builder.Extensions[roboclaw_pb2.currentSpeedRequest] = True
        driver_msg_builder.synNum = syn_num

        return driver_msg_builder


class MotorsCurrentSpeed(future_object.FutureObject):
    def __init__(self):
        super(MotorsCurrentSpeed, self).__init__()
        self.__front_left_speed, self.__front_right_speed = 0, 0
        self.__rear_left_speed, self.__rear_right_speed = 0, 0

    def __str__(self):
        return "Speed: fl=%d, fr=%d, rl=%d, rr=%d" % (self.__front_left_speed, self.__front_right_speed,
                                                      self.__rear_left_speed, self.__rear_right_speed)

    def get_front_left_speed(self):
        if not self.is_available():
            self.wait_available()
        return self.__front_left_speed

    def set_front_left_speed(self, v):
        self.__front_left_speed = v

    def get_front_right_speed(self):
        if not self.is_available():
            self.wait_available()
        return self.__front_right_speed

    def set_front_right_speed(self, v):
        self.__front_right_speed = v

    def get_rear_left_speed(self):
        if self.is_available():
            self.wait_available()
        return self.__rear_left_speed

    def set_rear_left_speed(self, v):
        self.__rear_left_speed = v

    def get_rear_right_speed(self):
        if not self.is_available():
            self.wait_available()
        return self.__rear_right_speed

    def set_rear_right_speed(self, v):
        self.__rear_right_speed = v
