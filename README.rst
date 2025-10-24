Introduction
============




.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/natheihei/CircuitPython_AXS5106/workflows/Build%20CI/badge.svg
    :target: https://github.com/natheihei/CircuitPython_AXS5106/actions
    :alt: Build Status


.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Code Style: Ruff

Driver for AXS5106 touch controller


Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.

Installing to a Connected CircuitPython Device with Circup
==========================================================

Make sure that you have ``circup`` installed in your Python environment.
Install it with the following command if necessary:

.. code-block:: shell

    pip3 install circup

With ``circup`` installed and your CircuitPython device connected use the
following command to install:

.. code-block:: shell

    circup install axs5106

Or the following command to update an existing version:

.. code-block:: shell

    circup update

Usage Example
=============

.. code-block:: python

    import board
    import digitalio
    from axs5106 import AXS5106L

    # Initialize I2C bus
    i2c = board.I2C()

    # Initialize reset pin
    reset = digitalio.DigitalInOut(board.TOUCH_RST)

    # Initialize the touch controller with rotation and screen dimensions
    # rotation=4 is 90° clockwise, adjust based on your display orientation
    touch = AXS5106L(i2c, reset_pin=reset, rotation=4, dimensions=(320, 240))

    # Main loop
    while True:
        # Check if screen is being touched
        if touch.touched:
            # Get all touch points (supports up to 5 simultaneous touches)
            points = touch.touches
            for point in points:
                print(f"Touch {point['id']}: X={point['x']}, Y={point['y']}")

Documentation
=============
API documentation for this library can be found on `Read the Docs <https://circuitpython-axs5106.readthedocs.io/>`_.

For information on building library documentation, please check out
`this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/natheihei/CircuitPython_AXS5106/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
