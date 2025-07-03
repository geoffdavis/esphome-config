/*
 * Gaussian Filter 1 dimension
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 */

#pragma once
#include <cmath>
#include <cstdint>

class gaussian_filter1d{
    private:
        float *_gaussian_kernel1d;
        int radius;
    public:
        gaussian_filter1d(float sigma);
        ~gaussian_filter1d();
        void process(float * data, int num);
        void process(uint8_t * data, int num);
};

