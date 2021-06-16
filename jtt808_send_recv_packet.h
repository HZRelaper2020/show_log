#ifndef _JTT808_SEND_RECV_PACKET__H
#define _JTT808_SEND_RECV_PACKET__H

#include "jtt808_common.h"

int Jtt808RecvOnePacket(jtt808handle_t* handle,uint8_t* msg,int* msgLen,int maxlen);

int Jtt808InitHandle(jtt808handle_t* handle);

int Jtt808SendPacket(jtt808handle_t* handle,jtt808header_t* argheader,uint8_t* payload,const int payloadSize);

#endif
