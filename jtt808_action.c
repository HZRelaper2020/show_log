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
	
	Jtt808SendAndRecv_t sr;
	memset(&sr,0,sizeof(sr));
	sr.handle= handle;

	sr.header = header;
	sr.sendPayload= sendPayload;
	sr.sendPayloadSize= sendPayloadSize;

	sr.recvbuf = recvbuf;
	sr.maxRecvLen = sizeof(recvbuf);


	ret = Jtt808DoSendAndRecv(&sr);
	recvlen = sr.recvlen;


	if (ret == err_ok){
		ret = Jtt808BasicCheckSendRecv(header,recvbuf,recvlen);
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
	}

	return ret;
}

jtt808err_t Jtt808DoActionSendHeartPacket(jtt808handle_t* handle,jtt808header_t* header)
{
	jtt808err_t ret = err_ok;
	header->msgId = JTT808_MSGID_SEND_HEARTPKG;

	uint8_t recvbuf[1514*2];
	int recvlen;


	Jtt808SendAndRecv_t sr;
	memset(&sr,0,sizeof(sr));
        sr.handle= handle;

        sr.header = header;
        sr.sendPayload= NULL;
        sr.sendPayloadSize= 0;

        sr.recvbuf = recvbuf;
        sr.maxRecvLen = sizeof(recvbuf);


        ret = Jtt808DoSendAndRecv(&sr);
        recvlen = sr.recvlen;

	if (ret == err_ok){
                ret = Jtt808BasicCheckSendRecv(header,recvbuf,recvlen);
                if (ret == err_ok){
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
	Jtt808CloseSocket(handle);
	return 0;
}
#endif
