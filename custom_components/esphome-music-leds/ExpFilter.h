/*
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 */

#pragma once
#include <stdint.h>
using namespace std;

class ExpFilter{
    private:
        float *m_val;
        float m_alpha_decay, m_alpha_rise;
        int m_val_len;
    public:
        ExpFilter(float *val, int val_len, float alpha_decay, float alpha_rise);
        ExpFilter(int val_len, float alpha_decay, float alpha_rise);
        ~ExpFilter();
        void update(float * data);
        void update(uint8_t * data);
        void update0(float * data);
        float * value();
};
