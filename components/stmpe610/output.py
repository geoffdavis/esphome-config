import esphome.codegen as cg
from esphome.components import output
import esphome.config_validation as cv
from esphome.const import CONF_ID, CONF_PIN
from esphome.types import ConfigType

from . import CONF_STMPE610_ID, STMPE610Component, stmpe610_ns

DEPENDENCIES = ["touchscreen"]

STMPE610GPIOOutput = stmpe610_ns.class_("STMPE610GPIOOutput", output.BinaryOutput)

CONFIG_SCHEMA = output.BINARY_OUTPUT_SCHEMA.extend(
    {
        cv.Required(CONF_ID): cv.declare_id(STMPE610GPIOOutput),
        cv.GenerateID(CONF_STMPE610_ID): cv.use_id(STMPE610Component),
        # GPIO4-7 are the touch panel lines (X+/X-/Y+/Y-), so only 0-3 are
        # usable. The original PiTFT 2.8" resistive wires GPIO2 to the backlight.
        cv.Optional(CONF_PIN, default=2): cv.int_range(min=0, max=3),
    }
)


async def to_code(config: ConfigType) -> None:
    var = cg.new_Pvariable(config[CONF_ID])
    await output.register_output(var, config)
    parent = await cg.get_variable(config[CONF_STMPE610_ID])
    cg.add(var.set_parent(parent))
    cg.add(var.set_pin(config[CONF_PIN]))
