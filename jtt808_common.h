#ifndef  JTT808_COMMON__H
#define  JTT808_COMMON__H

#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <errno.h>
#include <unistd.h>
#include <time.h>
#include <signal.h>
#include <poll.h>

// for debug
#define ERROR(arg) printf arg
#define PRINTF printf

//#define BIGENDIAN
//#define ARMGCC   // for arm

#define MAX_JTT808_SEND_RETRY_TIMES 3
#define MAX_JTT808_RECV_RETRY_TIMES 3
#define MAX_JTT808_SEND_POLL_TIME 1000 // ms
#define MAX_JTT808_RECV_POLL_TIME 1000 // ms


#define JTT808_MSGID_REGISTER 0x100 

typedef struct jtt808MsgBodyProperty{
#ifdef BIGENDIAN
        uint16_t reserved:1;
        uint16_t versionIdentify:1;
        uint16_t hasSubPkg:1;
        uint16_t encodeType:3;  // 10 bit 1:RSA
        uint16_t msgLength:10; // msg length
#else
        uint16_t msgLength:10; // msg length
        uint16_t encodeType:3;  // 10 bit 1:RSA
        uint16_t hasSubPkg:1;
        uint16_t versionIdentify:1; //set 1
        uint16_t reserved:1;
#endif
}jtt808MsgBodyProperty_t;

typedef struct jtt808MsgPkgItem{
        uint16_t pkgCount;
        uint16_t pkgNumber; // start with 1
}jtt808MsgPkgItem_t;

typedef struct jtt808header{
        uint16_t msgId;
        jtt808MsgBodyProperty_t msgBodyProperty;
        uint8_t protocolVersion;
        uint8_t terminalMobile[10]; // BCD code
        uint16_t flowId;
        jtt808MsgPkgItem_t msgPkgItem; // may not have this
	uint8_t reserved[20];// reserved for 0x7e and 0x7d translation
}jtt808header_t;

typedef struct jtt808{
        uint8_t identify; // 0x7e
        jtt808header_t header;
        uint8_t* body;
        uint8_t checkcode[2]; // may be 0x7e so need to bytes

}jtt808_t;

typedef struct jtt808authorToken{
        uint8_t payload[200];
        uint8_t len;
}jtt808authorToken_t;

typedef struct jtt808handle{
        int sk;
	int pollRecvTime; // ms
	int pollSendTime; // ms
        jtt808authorToken_t token;

	uint16_t maxSendRetryTimes;
	uint16_t maxRecvRetryTimes;
}jtt808handle_t;

typedef struct jtt808Register{
	uint16_t provinceId;
	uint16_t cityId;
	uint8_t manufacturerId[11];
	uint8_t terminalType[30];
	uint8_t terminalId[30];
	uint8_t carColor;
	uint8_t carPlate[100];
	uint16_t totLen;
}jtt808Register_t;

typedef struct jtt808CommonReply{
	uint16_t flowId;
	uint8_t result;
	uint8_t* authorCode;
}jtt808CommonReply_t;
#endif
