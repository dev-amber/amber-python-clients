import amber_proxy
import drivermsg_pb2
import future_object
import hokuyo_pb2

__author__ = 'paoolo'

DEVICE_TYPE = 4


class HokuyoProxy(amber_proxy.AmberProxy):
    def __init__(self, amber_client, device_id):
        super(HokuyoProxy, self).__init__(DEVICE_TYPE, device_id, amber_client, None)
        self.__amber_client, self.__syn_num, self.__future_objs = amber_client, 0, {}

        print('Starting and registering HokuyoProxy.')

    def handle_data_msg(self, header, message):
        print('Handling data message')

        if message.HasField('ackNum') and message.ackNum != 0:
            ack_num = message.ackNum
            if ack_num in self.__future_objs:
                obj = self.__future_objs[ack_num]
                del self.__future_objs[ack_num]

                if isinstance(obj, VersionInfo):
                    self.__fill_version_info(obj, message)
                elif isinstance(obj, SensorState):
                    self.__fill_sensor_state(obj, message)
                elif isinstance(obj, SensorSpecs):
                    self.__fill_sensor_specs(obj, message)

    def __get_next_syn_num(self):
        self.__syn_num += 1
        return self.__syn_num

    def laser_on(self):
        print('Laser on.')

        driver_msg = self.__build_laser_on_req_msg()
        self.__amber_client.send_message(self.build_header(), driver_msg)

    def __build_laser_on_req_msg(self):
        driver_msg = drivermsg_pb2.DriverMsg()

        driver_msg.type = drivermsg_pb2.DriverMsg.DATA
        driver_msg.Extensions[hokuyo_pb2.laser_on] = True

        return driver_msg

    def laser_off(self):
        print('Laser off.')

        driver_msg = self.__build_laser_off_req_msg()
        self.__amber_client.send_message(self.build_header(), driver_msg)

    def __build_laser_off_req_msg(self):
        driver_msg = drivermsg_pb2.DriverMsg()

        driver_msg.type = drivermsg_pb2.DriverMsg.DATA
        driver_msg.Extensions[hokuyo_pb2.laser_off] = True

        return driver_msg

    def reset(self):
        print('Reset.')

        driver_msg = self.__build_reset_req_msg()
        self.__amber_client.send_message(self.build_header(), driver_msg)

    def __build_reset_req_msg(self):
        driver_msg = drivermsg_pb2.DriverMsg()

        driver_msg.type = driver_msg.DriverMsg.DATA
        driver_msg.Extensions[hokuyo_pb2.reset] = True

        return driver_msg

    def set_motor_speed(self, motor_speed):
        print('Set motor speed to %d.' % motor_speed)

        driver_msg = self.__build_set_motor_speed_req_msg(motor_speed)
        self.__amber_client.send_message(self.build_header(), driver_msg)

    def __build_set_motor_speed_req_msg(self, motor_speed):
        driver_msg = drivermsg_pb2.DriverMsg()

        driver_msg.type = drivermsg_pb2.DriverMsg.DATA
        driver_msg.Extensions[hokuyo_pb2.set_motor_speed] = True
        driver_msg.Extensions[hokuyo_pb2.motor_speed] = motor_speed

        return driver_msg

    def set_high_sensitive(self, enable):
        print('Set high sensitive to %r.' % enable)

        driver_msg = self.__build_set_high_sensitive_req_msg(enable)
        self.__amber_client.send_message(self.build_header(), driver_msg)

    def __build_set_high_sensitive_req_msg(self, enable):
        driver_msg = drivermsg_pb2.DriverMsg()

        driver_msg.type = drivermsg_pb2.DriverMsg.DATA
        driver_msg.Extensions[hokuyo_pb2.set_high_sensitive] = True
        driver_msg.Extensions[hokuyo_pb2.high_sensitive] = enable

        return driver_msg

    def get_version_info(self):
        print('Get version info.')

        syn_num = self.__get_next_syn_num()

        driver_msg = self.__build_get_version_info_req_msg(syn_num)

        version_info = VersionInfo()
        self.__future_objs[syn_num] = version_info

        self.__amber_client.send_message(self.build_header(), driver_msg)

        return version_info

    def __build_get_version_info_req_msg(self, syn_num):
        driver_msg = drivermsg_pb2.DriverMsg()

        driver_msg.type = drivermsg_pb2.DriverMsg.DATA
        driver_msg.Extensions[hokuyo_pb2.get_version_info] = True
        driver_msg.synNum = syn_num

        return driver_msg

    def __fill_version_info(self, version_info, message):
        version = message.Extensions[hokuyo_pb2.version]

        version_info.set_vendor(version.vendor)
        version_info.set_product(version.product)

        version_info.set_firmware(version.firmware)
        version_info.set_protocol(version.protocol)
        version_info.set_serial(version.serial)

        version_info.set_available()

    def get_sensor_state(self):
        print('Get sensor state')

        syn_num = self.__get_next_syn_num()

        driver_msg = self.__build_get_sensor_state_req_msg(syn_num)

        sensor_state = SensorState()
        self.__future_objs[syn_num] = sensor_state

        self.__amber_client.send_message(self.build_header(), driver_msg)

        return sensor_state

    def __build_get_sensor_state_req_msg(self, syn_num):
        driver_msg = drivermsg_pb2.DriverMsg()

        driver_msg.type = drivermsg_pb2.DriverMsg.DATA
        driver_msg.Extensions[hokuyo_pb2.get_sensor_state] = True
        driver_msg.synNum = syn_num

        return driver_msg

    def __fill_sensor_state(self, sensor_state, message):
        state = message.Extensions[hokuyo_pb2.state]

        sensor_state.set_model(state.model)

        sensor_state.set_Laser(state.laser)

        sensor_state.set_motor_speed(state.motor_speed)
        sensor_state.set_measure_mode(state.measure_mode)
        sensor_state.set_bit_rate(state.bit_rate)

        sensor_state.set_time(state.time)

        sensor_state.set_diagnostic(state.diagnostic)

        sensor_state.set_available()

    def get_sensor_specs(self):
        print('Get sensor specs')

        syn_num = self.__get_next_syn_num()

        driver_msg = self.__build_get_sensor_specs_req_msg(syn_num)

        sensor_specs = SensorSpecs()
        self.__future_objs[syn_num] = sensor_specs

        self.__amber_client.send_message(self.build_header(), driver_msg)

        return sensor_specs


    def __build_get_sensor_specs_req_msg(self, syn_num):
        driver_msg = drivermsg_pb2.DriverMsg()

        driver_msg.type = drivermsg_pb2.DriverMsg.DATA
        driver_msg.Extensions[hokuyo_pb2.get_sensor_specs] = True
        driver_msg.synNum = syn_num

        return driver_msg

    def __fill_sensor_specs(self, sensor_specs, message):
        specs = message.Extensions[hokuyo_pb2.specs]

        sensor_specs.set_model(specs.model)

        sensor_specs.set_distance_minimum(specs.distance_minimum)
        sensor_specs.set_distance_maximum(specs.distance_maximum)

        sensor_specs.set_area_resolution(specs.area_resolution)
        sensor_specs.set_area_minimum(specs.area_minimum)
        sensor_specs.set_area_maximum(specs.area_maximum)
        sensor_specs.set_area_front(specs.area_front)

        sensor_specs.set_motor_speed(specs.motor_speed)


