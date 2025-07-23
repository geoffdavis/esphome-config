import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.const import CONF_ID

CONF_N_PIXELS = 'n_pixels'
CONF_SENSITIVITY = 'sensitivity'

esphome_music_leds_ns = cg.esphome_ns.namespace('esphome_music_leds')
MusicLeds = esphome_music_leds_ns.class_('MusicLeds', cg.Component)

CONFIG_SCHEMA = cv.COMPONENT_SCHEMA.extend({
    cv.GenerateID(): cv.declare_id(MusicLeds),
    cv.Required(CONF_N_PIXELS): cv.positive_int,
    cv.Optional(CONF_SENSITIVITY, default=0.0025): cv.float_,
})

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID], config[CONF_N_PIXELS], config[CONF_SENSITIVITY])
    await cg.register_component(var, config)
