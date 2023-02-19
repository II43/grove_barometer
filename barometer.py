#!/usr/bin/python3
import sys
import time
import math
from grove.gpio import GPIO
import Adafruit_BMP.BMP085 as BMP085
 
 
charmap = {
    '0': 0x3f,
    '1': 0x06,
    '2': 0x5b,
    '3': 0x4f,
    '4': 0x66,
    '5': 0x6d,
    '6': 0x7d,
    '7': 0x07,
    '8': 0x7f,
    '9': 0x6f,
    '-': 0x40,
    '_': 0x08,
    ' ': 0x00
}
 
ADDR_AUTO = 0x40
ADDR_FIXED = 0x44
STARTADDR = 0xC0
BRIGHT_DARKEST = 0
BRIGHT_DEFAULT = 2
BRIGHT_HIGHEST = 7
 
 
class Grove4DigitDisplay(object):
    colon_index = 1
 
    def __init__(self, clk, dio, brightness=BRIGHT_DEFAULT):
        self.brightness = brightness
 
        self.clk = GPIO(clk, direction=GPIO.OUT)
        self.dio = GPIO(dio, direction=GPIO.OUT)
        self.data = [0] * 4
        self.show_colon = False
 
    def clear(self):
        self.show_colon = False
        self.data = [0] * 4
        self._show()
 
    def show(self, data):
        if type(data) is str:
            for i, c in enumerate(data):
                if c in charmap:
                    self.data[i] = charmap[c]
                else:
                    self.data[i] = 0
                if i == self.colon_index and self.show_colon:
                    self.data[i] |= 0x80
                if i == 3:
                    break
        elif type(data) is int:
            self.data = [0, 0, 0, charmap['0']]
            if data < 0:
                negative = True
                data = -data
            else:
                negative = False
            index = 3
            while data != 0:
                self.data[index] = charmap[str(data % 10)]
                index -= 1
                if index < 0:
                    break
                data = int(data / 10)
 
            if negative:
                if index >= 0:
                    self.data[index] = charmap['-']
                else:
                    self.data = charmap['_'] + [charmap['9']] * 3
        else:
            raise ValueError('Not support {}'.format(type(data)))
        self._show()
 
    def _show(self):
        with self:
            self._transfer(ADDR_AUTO)
 
        with self:
            self._transfer(STARTADDR)
            for i in range(4):
                self._transfer(self.data[i])
 
        with self:
            self._transfer(0x88 + self.brightness)
 
    def update(self, index, value):
        if index < 0 or index > 4:
            return
 
        if value in charmap:
            self.data[index] = charmap[value]
        else:
            self.data[index] = 0
 
        if index == self.colon_index and self.show_colon:
            self.data[index] |= 0x80
 
        with self:
            self._transfer(ADDR_FIXED)
 
        with self:
            self._transfer(STARTADDR | index)
            self._transfer(self.data[index])
 
        with self:
            self._transfer(0x88 + self.brightness)
 
 
    def set_brightness(self, brightness):
        if brightness > 7:
            brightness = 7
 
        self.brightness = brightness
        self._show()
 
    def set_colon(self, enable):
        self.show_colon = enable
        if self.show_colon:
            self.data[self.colon_index] |= 0x80
        else:
            self.data[self.colon_index] &= 0x7F
        self._show()
 
    def _transfer(self, data):
        for _ in range(8):
            self.clk.write(0)
            if data & 0x01:
                self.dio.write(1)
            else:
                self.dio.write(0)
            data >>= 1
            time.sleep(0.000001)
            self.clk.write(1)
            time.sleep(0.000001)
 
        self.clk.write(0)
        self.dio.write(1)
        self.clk.write(1)
        self.dio.dir(GPIO.IN)
 
        while self.dio.read():
            time.sleep(0.001)
            if self.dio.read():
                self.dio.dir(GPIO.OUT)
                self.dio.write(0)
                self.dio.dir(GPIO.IN)
        self.dio.dir(GPIO.OUT)
 
    def _start(self):
        self.clk.write(1)
        self.dio.write(1)
        self.dio.write(0)
        self.clk.write(0)
 
    def _stop(self):
        self.clk.write(0)
        self.dio.write(0)
        self.clk.write(1)
        self.dio.write(1)
 
    def __enter__(self):
        self._start()
 
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stop()
 
 
Grove = Grove4DigitDisplay
sensor = BMP085.BMP085()
 
 
def main():
    if len(sys.argv) < 3:
        # print('Usage: {} clk dio'.format(sys.argv[0]))
        # sys.exit(1)
        display = Grove4DigitDisplay(12, 13)
    else:
        display = Grove4DigitDisplay(int(sys.argv[1]), int(sys.argv[2]))

    count = 1

    while True:
        if (count % 5) == 0:
            pressure = sensor.read_pressure()
            pressure = math.floor(pressure*100)
            print(f'Pressure = {pressure} hPa')
            display.show(f'{pressure}')
        elif (count % 6) == 0:
            t = time.strftime("%H%M", time.localtime(time.time()))
            print(f'Time = {t}')
            display.show(t)
            display.set_colon(True)
        else:
            temperature = sensor.read_temperature()
            print(f'Temperature = {temperature:.2f} degC')
            temperature = math.floor(temperature*100)
            display.show(f'{temperature}')
            display.set_colon(False)


        count += 1
        time.sleep(5)

if __name__ == '__main__':
    main()

