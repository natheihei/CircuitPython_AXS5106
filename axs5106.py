# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2025 natheihei
#
# SPDX-License-Identifier: MIT
"""
`axs5106`
================================================================================

Driver for AXS5106 touch controller


* Author(s): natheihei

Implementation Notes
--------------------

**Hardware:**

* AXS5106L Touch Controller

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads
"""

# imports

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/natheihei/CircuitPython_AXS5106.git"

import time
import digitalio
from adafruit_bus_device.i2c_device import I2CDevice
from micropython import const

try:
    from typing import List
except ImportError:
    pass


_AXS5106L_DEFAULT_I2C_ADDR = const(0x63)
_AXS5106L_ID_REG = const(0x08)
_AXS5106L_TOUCH_DATA_REG = const(0x01)
_AXS5106L_MAX_TOUCH_POINTS = const(5)
_AXS5106L_TOUCH_BUFFER_SIZE = const(14)


class AXS5106L:
    """
    A driver for the AXS5106L capacitive touch controller.
    """

    def __init__(
        self,
        i2c,
        address=_AXS5106L_DEFAULT_I2C_ADDR,
        debug=False,
        reset_pin=None,
        rotation=0,
        width=None,
        height=None,
    ):
        """
        Initialize the AXS5106L touch controller.

        :param i2c: The I2C bus object
        :param address: I2C address (default 0x63)
        :param debug: Enable debug output
        :param reset_pin: Optional reset pin (digitalio.DigitalInOut)
        :param rotation: Screen rotation (0-7). All 8 possible orientations:
            0: 0° (no rotation, no flip) - (x, y)
            1: 0° flip X - (width-1-x, y)
            2: 0° flip Y - (x, height-1-y)
            3: 180° (flip both X and Y) - (width-1-x, height-1-y)
            4: 90° CW - (height-1-y, x)
            5: 90° CW + flip X (= 270° CW + flip Y) - (y, x)
            6: 270° CW (= 90° CCW) - (width-1-y, height-1-x)
            7: 270° CW + flip X (= 90° CW + flip Y) - (width-1-y, x)
        :param width: Screen width in pixels (required for rotation transformations)
        :param height: Screen height in pixels (required for rotation transformations)
        """
        self._i2c = I2CDevice(i2c, address)
        self._debug = debug
        self._reset_pin = reset_pin
        self._rotation = rotation
        self._width = width
        self._height = height

        # Perform hardware reset if reset pin is provided
        if self._reset_pin is not None:
            self._reset_pin.switch_to_output(value=False)
            time.sleep(0.2)
            self._reset_pin.value = True
            time.sleep(0.3)

        # Read chip ID to verify communication
        chip_data = self._read(_AXS5106L_ID_REG, 3)
        if debug:
            print(f"Chip ID: {chip_data[0]:02X} {chip_data[1]:02X} {chip_data[2]:02X}")

        if chip_data[0] == 0 and chip_data[1] == 0 and chip_data[2] == 0:
            if debug:
                print("Warning: All zeros read from ID register")

    @property
    def touched(self) -> int:
        """Returns the number of touches currently detected"""
        data = self._read(_AXS5106L_TOUCH_DATA_REG, _AXS5106L_TOUCH_BUFFER_SIZE)
        return data[1]  # Touch count is at index 1

    @property
    def touches(self) -> List[dict]:
        """
        Returns a list of touchpoint dicts, with 'x' and 'y' containing the
        touch coordinates, and 'id' as the touch point index for multitouch tracking.
        Coordinates are automatically transformed based on the rotation setting.
        """
        touchpoints = []
        data = self._read(_AXS5106L_TOUCH_DATA_REG, _AXS5106L_TOUCH_BUFFER_SIZE)

        touch_count = data[1]
        if self._debug:
            print(f"Touch count: {touch_count}")

        if touch_count == 0:
            return []

        # Parse touch data - each touch point uses 6 bytes starting at offset 2
        for i in range(min(touch_count, _AXS5106L_MAX_TOUCH_POINTS)):
            offset = 2 + i * 6
            # X coordinate: high 4 bits from data[offset], low 8 bits from data[offset+1]
            raw_x = ((data[offset] & 0x0F) << 8) | data[offset + 1]
            # Y coordinate: high 4 bits from data[offset+2], low 8 bits from data[offset+3]
            raw_y = ((data[offset + 2] & 0x0F) << 8) | data[offset + 3]

            # Apply rotation transformation
            x, y = self._apply_rotation(raw_x, raw_y)

            point = {"x": x, "y": y, "id": i}
            if self._debug:
                print(f"Touch {i}: raw({raw_x}, {raw_y}) -> rotated({x}, {y})")
            touchpoints.append(point)

        return touchpoints

    def _apply_rotation(self, raw_x: int, raw_y: int) -> tuple:
        """
        Apply rotation transformation to raw touch coordinates.
        Supports all 8 possible orientations (4 rotations × 2 mirror states).

        :param raw_x: Raw X coordinate from sensor
        :param raw_y: Raw Y coordinate from sensor
        :return: Tuple of (transformed_x, transformed_y)
        """
        # Check if we have dimensions for transformations that need them
        w = self._width if self._width is not None else 0
        h = self._height if self._height is not None else 0

        if self._rotation == 0:
            # 0°: No transformation (x, y)
            return (raw_x, raw_y)
        elif self._rotation == 1:
            # 0° flip X: (width-1-x, y)
            return (w - 1 - raw_x if w > 0 else raw_x, raw_y)
        elif self._rotation == 2:
            # 0° flip Y: (x, height-1-y)
            return (raw_x, h - 1 - raw_y if h > 0 else raw_y)
        elif self._rotation == 3:
            # 180° (flip both): (width-1-x, height-1-y)
            return (w - 1 - raw_x if w > 0 else raw_x, h - 1 - raw_y if h > 0 else raw_y)
        elif self._rotation == 4:
            # 90° CW: (height-1-y, x)
            return (h - 1 - raw_y if h > 0 else raw_y, raw_x)
        elif self._rotation == 5:
            # 90° CW + flip X (swap x,y): (y, x)
            return (raw_y, raw_x)
        elif self._rotation == 6:
            # 270° CW (90° CCW): (width-1-y, height-1-x)
            return (w - 1 - raw_y if w > 0 else raw_y, h - 1 - raw_x if h > 0 else raw_x)
        elif self._rotation == 7:
            # 270° CW + flip X: (width-1-y, x)
            return (w - 1 - raw_y if w > 0 else raw_y, raw_x)
        else:
            # Fallback (should never reach here)
            return (raw_x, raw_y)

    def _read(self, register, length) -> bytearray:
        """Returns an array of 'length' bytes from the 'register'"""
        with self._i2c as i2c:
            i2c.write(bytes([register & 0xFF]))
            result = bytearray(length)
            i2c.readinto(result)
            if self._debug:
                print(f"\t${register:02X} => {[hex(i) for i in result]}")
            return result

    def _write(self, register, values) -> None:
        """Writes an array of 'length' bytes to the 'register'"""
        with self._i2c as i2c:
            values = [(v & 0xFF) for v in [register] + values]
            if self._debug:
                print(f"\t${values[0]:02X} <= {[hex(i) for i in values[1:]]}")
            i2c.write(bytes(values))