class VersionInfo(future_object.FutureObject):
    def __init__(self):
        super(VersionInfo, self).__init__()
        self.__vendor, self.__product, self.__firmware, self.__protocol, self.__serial = None, None, None, None, None

    def set_vendor(self, vendor):
        self.__vendor = vendor

    def get_vendor(self):
        if not self.is_available():
            self.wait_available()
        return self.__vendor

    def set_product(self, product):
        self.__product = product

    def get_product(self):
        if not self.is_available():
            self.wait_available()
        return self.__product

    def set_firmware(self, firmware):
        self.__firmware = firmware

    def get_firmware(self):
        if not self.is_available():
            self.wait_available()
        return self.__firmware

    def set_protocol(self, protocol):
        self.__protocol = protocol

    def get_protocol(self):
        if not self.is_available():
            self.wait_available()
        return self.__protocol

    def set_serial(self, serial):
        self.__serial = serial

    def get_serial(self):
        if not self.is_available():
            self.wait_available()
        return self.__serial


class SensorState(future_object.FutureObject):
    def __init__(self):
        super(SensorState, self).__init__()
        self.__model, self.__laser, self.__motor_speed, self.__measure_mode = None, None, None, None
        self.__bit_rate, self.__time, self.__diagnostic = None, None, None

    def set_model(self, model):
        self.__model = model

    def get_model(self):
        if not self.is_available():
            self.wait_available()
        return self.__model

    def set_laser(self, laser):
        self.__laser = laser

    def get_laser(self):
        if not self.is_available():
            self.wait_available()
        return self.__laser

    def set_motor_speed(self, motor_speed):
        self.__motor_speed = motor_speed

    def get_motor_speed(self):
        if not self.is_available():
            self.wait_available()
        return self.__motor_speed

    def set_measure_mode(self, measure_mode):
        self.__measure_mode = measure_mode

    def get_measure_mode(self):
        if not self.is_available():
            self.wait_available()
        return self.__measure_mode

    def set_bit_rate(self, bit_rate):
        self.__bit_rate = bit_rate

    def get_bit_rate(self):
        if not self.is_available():
            self.wait_available()
        return self.__bit_rate

    def set_time(self, time):
        self.__time = time

    def get_time(self):
        if not self.is_available():
            self.wait_available()
        return self.__time

    def set_diagnostic(self, diagnostic):
        self.__diagnostic = diagnostic

    def get_diagnostic(self):
        if not self.is_available():
            self.wait_available()
        return self.__diagnostic


