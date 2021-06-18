#include "jtt808_send_recv_packet.h"
#include "jtt808_convert.h"
#include "jtt808_netutil.h"
#include "jtt808_basic_check.h"
#include "jtt808_netutil.h"

typedef struct Jtt808SendAndRecv{
	jtt808handle_t* handle;

	// for send
	jtt808header_t* header;
	uint8_t* sendPayload;
	int sendPayloadSize;

	// for reply
	uint8_t* recvbuf;
	int recvlen;
	int maxRecvLen;
}Jtt808SendAndRecv_t;

#define DO_SEND_RECV_CHECK(argSendPayload,argSendPayloadSize,recvbuf,recvlen) do{ Jtt808SendAndRecv_t sr; memset(&sr,0,sizeof(sr)); sr.handle= handle; sr.header = header; sr.sendPayload= argSendPayload; sr.sendPayloadSize= argSendPayloadSize; sr.recvbuf = recvbuf; sr.maxRecvLen = sizeof(recvbuf); ret = Jtt808DoSendAndRecv(&sr); recvlen = sr.recvlen; if (ret == err_ok){ ret = Jtt808BasicCheckSendRecv(header,recvbuf,recvlen);};}while(0)

static jtt808err_t Jtt808DoSendAndRecv(Jtt808SendAndRecv_t* sr)
{
#if ARMGCC
	phtread_mutex_lock();
#endif
	jtt808err_t ret = err_ok;

	jtt808handle_t* handle = sr->handle;

	jtt808header_t* header = sr->header;
        uint8_t* sendPayload= sr->sendPayload;
        int sendPayloadSize = sr->sendPayloadSize;

	int recvlen =0;
	int maxRecvLen = sr->maxRecvLen;


	static uint8_t recvtemp[1514*2];


	const int pollSendTime = handle->pollSendTime;
	const int pollRecvTime = handle->pollRecvTime;
	const uint16_t maxSendRetryTimes = handle->maxSendRetryTimes;
	const uint16_t maxRecvRetryTimes = handle->maxRecvRetryTimes;
	uint16_t nowSendTimes = 0;
	uint16_t nowRecvTimes = 0;

	// auto set flowId
#if JTT808_AUTO_SET_FLOWID
	static uint16_t headerFlowId = 0;
	headerFlowId += 1;
	header->flowId = headerFlowId;
#endif

	ret = err_unknow;
	do{
		Jtt808ClearNetRecvBuffer(handle,1);

		while(Jtt808SendPacket(handle,header,sendPayload,sendPayloadSize) && nowSendTimes <=maxSendRetryTimes){
			ret = err_send_failed;
			nowSendTimes += 1;
			handle->pollSendTime = (nowSendTimes) * pollSendTime;
		}

		if (nowSendTimes <=maxSendRetryTimes){
			while (Jtt808RecvOnePacket(handle,recvtemp,&recvlen,sizeof(recvtemp)) && nowRecvTimes <= maxRecvRetryTimes){
				nowRecvTimes += 1;
				ret = err_recv_failed;
				handle->pollRecvTime = (nowRecvTimes) * pollRecvTime;
			}
		}

		if (nowSendTimes >maxSendRetryTimes || nowRecvTimes > maxRecvRetryTimes)
			break;

		if (recvlen < maxRecvLen){
			memcpy(sr->recvbuf,recvtemp,recvlen);
			sr->recvlen =recvlen; 
			ret = err_ok;
		}else{
			ret = err_exceed_max_recvlen;
		}

	}while(0);

	handle->pollRecvTime = pollRecvTime;
	handle->pollSendTime = pollSendTime;
#if ARMGCC
	phtread_mutex_unlock();
#endif
	return ret;
}
/*
 *
 *
 * registed by terminal ID
 *
 *
 */ 

jtt808err_t Jtt808DoActionRegister(jtt808handle_t* handle,jtt808header_t* header,jtt808register_t* regist)
{
	jtt808err_t ret = err_ok;
	uint8_t sendPayload[1514*2];
	uint8_t recvbuf[1514];
	int size = 0;
	int sendPayloadSize =0;
	const uint16_t flowId = header->flowId;
	int recvlen = 0;

	memset(recvbuf,0,sizeof(recvbuf));

	header->msgId = JTT808_MSGID_REGISTER;

	Jtt808ConvertReigstStructToRawData(regist,sendPayload,&sendPayloadSize);
	
	DO_SEND_RECV_CHECK(sendPayload,sendPayloadSize,recvbuf,recvlen);

	if (ret == err_ok){
		int bodyIndex = Jtt8080GetRawDataBodyIndex(recvbuf,recvlen);
		uint8_t value = recvbuf[bodyIndex + 2];
		if (value == 0){
			// ok,copy it
			memcpy((uint8_t*)&handle->token,recvbuf+bodyIndex+3,*(recvbuf+bodyIndex+3));
		} else if (value == 1){
			ret = err_register_car_already_registered;
		}else if (value == 2){
			ret = err_register_no_such_car;
		}else if (value == 3){
			ret = err_register_terminal_already_registered;
		}else if (value == 4){
			ret = err_register_database_no_such_terminal;
		}else{
			ret = err_register_unsupported_code;
		}
	}

	return ret;
}

