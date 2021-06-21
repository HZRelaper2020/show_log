#ifndef  JTT808_COMMON__H
#define  JTT808_COMMON__H
#define ARMGCC 1
#if ARMGCC
#define NET_CYCLONE 1
#define NET_LWIP 1
#endif

#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include <stdlib.h>
#include <unistd.h>
#if ARMGCC
#if NET_CYCLONE
#include "core/bsd_socket.h"
#include "core/net.h"
#endif
#else
#include <arpa/inet.h>
#include <poll.h>
#include <errno.h>
#endif
#include <sys/types.h>
#include <unistd.h>
#include <signal.h>

// for test
#define JTT808_TEST_IP "192.168.5.7"
#define JTT808_TEST_PORT 8837 
// for debug
#define ERROR(arg) do{printf arg ;printf("\n");}while(0)
#define PRINT(arg) printf arg

//#define BIGENDIAN
//#define ARMGCC   // for arm

#define JTT808_CHECK_RECV_CHECKSUM 			1  // if do checksum when receive
#define JTT808_DO_SEND_CHECKSUM 			1 // if do checksum when send data
#define JTT808_AUTO_SET_FLOWID				1 // if auto set flowid in send packet

#define MAX_JTT808_SEND_RETRY_TIMES 			3
#define MAX_JTT808_RECV_RETRY_TIMES 			3
#define MAX_JTT808_SEND_POLL_TIME 			1000 // ms
#define MAX_JTT808_RECV_POLL_TIME 			1000 // ms


#define JTT808_MSGID_REGISTER 			0x0100 
#define JTT808_MSGID_SEND_HEARTPKG		0x0002 
#define JTT808_MSGID_SEND_POSITION		0x0200
#define JTT808_MSGID_SEND_ACCELRATION_A1	0xE001
#define JTT808_MSGID_SEND_ACCELRATION_C1	0xE002


#pragma pack(1)

typedef enum jtt808Err{
	err_ok = 0,
	err_send_failed,
	err_recv_failed,
	err_exceed_max_recvlen,
	err_convert_header,
	err_msg_body_not_matched,
	
	err_not_supported_send_msgid,

	err_msg_id_not_matched = 1000,
	err_flowid_not_matched,
	err_register_car_already_registered,
	err_register_no_such_car,
	err_register_terminal_already_registered,
	err_register_database_no_such_terminal,
	err_register_unsupported_code,

	err_commonreply_failed = 1100,
	err_commonreply_msgwrong,
	err_commonreply_nosupported,
	err_commonreply_inprocess,
	err_commonreply_unsupportedcode,

	err_unknow,
} jtt808err_t;



typedef struct jtt808MsgBodyProperty{
	union {
		struct{
#if BIGENDIAN
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
		} attr;
		uint16_t value;
	};
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
        uint8_t len;
        uint8_t payload[200];
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

typedef struct jtt808register{
	uint16_t provinceId;
	uint16_t cityId;
	uint8_t manuafacturerId[11];
	uint8_t terminalType[30];
	uint8_t terminalId[30];
	uint8_t plateColor;
	uint8_t plateNumber[30];
}jtt808register_t;

typedef struct jtt808position{
	uint32_t alarmFlag;
	uint32_t status;
	uint32_t latitude;
	uint32_t longitude;
	uint16_t altitude;
	uint16_t speed;
	uint16_t direction;
	uint8_t time[6];
}jtt808position_t;

typedef struct jtt808accelerationA1{
	uint16_t eventType;
	uint16_t timestamp;
        uint8_t time[6]; // year,month,day,hour,minutes,second
	uint16_t millisecond;
        uint8_t resolution;
        char x;
        char y;
        char z;
}jtt808accelerationA1_t;

typedef struct jtt808accelerationC1{
	uint16_t eventType;
	uint8_t time[6];
	uint16_t millisecond;
	uint16_t temp;
	float pitch;
	float roll;
	float yaw;
	uint16_t aacx;
	uint16_t aacy;
	uint16_t aacz;
	uint16_t gyrox;
	uint16_t gyroy;
	uint16_t gyroz;
}jtt808accelerationC1_t;

#pragma pack()

static inline void jtt808_print_data(uint8_t* data,uint16_t size)
{
	const uint8_t PrintMethod =2;
	if (PrintMethod == 1){
		for (int i=0;i<size;i++){
			PRINT(("0x%02x ",data[i]));
                if (i%16 == 15) PRINT(("\n"));
		}
	}else if (PrintMethod ==2){
		for (int i=0;i<size;i++){
			PRINT(("0x%02x,",data[i]));
		} PRINT(("\n"));
	}
}

static inline void jtt808_print_header(jtt808header_t* header)
{
	PRINT(("header struct\n"));
	PRINT(("msgId:0x%04x\n",header->msgId));
	PRINT(("msgProperty:0x%04x\n",header->msgBodyProperty.value));
	PRINT(("mobile:"));
        for (int i=0;i<10;i++){
		PRINT(("%d%d",header->terminalMobile[i]>>4,header->terminalMobile[i]&0xf));
	} PRINT(("\n"));

	PRINT(("flowId:0x%04x\n",header->flowId));
	if (header->msgBodyProperty.attr.hasSubPkg){
		PRINT(("pkgCount:%d pkgNumber:%d\n",header->msgPkgItem.pkgCount,header->msgPkgItem.pkgNumber ));
	}
}

#endif
