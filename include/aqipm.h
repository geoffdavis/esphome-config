/**
 * Calculate Air Quality Index from particulate counts at 2.5 and 10 microns.
 *
 * Algorithm borrowed from https://github.com/zefanja/aqi/blob/master/html/aqi.js
 */

#include <math.h>
#include <string>

static const float BIN_PM25[] {0, 0, 12, 35.4, 55.4, 150.4, 250.4, 350.4, 500.4};
static const float BIN_PM10[] {0, 0, 54, 154, 254, 135, 424, 504, 604};
static const float BIN_AQI[]  {0, 0, 50, 100, 150, 200, 300, 400, 500};

int calcAQIpm25(float pm25) {
    float aqipm25 = 0;

	if (pm25 >= BIN_PM25[1] && pm25 <= BIN_PM25[2]) {
		aqipm25 = ((BIN_AQI[2] - BIN_AQI[1]) / (BIN_PM25[2] - BIN_PM25[1])) * (pm25 - BIN_PM25[1]) + BIN_AQI[1];
	} else if (pm25 >= BIN_PM25[2] && pm25 <= BIN_PM25[3]) {
		aqipm25 = ((BIN_AQI[3] - BIN_AQI[2]) / (BIN_PM25[3] - BIN_PM25[2])) * (pm25 - BIN_PM25[2]) + BIN_AQI[2];
	} else if (pm25 >= BIN_PM25[3] && pm25 <= BIN_PM25[4]) {
		aqipm25 = ((BIN_AQI[4] - BIN_AQI[3]) / (BIN_PM25[4] - BIN_PM25[3])) * (pm25 - BIN_PM25[3]) + BIN_AQI[3];
	} else if (pm25 >= BIN_PM25[4] && pm25 <= BIN_PM25[5]) {
		aqipm25 = ((BIN_AQI[5] - BIN_AQI[4]) / (BIN_PM25[5] - BIN_PM25[4])) * (pm25 - BIN_PM25[4]) + BIN_AQI[4];
	} else if (pm25 >= BIN_PM25[5] && pm25 <= BIN_PM25[6]) {
		aqipm25 = ((BIN_AQI[6] - BIN_AQI[5]) / (BIN_PM25[6] - BIN_PM25[5])) * (pm25 - BIN_PM25[5]) + BIN_AQI[5];
	} else if (pm25 >= BIN_PM25[6] && pm25 <= BIN_PM25[7]) {
		aqipm25 = ((BIN_AQI[7] - BIN_AQI[6]) / (BIN_PM25[7] - BIN_PM25[6])) * (pm25 - BIN_PM25[6]) + BIN_AQI[6];
	} else if (pm25 >= BIN_PM25[7] && pm25 <= BIN_PM25[8]) {
		aqipm25 = ((BIN_AQI[8] - BIN_AQI[7]) / (BIN_PM25[8] - BIN_PM25[7])) * (pm25 - BIN_PM25[7]) + BIN_AQI[7];
	}
    return trunc(aqipm25);
}

int calcAQIpm10(float pm10) {
    float aqipm10 = 0;

    if (pm10 >= BIN_PM10[1] && pm10 <= BIN_PM10[2]) {
		aqipm10 = ((BIN_AQI[2] - BIN_AQI[1]) / (BIN_PM10[2] - BIN_PM10[1])) * (pm10 - BIN_PM10[1]) + BIN_AQI[1];
	} else if (pm10 >= BIN_PM10[2] && pm10 <= BIN_PM10[3]) {
		aqipm10 = ((BIN_AQI[3] - BIN_AQI[2]) / (BIN_PM10[3] - BIN_PM10[2])) * (pm10 - BIN_PM10[2]) + BIN_AQI[2];
	} else if (pm10 >= BIN_PM10[3] && pm10 <= BIN_PM10[4]) {
		aqipm10 = ((BIN_AQI[4] - BIN_AQI[3]) / (BIN_PM10[4] - BIN_PM10[3])) * (pm10 - BIN_PM10[3]) + BIN_AQI[3];
	} else if (pm10 >= BIN_PM10[4] && pm10 <= BIN_PM10[5]) {
		aqipm10 = ((BIN_AQI[5] - BIN_AQI[4]) / (BIN_PM10[5] - BIN_PM10[4])) * (pm10 - BIN_PM10[4]) + BIN_AQI[4];
	} else if (pm10 >= BIN_PM10[5] && pm10 <= BIN_PM10[6]) {
		aqipm10 = ((BIN_AQI[6] - BIN_AQI[5]) / (BIN_PM10[6] - BIN_PM10[5])) * (pm10 - BIN_PM10[5]) + BIN_AQI[5];
	} else if (pm10 >= BIN_PM10[6] && pm10 <= BIN_PM10[7]) {
		aqipm10 = ((BIN_AQI[7] - BIN_AQI[6]) / (BIN_PM10[7] - BIN_PM10[6])) * (pm10 - BIN_PM10[6]) + BIN_AQI[6];
	} else if (pm10 >= BIN_PM10[7] && pm10 <= BIN_PM10[8]) {
		aqipm10 = ((BIN_AQI[8] - BIN_AQI[7]) / (BIN_PM10[8] - BIN_PM10[7])) * (pm10 - BIN_PM10[7]) + BIN_AQI[7];
	}
    return trunc(aqipm10);
}