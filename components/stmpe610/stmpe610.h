#pragma once

#include "esphome/components/spi/spi.h"
#include "esphome/components/touchscreen/touchscreen.h"
#include "esphome/core/component.h"
#include "esphome/core/hal.h"

namespace esphome::stmpe610 {

using namespace touchscreen;

/// ST STMPE610 resistive touch controller on SPI.
///
/// Register protocol (SPI): a read is one byte of (0x80 | reg) followed by one
/// data byte; a write is (reg, value). Multi-byte reads of the FIFO return bad
/// data (noted in Espressif's driver), so every register is read on its own.
/// Mode and clock come from YAML (default mode 1, 1 MHz).
class STMPE610Component final : public Touchscreen,
                                public spi::SPIDevice<spi::BIT_ORDER_MSB_FIRST, spi::CLOCK_POLARITY_LOW,
                                                      spi::CLOCK_PHASE_TRAILING, spi::DATA_RATE_1MHZ> {
 public:
  void set_threshold(uint8_t threshold) { this->threshold_ = threshold; }
  void set_irq_pin(InternalGPIOPin *pin) { this->irq_pin_ = pin; }

  void setup() override;
  void dump_config() override;

  /// Drive one of the controller's spare GPIOs (0-3). Safe to call before
  /// setup(); the state is applied once the chip has been initialised.
  void write_gpio(uint8_t pin, bool value);

 protected:
  void update_touches() override;

  bool init_chip_();
  void apply_gpio_();
  uint16_t read_chip_id_();
  uint8_t read_reg_(uint8_t reg);
  void write_reg_(uint8_t reg, uint8_t value);

  InternalGPIOPin *irq_pin_{nullptr};
  uint8_t threshold_{0};

  uint8_t gpio_mask_{0};   // pins claimed as outputs
  uint8_t gpio_state_{0};  // desired levels
  bool chip_ready_{false};

  uint16_t chip_id_{0};
  uint8_t chip_ver_{0};

  // Last good sample, reported again when the panel is still pressed but the
  // FIFO has no new data yet (avoids a spurious release between samples).
  bool have_last_{false};
  int16_t last_x_{0}, last_y_{0}, last_z_{0};
};

}  // namespace esphome::stmpe610