jtt808err_t Jtt808DoActionSendHeartPacket(jtt808handle_t* handle,jtt808header_t* header)
{
	jtt808err_t ret = err_ok;
	header->msgId = JTT808_MSGID_SEND_HEARTPKG;

	uint8_t recvbuf[1514*2];
	int recvlen = 0;

	DO_SEND_RECV_CHECK(NULL,0,recvbuf,recvlen);

	if (ret == err_ok){
		int bodyIndex = Jtt8080GetRawDataBodyIndex(recvbuf,recvlen);
		uint8_t value = recvbuf[bodyIndex+4];
		if (value == 0){
			// ok
		}else if (value == 1){
			ret = err_commonreply_failed;
		}else if (value == 2){
			ret = err_commonreply_msgwrong;
		}else if (value == 3){
			ret = err_commonreply_nosupported;
		}else if (value == 4){
			ret = err_commonreply_inprocess;
		}else{
			ret = err_commonreply_unsupportedcode;
		}
	}


	return ret;
}

/*
 *
 * send position info
 *
 */
jtt808err_t Jtt808DoActionSendPosition(jtt808handle_t* handle,jtt808header_t* header,jtt808position_t* pos)
{
        jtt808err_t ret = err_ok;
	uint8_t sendPayload[1514*2];
	int sendPayloadSize = 0;
	uint8_t recvbuf[1514*2];
        int recvlen;

        header->msgId = JTT808_MSGID_SEND_POSITION;

	Jtt808ConvertPositionStructToRawData(pos,sendPayload,&sendPayloadSize);
        DO_SEND_RECV_CHECK(sendPayload,sendPayloadSize,recvbuf,recvlen);

        if (ret == err_ok){
                int bodyIndex = Jtt8080GetRawDataBodyIndex(recvbuf,recvlen);
                uint8_t value = recvbuf[bodyIndex+4];
                if (value == 0){
                        // ok
                }else if (value == 1){
                        ret = err_commonreply_failed;
                }else if (value == 2){
                        ret = err_commonreply_msgwrong;
                }else if (value == 3){
                        ret = err_commonreply_nosupported;
                }else if (value == 4){
                        ret = err_commonreply_inprocess;
                }else{
                        ret = err_commonreply_unsupportedcode;
                }
        }

	return ret;
}

/*
 *
 * send acceleration  A1
 *
 */
jtt808err_t Jtt808DoActionSendAccelerationA1(jtt808handle_t* handle,jtt808header_t* header,jtt808accelerationA1_t* acce)
{
        jtt808err_t ret = err_ok;
        uint8_t sendPayload[1514*2];
        int sendPayloadSize = 0;
        uint8_t recvbuf[1514*2];
        int recvlen;

        header->msgId = JTT808_MSGID_SEND_ACCELRATION_A1;

        Jtt808ConvertStructToRawData((uint8_t*)acce,sizeof(jtt808accelerationA1_t),sendPayload,&sendPayloadSize);
        DO_SEND_RECV_CHECK(sendPayload,sendPayloadSize,recvbuf,recvlen);

        if (ret == err_ok){
                int bodyIndex = Jtt8080GetRawDataBodyIndex(recvbuf,recvlen);
                uint8_t value = recvbuf[bodyIndex+4];
                if (value == 0){
                        // ok
                }else if (value == 1){
                        ret = err_commonreply_failed;
                }else if (value == 2){
                        ret = err_commonreply_msgwrong;
                }else if (value == 3){
                        ret = err_commonreply_nosupported;
                }else if (value == 4){
                        ret = err_commonreply_inprocess;
                }else{
                        ret = err_commonreply_unsupportedcode;
                }
        }

        return ret;
}
/*
 *
 * send acceleration  C1
 *
 */
