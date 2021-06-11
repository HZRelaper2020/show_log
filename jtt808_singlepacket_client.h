#ifndef __JTT808_SINGLEPACKET_CLIENT__H
#define __JTT808_SINGLEPACKET_CLIENT__H

#include "jtt808_common.h"

int Jtt808RecvOnePacket(jtt808handle_t* handle,uint8_t* msg,int* msgLen);

int Jtt808InitHandle(jtt808handle_t* handle);

int Jtt808SendPacket(jtt808handle_t* handle,jtt808header_t* argheader,uint8_t* payload,const int payloadSize);

#endif
