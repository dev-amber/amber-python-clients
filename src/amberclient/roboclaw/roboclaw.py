import logging
import logging.config

import os

from amberclient.common import amber_proxy, future_object
from amberclient.common import drivermsg_pb2
import roboclaw_pb2


__author__ = 'paoolo'

DEVICE_TYPE = 2

LOGGER_NAME = 'RoboclawProxy'
pwd = os.path.dirname(os.path.abspath(__file__))
logging.config.fileConfig('%s/roboclaw.ini' % pwd)


class RoboclawProxy(amber_proxy.AmberProxy):
    def __init__(self, amber_client, device_id):
        super(RoboclawProxy, self).__init__(DEVICE_TYPE, device_id, amber_client)
        self.__amber_client = amber_client
        self.__logger = logging.getLogger(LOGGER_NAME)
        self.__logger.info('Starting and registering RoboclawProxy.')

    def handle_data_msg(self, header, message):
        self.__logger.debug('Handling data message.')

        if message.HasField('ackNum') and message.ackNum != 0:
            obj = self.get_future_object(message.ackNum)
            if isinstance(obj, MotorsCurrentSpeed):
                RoboclawProxy.__fill_motors_current_speed(obj, message)

    def send_motors_command(self, front_left, front_right, rear_left, rear_right):
        self.__logger.debug('Sending motors command: %d %d %d %d.', front_left, front_right, rear_left, rear_right)
        driver_msg = RoboclawProxy.__build_send_motors_command_req_msg(front_left, front_right, rear_left, rear_right)
        self.__amber_client.send_message(self.build_header(), driver_msg)

    @staticmethod
    def __build_send_motors_command_req_msg(front_left, front_right, rear_left, rear_right):
        driver_msg = drivermsg_pb2.DriverMsg()
        driver_msg.type = drivermsg_pb2.DriverMsg.DATA
        driver_msg.Extensions[roboclaw_pb2.motorsCommand].frontLeftSpeed = front_left
        driver_msg.Extensions[roboclaw_pb2.motorsCommand].frontRightSpeed = front_right
        driver_msg.Extensions[roboclaw_pb2.motorsCommand].rearLeftSpeed = rear_left
        driver_msg.Extensions[roboclaw_pb2.motorsCommand].rearRightSpeed = rear_right
        return driver_msg

    def get_current_motors_speed(self):
        self.__logger.debug('Getting current motors speed')
        syn_num = self.get_next_syn_num()
        current_speed_req_msg = RoboclawProxy.__build_current_speed_request_msg(syn_num)
        motors_current_speed = MotorsCurrentSpeed()
        self.set_future_object(syn_num, motors_current_speed)
        self.__amber_client.send_message(self.build_header(), current_speed_req_msg)
        return motors_current_speed

    @staticmethod
    def __build_current_speed_request_msg(syn_num):
        driver_msg_builder = drivermsg_pb2.DriverMsg()
        driver_msg_builder.type = drivermsg_pb2.DriverMsg.DATA
        driver_msg_builder.Extensions[roboclaw_pb2.currentSpeedRequest] = True
        driver_msg_builder.synNum = syn_num
        return driver_msg_builder

    @staticmethod
    def __fill_motors_current_speed(msc, message):
        input_msc = message.Extensions[roboclaw_pb2.currentSpeed]
        msc.set_front_left_speed(input_msc.frontLeftSpeed)
        msc.set_front_right_speed(input_msc.frontRightSpeed)
        msc.set_rear_left_speed(input_msc.rearLeftSpeed)
        msc.set_rear_right_speed(input_msc.rearRightSpeed)
        msc.set_available()


class MotorsCurrentSpeed(future_object.FutureObject):
    def __init__(self):
        super(MotorsCurrentSpeed, self).__init__()
        self.__front_left_speed, self.__front_right_speed = None, None
        self.__rear_left_speed, self.__rear_right_speed = None, None

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