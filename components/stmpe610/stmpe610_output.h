#pragma once

#include "esphome/core/defines.h"
#ifdef USE_OUTPUT

#include "esphome/components/output/binary_output.h"
#include "stmpe610.h"

namespace esphome::stmpe610 {

/// One of the STMPE610's spare GPIOs as a binary output. On the original
/// Adafruit PiTFT 2.8" resistive, GPIO2 switches the backlight.
class STMPE610GPIOOutput : public output::BinaryOutput {
 public:
  void set_parent(STMPE610Component *parent) { this->parent_ = parent; }
  void set_pin(uint8_t pin) { this->pin_ = pin; }

 protected:
  void write_state(bool state) override { this->parent_->write_gpio(this->pin_, state); }

  STMPE610Component *parent_{nullptr};
  uint8_t pin_{2};
};

}  // namespace esphome::stmpe610

#endif  // USE_OUTPUT
