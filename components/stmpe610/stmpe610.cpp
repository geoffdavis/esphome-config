#include "stmpe610.h"

#include "esphome/core/log.h"

namespace esphome::stmpe610 {

static const char *const TAG = "stmpe610";

// Register map (STMPE610/STMPE811 datasheet; same addresses as Espressif's
// esp_lcd_touch_stmpe610 and Adafruit_STMPE610).
static constexpr uint8_t REG_CHIP_ID = 0x00;  // 16-bit, 0x0811
static constexpr uint8_t REG_ID_VER = 0x02;
static constexpr uint8_t REG_SYS_CTRL1 = 0x03;
static constexpr uint8_t REG_SYS_CTRL2 = 0x04;
static constexpr uint8_t REG_INT_CTRL = 0x09;
static constexpr uint8_t REG_INT_EN = 0x0A;
static constexpr uint8_t REG_INT_STA = 0x0B;
static constexpr uint8_t REG_GPIO_SET_PIN = 0x10;
static constexpr uint8_t REG_GPIO_CLR_PIN = 0x11;
static constexpr uint8_t REG_GPIO_DIR = 0x13;
static constexpr uint8_t REG_GPIO_ALT_FUNCT = 0x17;
static constexpr uint8_t REG_ADC_CTRL1 = 0x20;
static constexpr uint8_t REG_ADC_CTRL2 = 0x21;
static constexpr uint8_t REG_TSC_CTRL = 0x40;
static constexpr uint8_t REG_TSC_CFG = 0x41;
static constexpr uint8_t REG_FIFO_TH = 0x4A;
static constexpr uint8_t REG_FIFO_STA = 0x4B;
static constexpr uint8_t REG_FIFO_SIZE = 0x4C;
static constexpr uint8_t REG_TSC_FRACTION_Z = 0x56;
static constexpr uint8_t REG_TSC_DATA = 0x57;  // non-incrementing FIFO read
static constexpr uint8_t REG_TSC_I_DRIVE = 0x58;

static constexpr uint16_t CHIP_ID = 0x0811;

static constexpr uint8_t SYS_CTRL1_RESET = 0x02;
static constexpr uint8_t TSC_CTRL_EN = 0x01;         // enable, XYZ acquisition
static constexpr uint8_t TSC_CTRL_TOUCHED = 0x80;    // TOUCH_DET status
static constexpr uint8_t INT_EN_TOUCH_DET = 0x01;
static constexpr uint8_t INT_EN_FIFO_TH = 0x02;
static constexpr uint8_t INT_CTRL_ENABLE = 0x01;
static constexpr uint8_t INT_CTRL_EDGE = 0x02;       // polarity bit (0x04) left clear: falling edge
static constexpr uint8_t FIFO_STA_RESET = 0x01;
static constexpr uint8_t FIFO_STA_EMPTY = 0x20;

void STMPE610Component::setup() {
  this->spi_setup();

  if (!this->init_chip_()) {
    this->mark_failed();
    return;
  }

  if (this->irq_pin_ != nullptr) {
    // INT is driven low on touch-detect and FIFO-threshold events (falling
    // edge, as in the Linux pitft28-resistive overlay). While the panel stays
    // pressed update_touches() keeps the loop polling, so missed edges only
    // delay the first sample.
    this->irq_pin_->pin_mode(gpio::FLAG_INPUT | gpio::FLAG_PULLUP);
    this->irq_pin_->setup();
    this->attach_interrupt_(this->irq_pin_, gpio::INTERRUPT_FALLING_EDGE);
  }
}

bool STMPE610Component::init_chip_() {
  this->chip_id_ = this->read_chip_id_();
  if (this->chip_id_ != CHIP_ID) {
    // Adafruit_STMPE610 tries mode 0 and falls back to mode 1; Espressif uses
    // mode 1. Try the other mode once before giving up.
    spi::SPIMode other = this->mode_ == spi::MODE1 ? spi::MODE0 : spi::MODE1;
    ESP_LOGW(TAG, "Chip ID 0x%04X in SPI mode %u, retrying in mode %u", this->chip_id_, (unsigned) this->mode_,
             (unsigned) other);
    this->spi_teardown();
    this->set_mode(other);
    this->spi_setup();
    this->chip_id_ = this->read_chip_id_();
    if (this->chip_id_ != CHIP_ID) {
      ESP_LOGE(TAG, "STMPE610 not found (chip ID 0x%04X, expected 0x%04X). Check wiring and CS.", this->chip_id_,
               CHIP_ID);
      return false;
    }
  }
  this->chip_ver_ = this->read_reg_(REG_ID_VER);

  this->write_reg_(REG_SYS_CTRL1, SYS_CTRL1_RESET);  // soft reset
  delay(10);
  this->write_reg_(REG_SYS_CTRL2, 0x00);  // clocks on: ADC, TSC, GPIO, temp
  this->write_reg_(REG_TSC_CTRL, TSC_CTRL_EN);
  this->write_reg_(REG_INT_EN, INT_EN_TOUCH_DET | INT_EN_FIFO_TH);
  this->write_reg_(REG_ADC_CTRL1, 0x60);       // 96-clock sample time (as Adafruit/Espressif)
  this->write_reg_(REG_ADC_CTRL2, 0x02);       // ADC clock 6.5 MHz
  this->write_reg_(REG_TSC_CFG, 0xA4);         // 4-sample average, 1 ms touch delay, 5 ms settle
  this->write_reg_(REG_TSC_FRACTION_Z, 0x06);  // Z: 6 fractional bits
  this->write_reg_(REG_FIFO_TH, 0x01);
  this->write_reg_(REG_FIFO_STA, FIFO_STA_RESET);
  this->write_reg_(REG_FIFO_STA, 0x00);
  this->write_reg_(REG_TSC_I_DRIVE, 0x01);  // 50 mA panel drive
  this->write_reg_(REG_INT_STA, 0xFF);
  this->write_reg_(REG_INT_CTRL, INT_CTRL_EDGE | INT_CTRL_ENABLE);

  this->chip_ready_ = true;
  this->apply_gpio_();  // the soft reset cleared any GPIO setup
  return true;
}

void STMPE610Component::write_gpio(uint8_t pin, bool value) {
  uint8_t bit = 1 << pin;
  this->gpio_mask_ |= bit;
  if (value) {
    this->gpio_state_ |= bit;
  } else {
    this->gpio_state_ &= ~bit;
  }
  if (!this->chip_ready_)
    return;
  this->write_reg_(value ? REG_GPIO_SET_PIN : REG_GPIO_CLR_PIN, bit);
}

void STMPE610Component::apply_gpio_() {
  if (this->gpio_mask_ == 0)
    return;
  // On the STMPE811 family a 1 in GPIO_ALT_FUNCT selects the GPIO function
  // for that pin (the Linux stmpe-gpio driver sets it for GPIO, clears it for
  // the touchscreen/ADC block).
  this->write_reg_(REG_GPIO_ALT_FUNCT, this->read_reg_(REG_GPIO_ALT_FUNCT) | this->gpio_mask_);
  // Set the level before switching the pin to output, so it doesn't glitch.
  if (this->gpio_state_ & this->gpio_mask_)
    this->write_reg_(REG_GPIO_SET_PIN, this->gpio_state_ & this->gpio_mask_);
  if (~this->gpio_state_ & this->gpio_mask_)
    this->write_reg_(REG_GPIO_CLR_PIN, ~this->gpio_state_ & this->gpio_mask_);
  this->write_reg_(REG_GPIO_DIR, this->read_reg_(REG_GPIO_DIR) | this->gpio_mask_);
}

void STMPE610Component::update_touches() {
  bool touched = (this->read_reg_(REG_TSC_CTRL) & TSC_CTRL_TOUCHED) != 0;

  uint32_t sum_x = 0, sum_y = 0, sum_z = 0;
  uint8_t count = 0;
  if (!(this->read_reg_(REG_FIFO_STA) & FIFO_STA_EMPTY)) {
    uint8_t size = this->read_reg_(REG_FIFO_SIZE);
    for (uint8_t i = 0; i < size; i++) {
      uint8_t d[4];
      for (auto &b : d)
        b = this->read_reg_(REG_TSC_DATA);
      // 12-bit X, 12-bit Y, 8-bit Z packed into 4 bytes.
      sum_x += (uint16_t(d[0]) << 4) | (d[1] >> 4);
      sum_y += (uint16_t(d[1] & 0x0F) << 8) | d[2];
      sum_z += d[3];
      count++;
    }
  }
  // Drop anything left over and acknowledge all interrupts.
  this->write_reg_(REG_FIFO_STA, FIFO_STA_RESET);
  this->write_reg_(REG_FIFO_STA, 0x00);
  this->write_reg_(REG_INT_STA, 0xFF);

  if (!touched) {
    this->have_last_ = false;
    return;
  }

  if (count > 0) {
    int16_t x = sum_x / count, y = sum_y / count, z = sum_z / count;
    ESP_LOGV(TAG, "Raw x=%d y=%d z=%d (%u samples)", x, y, z, count);
    if (z < this->threshold_) {
      // Too light: treat as no touch, but keep polling while pressed.
      this->have_last_ = false;
    } else {
      this->last_x_ = x;
      this->last_y_ = y;
      this->last_z_ = z;
      this->have_last_ = true;
    }
  }
  if (this->have_last_)
    this->add_raw_touch_position_(0, this->last_x_, this->last_y_, this->last_z_);

  // With an interrupt pin the base class only calls us after an IRQ. Keep
  // polling every loop while the panel is pressed so drags and the release
  // are seen even if an edge is missed.
  if (this->irq_pin_ != nullptr)
    this->store_.touched = true;
}

void STMPE610Component::dump_config() {
  ESP_LOGCONFIG(TAG,
                "STMPE610:\n"
                "  Chip ID: 0x%04X, version: 0x%02X\n"
                "  SPI mode: %u\n"
                "  X min: %d, X max: %d\n"
                "  Y min: %d, Y max: %d\n"
                "  Swap X/Y: %s, Invert X: %s, Invert Y: %s\n"
                "  Threshold: %u\n"
                "  GPIO outputs: 0x%02X",
                this->chip_id_, this->chip_ver_, (unsigned) this->mode_, this->x_raw_min_, this->x_raw_max_,
                this->y_raw_min_, this->y_raw_max_, YESNO(this->swap_x_y_), YESNO(this->invert_x_),
                YESNO(this->invert_y_), this->threshold_, this->gpio_mask_);
  LOG_PIN("  CS Pin: ", this->cs_);
  LOG_PIN("  IRQ Pin: ", this->irq_pin_);
  LOG_UPDATE_INTERVAL(this);
  if (this->is_failed())
    ESP_LOGE(TAG, "  Not detected");
}

uint16_t STMPE610Component::read_chip_id_() {
  return (uint16_t(this->read_reg_(REG_CHIP_ID)) << 8) | this->read_reg_(REG_CHIP_ID + 1);
}

uint8_t STMPE610Component::read_reg_(uint8_t reg) {
  this->enable();
  this->write_byte(0x80 | reg);
  uint8_t value = this->read_byte();
  this->disable();
  return value;
}

void STMPE610Component::write_reg_(uint8_t reg, uint8_t value) {
  this->enable();
  this->write_byte(reg);
  this->write_byte(value);
  this->disable();
}

}  // namespace esphome::stmpe610
