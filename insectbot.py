from m5stack import *
from m5ui import *
from uiflow import *
import hat
import unit
import time
import wifiCfg
from m5mqtt import M5mqtt


class Insect:
    def __init__(self):
        self.leg_left_front = None
        self.leg_right_front = None
        self.leg_left_back = None
        self.leg_right_back = None
        self.curr_leg = None  # Current moving leg
        self.state = 'STILL'
        self.remote_ctrl = ''  # Remote control from MQTT

        self._label_distance = M5TextBox(25, 35, '', lcd.FONT_DejaVu40, 0xFFFFFF, rotate=0)
        self._label_wifi = M5TextBox(25, 85, 'WiFi...', lcd.FONT_DejaVu40, 0xFFFFFF, rotate=0)
        self._label_mqtt = M5TextBox(25, 135, 'MQTT...', lcd.FONT_DejaVu40, 0xFFFFFF, rotate=0)
        self._tof = unit.get(unit.TOF, unit.PORTA)

    def show_distance(self):
        self._label_distance.setText(str(self._tof.distance))

    def reset(self):
        self.leg_left_front.reset(20)
        self.leg_right_front.reset(20)
        self.leg_left_back.reset(-30)
        self.leg_right_back.reset(-30)

        self.curr_leg = None

    def is_still(self):
        return not (self.leg_left_front.is_moving() or
                    self.leg_right_front.is_moving() or
                    self.leg_left_back.is_moving() or
                    self.leg_right_back.is_moving())

    def move_forward(self):
        legs = [self.leg_left_front, self.leg_right_front, self.leg_left_back, self.leg_right_back]
        for leg in legs:
            leg.heartbeat()

        if not self.is_still():
            return

        # Move the body forward if necessary
        if self.leg_left_front.thigh_curr_degree == 50:
            for leg in [self.leg_left_front, self.leg_left_back]:
                leg.move_from_to(leg.thigh_curr_degree, leg.thigh_curr_degree - 30)
            for leg in [self.leg_right_front, self.leg_right_back]:
                leg.move_from_to(leg.thigh_curr_degree, leg.thigh_curr_degree - 20)
        if self.leg_right_front.thigh_curr_degree == 50:
            for leg in [self.leg_right_front, self.leg_right_back]:
                leg.move_from_to(leg.thigh_curr_degree, leg.thigh_curr_degree - 30)
            for leg in [self.leg_left_front, self.leg_left_back]:
                leg.move_from_to(leg.thigh_curr_degree, leg.thigh_curr_degree - 20)
            return

        # Choose the next leg to move
        next_leg = {self.leg_left_front: self.leg_right_back,
                    self.leg_right_front: self.leg_left_back,
                    self.leg_left_back: self.leg_left_front,
                    self.leg_right_back: self.leg_right_front,
                    }
        if not self.curr_leg:
            self.curr_leg = self.leg_right_front
        self.curr_leg = next_leg[self.curr_leg]

        # Move one leg forward
        if self.curr_leg in [self.leg_left_back, self.leg_right_back]:
            self.curr_leg.lift_from_to(self.curr_leg.thigh_curr_degree, 0)
        elif self.curr_leg in [self.leg_left_front, self.leg_right_front]:
            self.curr_leg.lift_from_to(self.curr_leg.thigh_curr_degree, 50)

    def turn_left(self, degree):
        """turn left a degree (0~90)"""
        legs = [self.leg_left_front, self.leg_right_front, self.leg_left_back, self.leg_right_back]
        for leg in legs:
            leg.heartbeat()

        if not self.is_still():
            return

        # Turn the body if necessary
        if self.leg_right_front.thigh_curr_degree == 20 + degree and \
                self.leg_right_back.thigh_curr_degree == -30 + degree and \
                self.leg_left_front.thigh_curr_degree == 20 - degree and \
                self.leg_left_back.thigh_curr_degree == -30 - degree:
            for leg in [self.leg_right_front, self.leg_right_back]:
                leg.move_from_to(leg.thigh_curr_degree, leg.thigh_curr_degree - degree)
            for leg in [self.leg_left_front, self.leg_left_back]:
                leg.move_from_to(leg.thigh_curr_degree, leg.thigh_curr_degree + degree)
            return

        # Choose the next leg to move
        next_leg = {self.leg_right_front: self.leg_left_front,
                    self.leg_left_front: self.leg_left_back,
                    self.leg_right_back: self.leg_right_front,
                    self.leg_left_back: self.leg_right_back,
                    }
        if not self.curr_leg:
            self.curr_leg = self.leg_left_back
        self.curr_leg = next_leg[self.curr_leg]

        # Move one leg
        if self.curr_leg in [self.leg_right_front, self.leg_right_back]:
            self.curr_leg.lift_from_to(self.curr_leg.thigh_curr_degree, self.curr_leg.thigh_curr_degree + degree)
        elif self.curr_leg in [self.leg_left_front, self.leg_left_back]:
            self.curr_leg.lift_from_to(self.curr_leg.thigh_curr_degree, self.curr_leg.thigh_curr_degree - degree)

    def turn_right(self, degree):
        legs = [self.leg_left_front, self.leg_right_front, self.leg_left_back, self.leg_right_back]
        for leg in legs:
            leg.heartbeat()

        if not self.is_still():
            return

        # Turn the body if necessary
        if self.leg_left_front.thigh_curr_degree == 20 + degree and \
                self.leg_left_back.thigh_curr_degree == -30 + degree and \
                self.leg_right_front.thigh_curr_degree == 20 - degree and \
                self.leg_right_back.thigh_curr_degree == -30 - degree:
            for leg in [self.leg_left_front, self.leg_left_back]:
                leg.move_from_to(leg.thigh_curr_degree, leg.thigh_curr_degree - degree)
            for leg in [self.leg_right_front, self.leg_right_back]:
                leg.move_from_to(leg.thigh_curr_degree, leg.thigh_curr_degree + degree)
            return

        # Choose the next leg to move
        next_leg = {self.leg_left_front: self.leg_right_front,
                    self.leg_right_front: self.leg_right_back,
                    self.leg_left_back: self.leg_left_front,
                    self.leg_right_back: self.leg_left_back,
                    }
        if not self.curr_leg:
            self.curr_leg = self.leg_right_back
        self.curr_leg = next_leg[self.curr_leg]

        # Move one leg
        if self.curr_leg in [self.leg_left_front, self.leg_left_back]:
            self.curr_leg.lift_from_to(self.curr_leg.thigh_curr_degree, self.curr_leg.thigh_curr_degree + degree)
        elif self.curr_leg in [self.leg_right_front, self.leg_right_back]:
            self.curr_leg.lift_from_to(self.curr_leg.thigh_curr_degree, self.curr_leg.thigh_curr_degree - degree)

    def restore(self):
        """Restore to the initial pose"""
        legs = [self.leg_left_front, self.leg_right_front, self.leg_left_back, self.leg_right_back]
        for leg in legs:
            leg.heartbeat()

        if not self.is_still():
            return

        right_side_is_ok = self.leg_right_front.thigh_curr_degree == 20 and \
                           self.leg_right_back.thigh_curr_degree == -30
        if right_side_is_ok:
            if self.leg_left_front.thigh_curr_degree == 20 and \
                    self.leg_left_back.thigh_curr_degree == 0:
                self.leg_left_back.lift_from_to(self.leg_left_back.thigh_curr_degree, -30)
            if self.leg_left_front.thigh_curr_degree == 50 and \
                    self.leg_left_back.thigh_curr_degree == 0:
                self.leg_left_front.lift_from_to(self.leg_left_front.thigh_curr_degree, 20)
            if self.leg_left_front.thigh_curr_degree == 0 and \
                    self.leg_left_back.thigh_curr_degree == -50:
                self.leg_left_back.lift_from_to(self.leg_left_back.thigh_curr_degree, 0)
            if self.leg_left_front.thigh_curr_degree == 0 and \
                    self.leg_left_back.thigh_curr_degree == 0:
                self.leg_left_front.lift_from_to(self.leg_left_front.thigh_curr_degree, 20)

        left_side_is_ok = self.leg_left_front.thigh_curr_degree == 20 and \
                          self.leg_left_back.thigh_curr_degree == -30
        if left_side_is_ok:
            if self.leg_right_front.thigh_curr_degree == 0 and \
                    self.leg_right_back.thigh_curr_degree == -50:
                self.leg_right_back.lift_from_to(self.leg_right_back.thigh_curr_degree, 0)
            if self.leg_right_front.thigh_curr_degree == 0 and \
                    self.leg_right_back.thigh_curr_degree == 0:
                self.leg_right_front.lift_from_to(self.leg_right_front.thigh_curr_degree, 20)
            if self.leg_right_front.thigh_curr_degree == 20 and \
                    self.leg_right_back.thigh_curr_degree == 0:
                self.leg_right_back.lift_from_to(self.leg_right_back.thigh_curr_degree, -30)
            if self.leg_right_front.thigh_curr_degree == 50 and \
                    self.leg_right_back.thigh_curr_degree == 0:
                self.leg_right_front.lift_from_to(self.leg_right_front.thigh_curr_degree, 20)

        self.curr_leg = None

    def is_too_close(self):
        if self._tof.distance < 160:
            return True
        return False

    def is_init_pose(self):
        '''Whether it is restored to the initial pose'''

        return self.leg_left_front.thigh_curr_degree == 20 and \
               self.leg_right_front.thigh_curr_degree == 20 and \
               self.leg_left_back.thigh_curr_degree == -30 and \
               self.leg_right_back.thigh_curr_degree == -30


