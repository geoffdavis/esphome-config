from esphome import pins
import esphome.codegen as cg
from esphome.components import spi, touchscreen
import esphome.config_validation as cv
from esphome.const import CONF_ID, CONF_INTERRUPT_PIN, CONF_THRESHOLD
from esphome.types import ConfigType

from . import STMPE610Component

DEPENDENCIES = ["spi"]

CONFIG_SCHEMA = (
    touchscreen.touchscreen_schema(calibration_required=True)
    .extend(
        {
            cv.GenerateID(): cv.declare_id(STMPE610Component),
            cv.Optional(CONF_INTERRUPT_PIN): pins.internal_gpio_input_pin_schema,
            # Minimum Z (pressure) sample for a touch to count. 0 accepts all.
            cv.Optional(CONF_THRESHOLD, default=0): cv.int_range(min=0, max=255),
        }
    )
    # Espressif's esp_lcd_touch_stmpe610 runs the chip at 1 MHz, SPI mode 1.
    # If the chip ID check fails in the configured mode, setup() retries in
    # the other one (mode 0 <-> 1), like Adafruit_STMPE610::begin().
    .extend(spi.spi_device_schema(default_data_rate=1e6, default_mode="MODE1"))
)


async def to_code(config: ConfigType) -> None:
    var = cg.new_Pvariable(config[CONF_ID])
    await spi.register_spi_device(var, config)
    await touchscreen.register_touchscreen(var, config)

    cg.add(var.set_threshold(config[CONF_THRESHOLD]))

    if CONF_INTERRUPT_PIN in config:
        pin = await cg.gpio_pin_expression(config[CONF_INTERRUPT_PIN])
        cg.add(var.set_irq_pin(pin))
