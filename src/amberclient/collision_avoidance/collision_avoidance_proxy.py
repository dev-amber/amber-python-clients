import logging
import logging.config

import os

from amberclient.common import amber_proxy
from amberclient.common import drivermsg_pb2
from amberclient.roboclaw import roboclaw_pb2


__author__ = 'paoolo'

DEVICE_TYPE = 9

LOGGER_NAME = 'CollisionAvoidanceProxy'
pwd = os.path.dirname(os.path.abspath(__file__))
logging.config.fileConfig('%s/collision_avoidance.ini' % pwd)


class CollisionAvoidanceProxy(amber_proxy.AmberProxy):
    def __init__(self, amber_client, device_id):
        super(CollisionAvoidanceProxy, self).__init__(DEVICE_TYPE, device_id, amber_client)
        self.__amber_client = amber_client
        self.__logger = logging.getLogger(LOGGER_NAME)
        self.__logger.info('Starting and registering CollisionAvoidanceProxy.')

    def send_motors_command(self, front_left, front_right, rear_left, rear_right):
        self.__logger.debug('Sending motors command: %d %d %d %d.', front_left, front_right, rear_left, rear_right)
        driver_msg = CollisionAvoidanceProxy.__build_send_motors_command_req_msg(front_left, front_right,
                                                                                 rear_left, rear_right)
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
        return NotImplemented

    def handle_data_msg(self, header, message):
        self.__logger.debug('Dropping data message.')