class Leg:
    def __init__(self, thigh_servo, thigh_offset, calf_servo, calf_offset):
        self.servos = hat.get(hat.SERVOS)
        self._thigh = thigh_servo
        self._thigh_offset = thigh_offset
        self.thigh_curr_degree = 0
        self._thigh_begin_degree = 0  # The begin degree when moving thigh
        self._thigh_end_degree = 0  # The end degree when moving thigh

        self._calf = calf_servo
        self._calf_offset = calf_offset
        self._calf_curr_degree = 0

        self._pulse = 0
        self._state = 'STILL'

    def _set_thigh(self, degree):
        self.thigh_curr_degree = degree

        # unify the rotating direction of all servoes
        if self._thigh in {1, 4}:
            degree = -1 * degree

        self.servos.SetAngle(self._thigh, degree + self._thigh_offset)

    def _set_calf(self, degree):
        self._calf_curr_degree = degree

        # unify the rotating direction of all servoes
        if self._calf in {3, 6}:
            degree = -1 * degree

        self.servos.SetAngle(self._calf, degree + self._calf_offset)

    def reset(self, thigh_degree):
        self._set_thigh(thigh_degree)
        self._set_calf(0)

    def is_moving(self):
        return self._pulse != 0

    def heartbeat(self):
        if self._state == 'LIFT_FROM_TO':
            self._lift_from_to(self._thigh_begin_degree, self._thigh_end_degree, 30)
        if self._state == 'MOVE_FROM_TO':
            self._move_from_to(self._thigh_begin_degree, self._thigh_end_degree, 20)
        if self._state == 'STILL':
            pass

    def lift_from_to(self, begin, end):
        """Enter LIFT_FROM_TO mode, set the thigh's begin degree to end"""

        self._state = 'LIFT_FROM_TO'
        self._thigh_begin_degree = begin
        self._thigh_end_degree = end

    def move_from_to(self, begin, end):
        """Enter MOVE_FROM_TO mode, set the thigh's begin and end degree"""
        self._state = 'MOVE_FROM_TO'
        self._thigh_begin_degree = begin
        self._thigh_end_degree = end

    def still(self):
        """Enter STILL mode"""
        self._state = 'STILL'

    def _lift_from_to(self, begin, end, total_pulses):
        """Lift the calf and move the thigh form degree begin to end in total pulses"""

        self._pulse += 1

        degree = self._pulse * (end - begin) / total_pulses + begin
        self._set_thigh(degree)

        self._set_calf(-(self._pulse - 15) ** 2 * 5 / total_pulses + 15 ** 2 * 5 / total_pulses)

        if self._pulse >= total_pulses and \
                self._calf_curr_degree == 0:
            self._pulse = 0
            self._state = 'STILL'

    def _move_from_to(self, begin, end, total_pulses):
        """Move the thigh from degree begin to end in total pulses"""

        self._pulse += 1

        degree = self._pulse * (end - begin) / total_pulses + begin
        self._set_thigh(degree)

        if self._pulse >= total_pulses:
            self._pulse = 0
            self._state = 'STILL'


