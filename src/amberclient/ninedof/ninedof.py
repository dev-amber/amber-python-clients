import logging
import logging.config

import os

from amberclient.common import amber_proxy, future_object
from amberclient.common import drivermsg_pb2
import ninedof_pb2


__author__ = 'paoolo'

DEVICE_TYPE = 1

LOGGER_NAME = 'NinedofProxy'
pwd = os.path.dirname(os.path.abspath(__file__))
logging.config.fileConfig('%s/ninedof.ini' % pwd)


class NinedofProxy(amber_proxy.AmberProxy):
    def __init__(self, amber_client, device_id):
        super(NinedofProxy, self).__init__(DEVICE_TYPE, device_id, amber_client)
        self.__amber_client, self.__syn_num, self.__future_objs = amber_client, 0, {}

        self.__logger = logging.getLogger(LOGGER_NAME)

        self.__logger.info('Starting and registering RoboclawProxy.')

    def register_ninedof_data_listener(self, freq, accel, gyro, magnet, listener):
        self.__logger.debug('Registering NinedofDataListener, freq: %d, a:%s, g:%s, m:%s.')

        driver_msg = self.__build_subscribe_action_msg(freq, accel, gyro, magnet)
        self.__ninedof_data_listener = listener

        self.__amber_client.send_message(self.build_header(), driver_msg)

    def unregister_data_listener(self):
        driver_msg = self.__build_subscribe_action_msg(0, False, False, False)

        self.__ninedof_data_listener = None

        self.__amber_client.send_message(self.build_header(), driver_msg)

    def get_axes_data(self, accel, gyro, magnet):
        syn_num = self.__get_next_syn_num()

        self.__logger.debug('Pulling NinedofData, a:%s, g:%s, m:%s.' % (accel, gyro, magnet))

        data_req_msg = self.__build_data_request_msg(syn_num, accel, gyro, magnet)

        ninedof_data = NinedofData()
        self.__future_objs[syn_num] = ninedof_data

        self.__amber_client.send_message(self.build_header(), data_req_msg)

        return ninedof_data

    def handle_data_msg(self, header, message):
        if not message.HasField('ackNum') or message.ackNum == 0:
            ninedof_data = NinedofData()
            self.__fill_structure(ninedof_data, message)
            ninedof_data.set_available()

            if self.__ninedof_data_listener is not None:
                self.__ninedof_data_listener.handle(ninedof_data)
        else:
            ack_num = message.ackNum
            if ack_num in self.__future_objs:
                obj = self.__future_objs[ack_num]
                del self.__future_objs[ack_num]

                if isinstance(obj, NinedofData):
                    self.__fill_structure(obj, message)
                    obj.set_available()

    def __get_next_syn_num(self):
        self.__syn_num += 1
        return self.__syn_num

    def __fill_structure(self, ninedof_data, message):
        sensor_data = message.Extensions[ninedof_pb2.sensorData]

        ninedof_data.set_accel(
            AxesData(sensor_data.accel.xAxis, sensor_data.accel.yAxis, sensor_data.accel.zAxis))
        ninedof_data.set_gyro(
            AxesData(sensor_data.gyro.xAxis, sensor_data.gyro.yAxis, sensor_data.gyro.zAxis))
        ninedof_data.set_magnet(
            AxesData(sensor_data.magnet.xAxis, sensor_data.magnet.yAxis, sensor_data.magnet.zAxis))

    def __build_subscribe_action_msg(self, freq, accel, gyro, magnet):
        driver_msg = drivermsg_pb2.DriverMsg()

        driver_msg.type = drivermsg_pb2.DriverMsg.DATA
        driver_msg.Extensions[ninedof_pb2.subscribeAction].freq = freq
        driver_msg.Extensions[ninedof_pb2.subscribeAction].accel = accel
        driver_msg.Extensions[ninedof_pb2.subscribeAction].gyro = gyro
        driver_msg.Extensions[ninedof_pb2.subscribeAction].magnet = magnet

        return driver_msg

    def __build_data_request_msg(self, syn_num, accel, gyro, magnet):
        driver_msg = drivermsg_pb2.DriverMsg()

        driver_msg.type = drivermsg_pb2.DriverMsg.DATA
        driver_msg.Extensions[ninedof_pb2.dataRequest].accel = accel
        driver_msg.Extensions[ninedof_pb2.dataRequest].gyro = gyro
        driver_msg.Extensions[ninedof_pb2.dataRequest].magnet = magnet
        driver_msg.synNum = syn_num

        return driver_msg


class AxesData(object):
    def __init__(self, x_axis, y_axis, z_axis):
        self.x_axis, self.y_axis, self.z_axis = x_axis, y_axis, z_axis

    def __str__(self):
        return "axes: x=%d, y=%d, z=%d" % (self.x_axis, self.y_axis, self.z_axis)


class NinedofData(future_object.FutureObject):
    def __init__(self):
        super(NinedofData, self).__init__()
        self.__accel, self.__gyro, self.__magnet = None, None, None

    def __str__(self):
        return "accel: %s\ngyro: %s\nmagnet: %s" % (self.__accel, self.__gyro, self.__magnet)

    def get_accel(self):
        if not self.is_available():
            self.wait_available()
        return self.__accel

    def set_accel(self, accel):
        self.__accel = accel

    def get_gyro(self):
        if not self.is_available():
            self.wait_available()
        return self.__gyro

    def set_gyro(self, gyro):
        self.__gyro = gyro

    def get_magnet(self):
        if not self.is_available():
            self.wait_available()
        return self.__magnet

    def set_magnet(self, magnet):
        self.__magnet = magnet