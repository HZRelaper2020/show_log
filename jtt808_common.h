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

// for test
#define JTT808_TEST_IP "192.168.5.7"
#define JTT808_TEST_PORT 5555
// for debug
#define ERROR(arg) do{printf arg ;printf("\n");}while(0);
#define PRINT(arg) printf arg
#define JTT808_DEBUG_SEND_MSG 1

//#define BIGENDIAN
//#define ARMGCC   // for arm

#define JTT808_CHECK_RECV_CHECKSUM 1

#define MAX_JTT808_SEND_RETRY_TIMES 3
#define MAX_JTT808_RECV_RETRY_TIMES 3
#define MAX_JTT808_SEND_POLL_TIME 1000 // ms
#define MAX_JTT808_RECV_POLL_TIME 1000 // ms


#define JTT808_MSGID_REGISTER 0x100 



typedef enum jtt808error_t{
	JTT808_ERROR_OK = 0,
	JTT808_ERROR_POLL_RECV,
	JTT808_ERROR_POLL_RECV_TIMEO,
	JTT808_ERROR_RECV,
}jtt808error_t;


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

	int (*send)(struct jtt808handle* handle,uint8_t* data,int size);
	int (*recv)(struct jtt808handle* handle,uint8_t* data,int size);

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


static inline void jtt808_print_data(uint8_t* data,uint16_t size)
{
        for (int i=0;i<size;i++){
                PRINT(("%02x ",data[i]));
                if (i%16 == 15) PRINT(("\n"));
        }
}
#endif