insect = Insect()

# Connect WiFi
for retry in range(3):
    if wifiCfg.wlan_sta.isconnected():
        insect._label_wifi.setText('WiFi OK')
        break
else:
    insect._label_wifi.setText('No WiFi')


# MQTT callback function
def mqtt_callback(topic_data):
    insect.remote_ctrl = topic_data
    insect._label_mqtt.setText(topic_data)


m5mqtt = M5mqtt('insectbot', 'broker-cn.emqx.io', 1883, '', '', 300)
m5mqtt.subscribe(str('insect'), mqtt_callback)
m5mqtt.start()

# Calibrate all legs
insect.leg_left_back = Leg(1, 48, 2, 73)
insect.leg_left_front = Leg(4, 134, 3, 100)
insect.leg_right_back = Leg(5, 120, 6, 112)
insect.leg_right_front = Leg(8, 49, 7, 77)

insect.reset()

# setScreenColor(0x111155)

# Infinite heart beats
insect.state = 'MOVE_FORWARD'

while True:
    time.sleep_ms(1)

    if insect.is_still():
        insect.show_distance()

    # Control from remote
    if insect.remote_ctrl == 'fwd':
        insect.state = 'MOVE_FORWARD'
    elif insect.remote_ctrl == 'bwd':
        pass
    elif insect.remote_ctrl == 'left':
        insect.state = 'TURN_LEFT'
    elif insect.remote_ctrl == 'right':
        insect.state = 'TURN_RIGHT'

    # Move according to current state
    if insect.state == 'MOVE_FORWARD':
        insect.move_forward()
        if insect.is_still() and insect.is_too_close():
            insect.state = 'RESTORE'
    elif insect.state == 'RESTORE':
        insect.restore()
        if insect.is_init_pose():
            if insect.is_too_close():
                insect.state = 'TURN_RIGHT'
            else:
                insect.state = 'MOVE_FORWARD'
    elif insect.state == 'TURN_RIGHT':
        insect.turn_right(60)
        if insect.is_init_pose():
            if insect.is_too_close():
                insect.state = 'TURN_RIGHT'
            else:
                insect.state = 'MOVE_FORWARD'

