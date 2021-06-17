#include "jtt808_basic_check.h"
#include "jtt808_convert.h"


jtt808err_t Jtt808BasicCheckSendRecv(jtt808header_t* sendheader,uint8_t* recvbuf,int recvlen)
{
	jtt808err_t ret = err_ok;

	jtt808header_t recvheader;

	if (Jtt808ConvertRawDataToHeader(recvbuf,recvlen,&recvheader)){
		ret = err_convert_header;
	}

	jtt808header_t* s = sendheader;
	jtt808header_t* r = &recvheader;

	if (ret == err_ok){
		if (s->flowId != r->flowId){
			ret = err_flowid_not_matched;
		}
	}

	if (ret == err_ok){
		switch(s->msgId){
			case JTT808_MSGID_REGISTER:
				if (r->msgId == 0x8100){

				}else{
					ret = err_msg_id_not_matched;
				}
				break;
			case JTT808_MSGID_SEND_HEARTPKG:
			case JTT808_MSGID_SEND_POSITION:
				if (r->msgId == 0x8001){
				}else{
					ret = err_msg_id_not_matched;
				}
				break;
			default:
				ret = err_not_supported_send_msgid;
				break;
		}
	}

	return ret;
}


uint8_t Jtt808GetCheckSum(uint8_t* data,int size)
{
	uint8_t checksum = 0;
        for (int i =0;i<size;i++){
                checksum ^= data[i];
        }

	return checksum;
}
