"""ST STMPE610 resistive touch controller (SPI).

Platforms:
  touchscreen: the touch controller itself (touchscreen.py)
  output:      one of the STMPE610's spare GPIOs as a binary output (output.py)
"""

import esphome.codegen as cg
from esphome.components import spi, touchscreen

CODEOWNERS = ["@geoffdavis"]
DEPENDENCIES = ["spi"]

CONF_STMPE610_ID = "stmpe610_id"

stmpe610_ns = cg.esphome_ns.namespace("stmpe610")
STMPE610Component = stmpe610_ns.class_(
    "STMPE610Component",
    touchscreen.Touchscreen,
    spi.SPIDevice,
)
