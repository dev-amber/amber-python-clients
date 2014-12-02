import logging
import logging.config

import os

from amber.common import amber_proxy, future_object
from amber.common import drivermsg_pb2
import drive_to_point_pb2


__author__ = 'paoolo'

DEVICE_TYPE = 5

LOGGER_NAME = 'DriveToPointProxy'
pwd = os.path.dirname(os.path.abspath(__file__))
try:
    logging.config.fileConfig('%s/DriveToPoint.ini' % pwd)
except BaseException:
    print 'Logging not set.'


class DriveToPointProxy(amber_proxy.AmberProxy):
    def __init__(self, amber_client, device_id):
        super(DriveToPointProxy, self).__init__(DEVICE_TYPE, device_id, amber_client)
        self.__amber_client, self.__syn_num, self.__future_objs, self.__listener = amber_client, 0, {}, None

        self.__logger = logging.getLogger(LOGGER_NAME)
        self.__logger.setLevel(logging.WARNING)

        self.__logger.info('Starting and registering DriveToPointProxy.')

    def handle_data_msg(self, header, message):
        """
        Handle DATA message type. Must be implemented.
        It services responses for requested operation and subscribed data.

        :param header:
        :param message:
        :return:
        """
        self.__logger.debug('Handling data message')

    def __get_next_syn_num(self):
        self.__syn_num += 1
        return self.__syn_num

    def set_targets(self, targets):
        self.__logger.debug('Set targets')

        driver_msg = self.__build_set_targets_req_msg(targets)
        self.__amber_client.send_message(self.build_header(), driver_msg)

    @staticmethod
    def __build_set_targets_req_msg(targets):
        driver_msg = drivermsg_pb2.DriverMsg()

        driver_msg.type = drivermsg_pb2.DriverMsg.DATA
        driver_msg.Extensions[drive_to_point_pb2.setTargets] = True
        driver_msg.Extensions[drive_to_point_pb2.targets].longitudes.extend(map(lambda t: t.x, targets))
        driver_msg.Extensions[drive_to_point_pb2.targets].latitudes.extend(map(lambda t: t.y, targets))
        driver_msg.Extensions[drive_to_point_pb2.targets].radiuses.extend(map(lambda t: t.r, targets))

        return driver_msg

    def get_next_target(self):
        self.__logger.debug('Get next target')

        syn_num = self.__get_next_syn_num()
        driver_msg = self.__build_get_next_target_req_msg(syn_num)

        result = Result()
        self.__future_objs[syn_num] = result

        self.__amber_client.send_message(self.build_header(), driver_msg)

        return result

    @staticmethod
    def __build_get_next_target_req_msg(syn_num):
        driver_msg = drivermsg_pb2.DriverMsg()

        driver_msg.type = drivermsg_pb2.DriverMsg.DATA
        driver_msg.Extensions[drive_to_point_pb2.getNextTarget] = True
        driver_msg.synNum = syn_num

        return driver_msg

    def get_next_targets(self):
        self.__logger.debug('Get next targets')

        syn_num = self.__get_next_syn_num()
        driver_msg = self.__build_get_next_targets_req_msg(syn_num)

        result = Result()
        self.__future_objs[syn_num] = result

        self.__amber_client.send_message(self.build_header(), driver_msg)

        return result

    @staticmethod
    def __build_get_next_targets_req_msg(syn_num):
        driver_msg = drivermsg_pb2.DriverMsg()

        driver_msg.type = drivermsg_pb2.DriverMsg.DATA
        driver_msg.Extensions[drive_to_point_pb2.getNextTargets] = True
        driver_msg.synNum = syn_num

        return driver_msg

    def get_visited_target(self):
        self.__logger.debug('Get visited target')

        syn_num = self.__get_next_syn_num()
        driver_msg = self.__build_get_visited_target_req_msg(syn_num)

        result = Result()
        self.__future_objs[syn_num] = result

        self.__amber_client.send_message(self.build_header(), driver_msg)

        return result

    @staticmethod
    def __build_get_visited_target_req_msg(syn_num):
        driver_msg = drivermsg_pb2.DriverMsg()

        driver_msg.type = drivermsg_pb2.DriverMsg.DATA
        driver_msg.Extensions[drive_to_point_pb2.getVisitedTarget] = True
        driver_msg.synNum = syn_num

        return driver_msg

    def get_visited_targets(self):
        self.__logger.debug('Get visited targets')

        syn_num = self.__get_next_syn_num()
        driver_msg = self.__build_get_visited_targets_req_msg(syn_num)

        result = Result()
        self.__future_objs[syn_num] = result

        self.__amber_client.send_message(self.build_header(), driver_msg)

        return result

    @staticmethod
    def __build_get_visited_targets_req_msg(syn_num):
        driver_msg = drivermsg_pb2.DriverMsg()

        driver_msg.type = drivermsg_pb2.DriverMsg.DATA
        driver_msg.Extensions[drive_to_point_pb2.getVisitedTargets] = True
        driver_msg.synNum = syn_num

        return driver_msg

    @staticmethod
    def __fill_target(result, message):
        _targets = message.Extensions[drive_to_point_pb2.targets]
        _targets = zip(_targets.longitudes, _targets.latitudes, _targets.radiuses)
        _target = _targets[0] if len(_targets) > 0 else None
        _target = Target(*_target) if not _target is None else None
        result.set_result(_target)
        result.set_available()

    @staticmethod
    def __fill_targets(result, message):
        _targets = message.Extensions[drive_to_point_pb2.targets]
        _targets = zip(_targets.longitudes, _targets.latitudes, _targets.radiuses)
        _targets = map(lambda target: Target(*target), _targets)
        result.set_result(_targets)
        result.set_available()


class Target(object):
    def __init__(self, x, y, r):
        self.x, self.y, self.r = x, y, r


class Result(future_object.FutureObject):
    def __init__(self):
        super(Result, self).__init__()
        self.__result = None

    def get_result(self):
        if not self.is_available():
            self.wait_available()
        return self.__result

    def set_result(self, result):
        self.__result = result