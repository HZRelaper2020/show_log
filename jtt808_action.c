#include "jtt808_send_recv_packet.h"
#include "jtt808_convert.h"

typedef struct Jtt808SendAndRecv{
	jtt808handle_t* handle;
	jtt808header_t* header;
	uint8_t* sendbuf;
	int sendlen;
	int maxlen;

	int* recvlen;


}Jtt808SendAndRecv_t;

static jtt808err_t Jtt808DoSendAndRecv(Jtt808SendAndRecv_t* sr)
{
#if ARMGCC
	phtread_mutex_lock();
#endif
	jtt808err_t ret = err_ok;

	jtt808handle_t* handle = sr->handle;
        jtt808header_t* header = sr->header;
        uint8_t* sendbuf = sr->sendbuf;
        int sendlen = sr->sendlen;
        int maxlen = sr->maxlen;


	static uint8_t recvbuf[JTT808_MAX_BUFFER_LENGTH];
	if (Jtt808SendPacket(handle,header,sendbuf,sendlen)){
		ret = err_send_failed;
	}else{
		if (Jtt808RecvOnePacket(handle,sendbuf,&sendlen)){
			ret = err_recv_failed;
		}else{
			*(sr->recvlen) = sendlen;
		}
	}

#if ARMGCC
	phtread_mutex_unlock();
#endif
	return ret;
}

jtt808err_t Jtt808ActionRegister(jtt808handle_t* handle,jtt808header_t* header,jtt808register_t* regist)
{
	jtt808err_t ret = err_ok;
	uint8_t sendbuf[1514*2];
	int size =0;
	const uint16_t flowId = header->flowId;
	int recvlen = 0;

	header->msgId = JTT808_MSGID_REGISTER;

	Jtt808ConvertReigstStructToRawData(regist,sendbuf,&size);
	
	Jtt808SendAndRecv_t sr;
	sr.handle= handle;
	sr.header= header;
	sr.sendbuf= sendbuf;
	sr.sendlen = size;
	sr.maxlen = sizeof(sendbuf);
	sr.recvlen = &recvlen;

	ret = Jtt808DoSendAndRecv(&sr);

	if (ret == err_ok){
	}

	return ret;
}
