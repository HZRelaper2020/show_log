#ifndef __JTT808_SINGLEPACKET_CLIENT__H
#define __JTT808_SINGLEPACKET_CLIENT__H

#include "jtt808_common.h"

int Jtt808RecvOnePacket(jtt808handle_t* handle,uint8_t* msg,int* msgLen);

#endif
