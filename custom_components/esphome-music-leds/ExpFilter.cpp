#include "ExpFilter.h"

ExpFilter::ExpFilter(float *val, int val_len, float alpha_decay, float alpha_rise){
    m_val_len = val_len;
    m_alpha_decay = alpha_decay;
    m_alpha_rise = alpha_rise;

    m_val = new float[val_len];
    for(int i=0; i<m_val_len; i++)
        m_val[i] = val[i];
}

ExpFilter::ExpFilter(int val_len, float alpha_decay, float alpha_rise){
    m_val_len = val_len;
    m_alpha_decay = alpha_decay;
    m_alpha_rise = alpha_rise;

    m_val = new float[val_len];
    for(int i=0; i<m_val_len; i++)
        m_val[i] = 0.0;
}

ExpFilter::~ExpFilter(){
    delete[] m_val;
}

float * ExpFilter::value(){
  return m_val;
}

void ExpFilter::update0(float * data){
    for(int i=0; i<m_val_len; i++){
        if (data[i]>m_val[i])
            m_val[i] = data[i]*m_alpha_rise + m_val[i]*(1.0-m_alpha_rise);
        else
            m_val[i] = data[i]*m_alpha_decay + m_val[i]*(1.0-m_alpha_decay);
    }
}

void ExpFilter::update(float * data){
    for(int i=0; i<m_val_len; i++){
        if (data[i]>m_val[i])
            m_val[i] = data[i]*m_alpha_rise + m_val[i]*(1.0-m_alpha_rise);
        else
            m_val[i] = data[i]*m_alpha_decay + m_val[i]*(1.0-m_alpha_decay);
        data[i] = m_val[i];
    }
}

void ExpFilter::update(uint8_t * data){
    for(int i=0; i<m_val_len; i++){
        if (data[i]>m_val[i])
            m_val[i] = data[i]*m_alpha_rise + m_val[i]*(1.0-m_alpha_rise);
        else
            m_val[i] = data[i]*m_alpha_decay + m_val[i]*(1.0-m_alpha_decay);
        data[i] = m_val[i];
    }
}
