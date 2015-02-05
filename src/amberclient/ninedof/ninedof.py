import logging
import logging.config

import os

from amberclient.common import amber_proxy, future_object
from amberclient.common import drivermsg_pb2
import ninedof_pb2


__author__ = 'paoolo'

DEVICE_TYPE = 1

LOGGER_NAME = 'Ninedof'

pwd = os.path.dirname(os.path.abspath(__file__))
logging.config.fileConfig('%s/ninedof.ini' % pwd)


class NinedofProxy(amber_proxy.AmberProxy):
    def __init__(self, amber_client, device_id):
        super(NinedofProxy, self).__init__(DEVICE_TYPE, device_id, amber_client)
        self.__amber_client, self.__sensors = amber_client, 0b0
        self.__logger = logging.getLogger(LOGGER_NAME)
        self.__logger.info('Starting and registering NinedofProxy.')

    def subscribe(self, listener, accel=True, gyro=True, magnet=True, freq=100):
        """ Only first invocation could set which sensors will be listened. """
        self.__logger.debug('Subscribe: freq: %d, a:%s, g:%s, m:%s.', freq, accel, gyro, magnet)
        listeners_count = self.append_listener(listener)
        if listeners_count == 0:
            driver_msg = NinedofProxy.__build_subscription_action_msg(freq, accel, gyro, magnet)
            self.__amber_client.send_message(self.build_header(), driver_msg)

    def unsubscribe(self, listener=None):
        self.__logger.debug('Unsubscribe')
        listeners_length = self.remove_listener(listener)
        if listeners_length == 0:
            driver_msg = NinedofProxy.__build_subscription_action_msg(0, False, False, False)
            self.__amber_client.send_message(self.build_header(), driver_msg)

    @staticmethod
    def __build_subscription_action_msg(freq, accel, gyro, magnet):
        driver_msg = drivermsg_pb2.DriverMsg()
        driver_msg.type = drivermsg_pb2.DriverMsg.DATA
        driver_msg.Extensions[ninedof_pb2.subscribeAction].freq = freq
        driver_msg.Extensions[ninedof_pb2.subscribeAction].accel = accel
        driver_msg.Extensions[ninedof_pb2.subscribeAction].gyro = gyro
        driver_msg.Extensions[ninedof_pb2.subscribeAction].magnet = magnet
        return driver_msg

    def handle_data_msg(self, header, message):
        self.__logger.debug('Handling data message')

        if not message.HasField('ackNum') or message.ackNum == 0:
            if message.HasExtension(ninedof_pb2.sensorData):
                ninedof_data = NinedofData()
                NinedofProxy.__fill_structure(ninedof_data, message)
                listeners = self.get_listeners()
                for listener in listeners:
                    listener.handle(ninedof_data)

        elif message.HasField('ackNum') and message.ackNum != 0:
            obj = self.get_future_object(message.ackNum)
            if isinstance(obj, NinedofData):
                NinedofProxy.__fill_structure(obj, message)

    def get_sensor_data(self, accel=True, gyro=True, magnet=True):
        self.__logger.debug('Get axes data: a:%s, g:%s, m:%s.', accel, gyro, magnet)
        syn_num = self.get_next_syn_num()
        data_req_msg = NinedofProxy.__build_get_sensor_data_req_msg(syn_num, accel, gyro, magnet)
        ninedof_data = NinedofData()
        self.set_future_object(syn_num, ninedof_data)
        self.__amber_client.send_message(self.build_header(), data_req_msg)
        return ninedof_data

    @staticmethod
    def __build_get_sensor_data_req_msg(syn_num, accel, gyro, magnet):
        driver_msg = drivermsg_pb2.DriverMsg()
        driver_msg.type = drivermsg_pb2.DriverMsg.DATA
        driver_msg.Extensions[ninedof_pb2.dataRequest].accel = accel
        driver_msg.Extensions[ninedof_pb2.dataRequest].gyro = gyro
        driver_msg.Extensions[ninedof_pb2.dataRequest].magnet = magnet
        driver_msg.synNum = syn_num
        return driver_msg

    @staticmethod
    def __fill_structure(ninedof_data, message):
        sensor_data = message.Extensions[ninedof_pb2.sensorData]
        ninedof_data.set_accel(
            AxesData(sensor_data.accel.xAxis, sensor_data.accel.yAxis, sensor_data.accel.zAxis))
        ninedof_data.set_gyro(
            AxesData(sensor_data.gyro.xAxis, sensor_data.gyro.yAxis, sensor_data.gyro.zAxis))
        ninedof_data.set_magnet(
            AxesData(sensor_data.magnet.xAxis, sensor_data.magnet.yAxis, sensor_data.magnet.zAxis))
        ninedof_data.set_available()


class AxesData(object):
    def __init__(self, x_axis, y_axis, z_axis):
        self.x_axis, self.y_axis, self.z_axis = x_axis, y_axis, z_axis


class NinedofData(future_object.FutureObject):
    def __init__(self):
        super(NinedofData, self).__init__()
        self.__accel, self.__gyro, self.__magnet = None, None, None

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