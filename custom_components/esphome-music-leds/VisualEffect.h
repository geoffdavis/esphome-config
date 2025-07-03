/*
 * Transfer from Mel-Frequency to Leds Effect
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 */

#pragma once
#include <FastLED.h>
#include <cmath>
#include "ExpFilter.h"
#include "gaussian_filter1d.h"

class VisualEffect{
    private:
      class ExpFilter *_gain, *_p_filt_r, *_p_filt_g, *_p_filt_b, *_common_mode, *_r_filt, *_g_filt, *_b_filt;
      class gaussian_filter1d *_gauss02, *_gauss40;
      uint8_t *_leds[3];
      uint16_t _mel_num, _leds_num;
      void mirror(CRGB * physic_leds);
      float * _spectrum, * _prev_spectrum;
    public:
        VisualEffect(uint16_t mel_num, uint16_t leds_num);
        void visualize_scroll(float * mel_data, CRGB * physic_leds);
        void visualize_energy(float * mel_data, CRGB * physic_leds);
        void visualize_spectrum(float * mel_data, CRGB * physic_leds);
        ~VisualEffect();
};


