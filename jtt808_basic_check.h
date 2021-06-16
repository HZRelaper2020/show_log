#ifndef _JTT808_BASIC_CHECK__H
#define _JTT808_BASIC_CHECK__H

#include "jtt808_common.h"

uint8_t Jtt808GetCheckSum(uint8_t* data,int size);

jtt808err_t Jtt808BasicCheckSendRecv(jtt808header_t* sendheader,uint8_t* recvbuf,int recvlen);

#endif


