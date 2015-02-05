import logging
import logging.config

import os

from amberclient.common import amber_proxy, future_object
from amberclient.common import drivermsg_pb2
import drive_to_point_pb2


__author__ = 'paoolo'

DEVICE_TYPE = 8

LOGGER_NAME = 'DriveToPoint'

pwd = os.path.dirname(os.path.abspath(__file__))
logging.config.fileConfig('%s/drive_to_point.ini' % pwd)


class DriveToPointProxy(amber_proxy.AmberProxy):
    def __init__(self, amber_client, device_id):
        super(DriveToPointProxy, self).__init__(DEVICE_TYPE, device_id, amber_client)
        self.__amber_client = amber_client
        self.__logger = logging.getLogger(LOGGER_NAME)
        self.__logger.info('Starting and registering DriveToPointProxy.')

    def handle_data_msg(self, header, message):
        self.__logger.debug('Handling data message')

        if message.HasField('ackNum') and message.ackNum != 0:
            obj = self.get_future_object(message.ackNum)
            if isinstance(obj, Result):
                if message.Extensions[drive_to_point_pb2.getNextTarget] or \
                        message.Extensions[drive_to_point_pb2.getVisitedTarget]:
                    DriveToPointProxy.__fill_target(obj, message)

                elif message.Extensions[drive_to_point_pb2.getNextTargets] or \
                        message.Extensions[drive_to_point_pb2.getVisitedTargets]:
                    DriveToPointProxy.__fill_targets(obj, message)

                elif message.Extensions[drive_to_point_pb2.getConfiguration]:
                    DriveToPointProxy.__fill_configuration(obj, message)

    def set_targets(self, targets):
        self.__logger.debug('Set targets')
        driver_msg = DriveToPointProxy.__build_set_targets_req_msg(targets)
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
        syn_num = self.get_next_syn_num()
        driver_msg = DriveToPointProxy.__build_get_next_target_req_msg(syn_num)
        result = Result()
        self.set_future_object(syn_num, result)
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
        syn_num = self.get_next_syn_num()
        driver_msg = DriveToPointProxy.__build_get_next_targets_req_msg(syn_num)
        result = Result()
        self.set_future_object(syn_num, result)
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
        syn_num = self.get_next_syn_num()
        driver_msg = DriveToPointProxy.__build_get_visited_target_req_msg(syn_num)
        result = Result()
        self.set_future_object(syn_num, result)
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
        syn_num = self.get_next_syn_num()
        driver_msg = DriveToPointProxy.__build_get_visited_targets_req_msg(syn_num)
        result = Result()
        self.set_future_object(syn_num, result)
        self.__amber_client.send_message(self.build_header(), driver_msg)
        return result

    @staticmethod
    def __build_get_visited_targets_req_msg(syn_num):
        driver_msg = drivermsg_pb2.DriverMsg()
        driver_msg.type = drivermsg_pb2.DriverMsg.DATA
        driver_msg.Extensions[drive_to_point_pb2.getVisitedTargets] = True
        driver_msg.synNum = syn_num
        return driver_msg

    def get_configuration(self):
        self.__logger.debug('Get configuration')
        syn_num = self.get_next_syn_num()
        driver_msg = DriveToPointProxy.__build_get_configuration_req_msg(syn_num)
        result = Result()
        self.set_future_object(syn_num, result)
        self.__amber_client.send_message(self.build_header(), driver_msg)
        return result

    @staticmethod
    def __build_get_configuration_req_msg(syn_num):
        driver_msg = drivermsg_pb2.DriverMsg()
        driver_msg.type = drivermsg_pb2.DriverMsg.DATA
        driver_msg.Extensions[drive_to_point_pb2.getConfiguration] = True
        driver_msg.synNum = syn_num
        return driver_msg

    @staticmethod
    def __fill_target(result, message):
        _targets = message.Extensions[drive_to_point_pb2.targets]
        _targets = zip(_targets.longitudes, _targets.latitudes, _targets.radiuses)
        _target = _targets[0] if len(_targets) > 0 else None
        _target = Point(*_target) if _target is not None else None
        _location = message.Extensions[drive_to_point_pb2.location]
        _location = Location(_location.x, _location.y, _location.p, _location.alfa, _location.timeStamp)
        result.set_result(_target)
        result.set_location(_location)
        result.set_available()

    @staticmethod
    def __fill_targets(result, message):
        _targets = message.Extensions[drive_to_point_pb2.targets]
        _targets = zip(_targets.longitudes, _targets.latitudes, _targets.radiuses)
        _targets = map(lambda target: Point(*target), _targets)
        _location = message.Extensions[drive_to_point_pb2.location]
        _location = Location(_location.x, _location.y, _location.p, _location.alfa, _location.timeStamp)
        result.set_result(_targets)
        result.set_location(_location)
        result.set_available()

    @staticmethod
    def __fill_configuration(result, message):
        _configuration = message.Extensions[drive_to_point_pb2.configuration]
        _configuration = Configuration(_configuration.maxSpeed)
        result.set_result(_configuration)
        result.set_available()


class Point(object):
    def __init__(self, x, y, r):
        self.x, self.y, self.r = x, y, r

    def _to_str(self):
        return 'point: %f, %f, %f' % (self.x, self.y, self.r)

    def __str__(self):
        return self._to_str()

    def __repr__(self):
        return self._to_str()


class Location(object):
    def __init__(self, x, y, p, alfa, timeStamp):
        self.x, self.y, self.p, self.alfa, self.timeStamp = x, y, p, alfa, timeStamp

    def _to_str(self):
        return 'location: %f, %f, %f, %f, %f' % (self.x, self.y, self.p, self.alfa, self.timeStamp)

    def __str__(self):
        return self._to_str()

    def __repr__(self):
        return self._to_str()


class Configuration(object):
    def __init__(self, max_speed):
        self.max_speed = max_speed

    def _to_str(self):
        return 'configuration: %f' % self.max_speed

    def __str__(self):
        return self._to_str()

    def __repr__(self):
        return self._to_str()


class Result(future_object.FutureObject):
    def __init__(self):
        super(Result, self).__init__()
        self.__result, self.__location = None, None

    def get_result(self):
        if not self.is_available():
            self.wait_available()
        return self.__result

    def set_result(self, result):
        self.__result = result

    def get_location(self):
        if not self.is_available():
            self.wait_available()
        return self.__location

    def set_location(self, location):
        self.__location = location