jtt808err_t Jtt808DoActionSendAccelerationC1(jtt808handle_t* handle,jtt808header_t* header,jtt808accelerationC1_t* acce)
{
        jtt808err_t ret = err_ok;
        uint8_t sendPayload[1514*2];
        int sendPayloadSize = 0;
        uint8_t recvbuf[1514*2];
        int recvlen;

        header->msgId = JTT808_MSGID_SEND_ACCELRATION_C1 ;

        Jtt808ConvertStructToRawData((uint8_t*)acce,sizeof(*acce),sendPayload,&sendPayloadSize);
        DO_SEND_RECV_CHECK(sendPayload,sendPayloadSize,recvbuf,recvlen);

        if (ret == err_ok){
                int bodyIndex = Jtt8080GetRawDataBodyIndex(recvbuf,recvlen);
                uint8_t value = recvbuf[bodyIndex+4];
                if (value == 0){
                        // ok
                }else if (value == 1){
                        ret = err_commonreply_failed;
                }else if (value == 2){
                        ret = err_commonreply_msgwrong;
                }else if (value == 3){
                        ret = err_commonreply_nosupported;
                }else if (value == 4){
                        ret = err_commonreply_inprocess;
                }else{
                        ret = err_commonreply_unsupportedcode;
                }
        }

        return ret;
}
#if JTT808_TEST_REGISTER || JTT808_TEST_SEND_HEART_PACKET
int main()
{
	jtt808handle_t rawhandle;
        jtt808handle_t* handle = & rawhandle;

        Jtt808InitHandle(handle);
	jtt808header_t header;

	jtt808err_t err = err_ok;
        if (Jtt808CreteSocket(handle)){
                return -1;
        }

        if (Jtt808Connect(handle,JTT808_TEST_IP,JTT808_TEST_PORT)){
                return -1;
        }

#if JTT808_TEST_REGISTER
	jtt808register_t regist;

	for (int i =0;i<30;i++){
		regist.terminalId[i] = i;
	}

	err=Jtt808DoActionRegister(handle,&header,&regist);
	PRINT(("register %d\n",err));
	if (err == err_ok){
		PRINT(("author id\n"));
		jtt808_print_data(handle->token.payload,handle->token.len);
	}

#endif

#if JTT808_TEST_SEND_HEART_PACKET
	for (int i=0;i<3;i++){
		err=Jtt808DoActionSendHeartPacket(handle,&header);
		PRINT(("send heart packet %d ret:%d\n",i+1,err));
	}
#endif

#if JTT808_TEST_SEND_POSITION_PACKET
	for (int i=0;i<10;i++){
		jtt808position_t pos;
		memset(&pos,0,sizeof(pos));
		pos.alarmFlag = 0x12345678;
		pos.status = 0x22345678;
//		pos.longitude = 0x32345678;
		pos.longitude = i*i;
		//pos.latitude = 0x42345678;
		pos.latitude = i*i+3;
		pos.altitude = 0x3344;
		pos.speed = 0x5566;
		pos.direction = 0x7788;
		pos.time[0] = 0x21;
		pos.time[1] = 0x06;
		pos.time[2] = 0x17;
		pos.time[3] = 0x14;
		pos.time[4] = 0x09;
		pos.time[5] = ((i+1)/10<<4) + ((i+1)%10);

		err=Jtt808DoActionSendPosition(handle,&header,&pos);
		PRINT(("send position result:%d \n",err));
		sleep(1);
	}
#endif

#if JTT808_TEST_SEND_ACCELERATION_A1
	for (int i = 0;i<10;i++){
		jtt808accelerationA1_t acce;
		memset(&acce,0,sizeof(acce));

		acce.eventType = 0x3412;
		acce.timestamp = 0x7856;
		acce.time[0] = 0x1;
		acce.time[1] = 0x2;
		acce.time[2] = 0x3;
		acce.time[3] = 0x4;
		acce.time[4] = 0x5;
		acce.time[5] = 0x6;
		acce.millisecond= i+1;
		acce.resolution = 0x1;
		acce.x = i;
		acce.y = -2;
		acce.z = 3;

		err=Jtt808DoActionSendAccelerationA1(handle,&header,&acce);
                PRINT(("send acceleration A1 result:%d \n",err));
                sleep(1);
	}
#endif

#if JTT808_TEST_SEND_ACCELERATION_C1
        for (int i = 0;i<10;i++){
                jtt808accelerationC1_t acce;
                memset(&acce,0,sizeof(acce));

                acce.eventType = 0x3412;
                acce.time[0] = 0x1;
                acce.time[1] = 0x2;
                acce.time[2] = 0x3;
                acce.time[3] = 0x4;
                acce.time[4] = 0x5;
                acce.time[5] = 0x6;
                acce.millisecond= i+1;

                acce.temp = 0x1;
                acce.pitch = 1;
                acce.roll = -2;
                acce.yaw = 3;

		acce.aacx = 0x1;
		acce.aacy = 0x1;
		acce.aacz = 0x1;
		acce.gyrox = 0x2;
		acce.gyroy = 0x2;
		acce.gyroz = 0x2;

                err=Jtt808DoActionSendAccelerationC1(handle,&header,&acce);
                PRINT(("send acceleration C1 result:%d \n",err));
                sleep(1);
        }
#endif

	Jtt808CloseSocket(handle);
	return 0;
}
#endif
