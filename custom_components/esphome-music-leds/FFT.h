/*
 * Fast Fourier Transformation/Mel-Frequency
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 */

#pragma once
#include <cmath>
#include <cstdlib>
#include <cstring>
#include <algorithm>
#include <stdio.h>
#include "ExpFilter.h"

class FFT{
    private:
        float* _hammer=NULL;
        uint16_t _num_mel_bands, _num_samples, _sample_rate;
        float _min_frequency, _max_frequency, _min_volume_threshold;
        float * _y_data_cal;
        float** _melmat=NULL;
        float hz2mel(float f);
        float mel2hz(float m);
        void compute_hammer();
        void compute_melmat(uint16_t num_mel_bands, float freq_min, float freq_max, uint16_t num_fft_bands, uint16_t sample_rate);
        class ExpFilter * _mel_gain, * _mel_smoothing;

    public:
        FFT(uint16_t samples, uint16_t n_mel_bin, float min_frequency, float max_frequency, uint16_t sample_rate, float min_volume_threshold);
        ~FFT();
        void fft(float * real, float * imag);
        void fft(float * real);
        void abs(float * real, float * imag);
        void hamming(float *real);
        void t2mel(float * y_data, float * mel_data);
};