class SensorSpecs(future_object.FutureObject):
    def __init__(self):
        super(SensorSpecs, self).__init__()
        self.__model = None
        self.__distance_minimum, self.__distance_maximum = 0, 0
        self.__area_resolution, self.__area_minimum, self.__area_maximum, self.__area_front = 0, 0, 0, 0
        self.__motor_speed = 0

    def set_model(self, model):
        self.__model = model

    def get_model(self):
        if not self.is_available():
            self.wait_available()
        return self.__model

    def set_distance_minimum(self, distance_minimum):
        self.__distance_minimum = distance_minimum

    def get_distance_minimum(self):
        if not self.is_available():
            self.wait_available()
        return self.__distance_minimum

    def set_distance_maximum(self, distance_maximum):
        self.__distance_maximum = distance_maximum

    def get_distance_maximum(self):
        if not self.is_available():
            self.wait_available()
        return self.__distance_maximum

    def set_area_resolution(self, area_resolution):
        self.__area_resolution = area_resolution

    def get_area_resolution(self):
        if not self.is_available():
            self.wait_available()
        return self.__area_resolution

    def set_area_minimum(self, area_minimum):
        self.__area_minimum = area_minimum

    def get_area_minimum(self):
        if not self.is_available():
            self.wait_available()
        return self.__area_minimum

    def set_area_maximum(self, area_maximum):
        self.__area_maximum = area_maximum

    def get_area_maximum(self):
        if not self.is_available():
            self.wait_available()
        return self.__area_maximum

    def set_area_front(self, area_front):
        self.__area_front = area_front

    def get_area_front(self):
        if not self.is_available():
            self.wait_available()
        return self.__area_front

    def set_motor_speed(self, motor_speed):
        self.__motor_speed = motor_speed

    def get_motor_speed(self):
        if not self.is_available():
            self.wait_available()
        return self.__motor_speed