# stmpe610

ESPHome external component for the ST STMPE610 resistive touch controller on SPI, built on ESPHome's
`touchscreen` base (structured like the built-in `xpt2046` driver). Written for the original Adafruit PiTFT 2.8"
resistive (product 1601); see `desk-panel.yaml`.

## Platforms

```yaml
external_components:
  - source:
      type: local
      path: components
    components: [stmpe610]

touchscreen:
  - platform: stmpe610
    id: touch
    display: tft
    cs_pin: GPIO17
    interrupt_pin: GPIO27   # optional; without it the chip is polled every update_interval (50ms)
    threshold: 0            # optional; minimum Z (0-255) for a touch to count
    spi_mode: MODE1         # optional; default MODE1 at 1MHz (data_rate)
    calibration:            # required
      x_min: 150
      x_max: 3800
      y_min: 150
      y_max: 3800

output:
  - platform: stmpe610
    id: backlight_gpio
    stmpe610_id: touch
    pin: 2                  # STMPE610 GPIO 0-3; GPIO2 is the PiTFT backlight
```

Wrap the output in a `light: platform: binary` (or `switch: platform: output`) to control it.

## How it talks to the chip

- Register reads are `0x80 | reg` followed by one data byte; writes are `reg, value`. The FIFO (`0x57`) is read one
  byte at a time, four bytes per sample, because multi-byte FIFO reads return bad data (noted in Espressif's
  `esp_lcd_touch_stmpe610`).
- Setup checks the chip ID (`0x0811`). If it doesn't match in the configured SPI mode, it retries once in the other
  mode (0 <-> 1), as `Adafruit_STMPE610::begin()` does. Espressif's driver uses mode 1; Adafruit's starts in mode 0.
- Init values follow Adafruit's and Espressif's drivers: 4-sample averaging, 1 ms touch delay, 5 ms settle, FIFO
  threshold 1, 50 mA drive. Interrupts are enabled for touch-detect and FIFO-threshold, falling edge, like the Linux
  `pitft28-resistive` overlay.
- Each update drains the FIFO and averages the samples. While `TSC_CTRL` reports the panel pressed, the last good
  point is repeated between samples, and with an IRQ pin the component keeps polling every loop until release.
- GPIO outputs set the pin's bit in `GPIO_ALT_FUNCT` (GPIO function), the level, then `GPIO_DIR`. The state is
  cached and re-applied after the chip's soft reset in setup.

Not yet checked on hardware: the `GPIO_ALT_FUNCT` polarity (1 = GPIO, from memory of the Linux `stmpe` MFD driver;
neither Adafruit's nor Espressif's touch driver touches the GPIO block), and which way Z moves with pressure. If the
backlight doesn't respond, try clearing the bit instead; if `threshold` rejects firm presses, the scale is inverted.

## Calibrating x_min / x_max / y_min / y_max

The calibration maps raw 12-bit ADC readings (0-4095) onto the display. The starting values (150-3800 on both axes)
are the range Espressif's `esp_lcd_touch_stmpe610` hard-codes; every panel differs a little.

1. Flash with the placeholder calibration and `logger: level: VERBOSE` (or add `logs: {stmpe610: VERBOSE}`).
2. Watch the log (`esphome logs desk-panel.yaml`). Every touch prints `Raw x=… y=… z=…`.
3. With a stylus, press each edge of the visible area: left, right, top, bottom. Note the raw values.
   Press firmly at the very edge; the extremes are what matter.
4. Set `x_min`/`x_max` to the smallest/largest raw X you saw, and the same for Y. `min` must be less than `max`.
   Calibration is in the panel's native (portrait, 240x320) frame: LVGL's `rotation: 90` rotates the touch points
   along with the drawing, so don't swap them for landscape.
5. If a touch lands mirrored, set `transform: mirror_x` / `mirror_y`; if horizontal motion moves the point
   vertically, set `transform: swap_xy`. Don't reverse min and max to mirror; ESPHome rejects that.
6. Turn the log level back down.

To check it, put a small widget in each corner and tap it with the stylus, or log the mapped coordinates with
`touchscreen: on_touch: - logger.log: format: "x=%d y=%d" args: [touch.x, touch.y]`.

`threshold` (minimum Z) is 0, which accepts every sample. If light brushes or a resting palm register, raise it to
just under the Z you see for a deliberate stylus press.
