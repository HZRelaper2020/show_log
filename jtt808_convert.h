#ifndef  _JTT808_CONVERT__H
#define  _JTT808_CONVERT__H

#include "jtt808_common.h"

int Jtt808ConvertRawDataToHeader(uint8_t* data,int size,jtt808header_t* header);

int Jtt808ConvertHeaderToRawData(jtt808header_t* header,uint8_t* outbuf,int* outsize);

int Jtt808Encode0x7eAnd0x7d(uint8_t* inbuf,int insize,uint8_t* outbuf,int* outsize);

int Jtt808Decode0x7d01And0x7d02(uint8_t* inbuf,int insize,uint8_t* outbuf,int* outsize);


// convert action to raw data
int Jtt808ConvertReigstStructToRawData(jtt808register_t* regist,uint8_t* outbuf,int* outsize);

int Jtt808ConvertPositionStructToRawData(jtt808position_t* pos,uint8_t* outbuf,int* outsize);

int Jtt8080GetRawDataBodyIndex(uint8_t* rawbuf,int rawlen);

int Jtt808ConvertStructToRawData(uint8_t* stct,int stctsize,uint8_t* outbuf,int* outsize);

#endif
