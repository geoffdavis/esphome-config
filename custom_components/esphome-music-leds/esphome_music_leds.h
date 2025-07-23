#pragma once

#include "esphome/core/component.h"
#include "esphome/components/light/addressable_light.h"
#include "driver/i2s.h"
#include <FastLED.h>
#include "FFT.h"
#include "VisualEffect.h"

namespace esphome {
namespace esphome_music_leds {

enum PLAYMODE {MODE_SCROLL, MODE_ENERGY, MODE_SPECTRUM};

static const char* TAG = "MusicLeds";

class MusicLeds : public Component {
    private:
        //N_PIXELS: The number of the LEDS on the led strip, must be even.
        static const uint16_t DEFAULT_N_PIXELS = 60;
        //MIN_VOLUME_THRESHOLD: If the audio's volume is less than this number, the signal will not be processed.
        static constexpr float DEFAULT_MIN_VOLUME_THRESHOLD = 0.0003;
        //Microphone(type of PDM)'s WS Pin and DATA_IN Pin, connecting to GPIO
        static const int DEFAULT_PDM_WS_IO_PIN = 19;
        static const int DEFAULT_PDM_DATA_IN_PIN = 22;

        static const uint16_t BUFFER_SIZE = 512;
        static const uint8_t N_ROLLING_HISTORY = 2;
        static const uint16_t SAMPLE_RATE = 16000;
        static const uint16_t N_MEL_BIN = 18;
        static constexpr float MIN_FREQUENCY = 200;
        static constexpr float MAX_FREQUENCY = 8000;
        static const i2s_port_t MLED_I2S_NUM = I2S_NUM_0;

        float y_data[BUFFER_SIZE * N_ROLLING_HISTORY]{};
        class FFT *fft{nullptr};
        class VisualEffect *effect{nullptr};

        CRGB *physic_leds{nullptr};

        uint16_t n_pixels_; // init in constructor
        i2s_config_t i2s_config = {
          .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX | I2S_MODE_PDM),
          .sample_rate = SAMPLE_RATE,
          .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
          .channel_format = I2S_CHANNEL_FMT_ONLY_RIGHT,
          .communication_format = I2S_COMM_FORMAT_STAND_MSB,

          .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1, // high interrupt priority
          .dma_buf_count = 32,
          .dma_buf_len = 32
        };

        i2s_pin_config_t pin_config = {
          //.bck_io_num = 18,
          .bck_io_num = -1,
          .ws_io_num = DEFAULT_PDM_WS_IO_PIN,
          .data_out_num = -1,
          .data_in_num = DEFAULT_PDM_DATA_IN_PIN
        };

    public:
        /**
         * MusicLeds Constructor
         *
         * Args:
         * n_pixels - the number of LEDs on the strip. Must be an even number.
         * min_volume_threshold - ignore sounds below this level
         * pdm_ws_io_pin - I2S bus pin for the WS line of the PDM mic
         * pdm_data_in_pin - I2S bun pin for the DATA line of the PDM mic
         *
         */
        MusicLeds(
                uint16_t n_pixels=DEFAULT_N_PIXELS,
                float min_volume_threshold = DEFAULT_MIN_VOLUME_THRESHOLD,
                int pdm_ws_io_pin = DEFAULT_PDM_WS_IO_PIN,
                int pdm_data_in_pin = DEFAULT_PDM_DATA_IN_PIN
        );
        ~MusicLeds();
        void setup() override;
        void ShowFrame( PLAYMODE CurrentMode, light::AddressableLight *p_it);
};

} //namespace esphome_music_leds
} //namespace esphome
