#ifndef _JTT808_NETUTIL__H
#define  _JTT808_NETUTIL__H

#include "jtt808_common.h"

int Jtt808CreteSocket(jtt808handle_t* handle);

void Jtt808CloseSocket(jtt808handle_t* handle);

int Jtt808Connect(jtt808handle_t* handle,const uint8_t* ip,uint16_t port);

int Jtt808NetRecv(jtt808handle_t* handle,uint8_t* recvdata,int recvsize);

int Jtt808NetSend(jtt808handle_t* handle,uint8_t* senddata,int sendsize);

int Jtt808ClearNetRecvBuffer(jtt808handle_t* handle,int ptime);

#endif
