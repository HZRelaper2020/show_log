#include <stdio.h>
#include "jtt808_common.h"
#include "jtt808_netutil.h"
#include "jtt808_convert.h"
#include "jtt808_singlepacket_client.h"

//#define TEST_RECV_PACKET 			0
//#define TEST_SEND_PACKET 			0

/*
 * receive data until get 0x7e  not include 0x7e
 * @return  0:success  other:failed
 */
static int Jtt808RecvUintil0x7e(jtt808handle_t* handle,uint8_t* data,int* size)
{
	int len =0;
	int times = 0;
	int ret = 0;
	uint8_t recvbuf[1];
	int recvlen =0;

	times = 0;
	recvlen = 0;
	ret = -1;
	while (1){
		times += 1;
		if (times > 1514)
			break;

                len = handle->recv(handle,recvbuf,1);
                if (len == 1){
                        if (recvbuf[0] == 0x7e){
				ret = 0;
                                break;
                        }

			memcpy(data + recvlen,recvbuf,len);
			recvlen += len;
                }else{
                        break;
                }
        }

	*size = recvlen;

	return ret;
}
/*
 * get from 0x7e to 0x7e
 * @return 0 :nothing    1 :hasPacket 
 */
static int Jtt808RecvOneSubPacket(jtt808handle_t* handle,uint8_t* msg,int* msgLen)
{
	uint8_t recvbuf[1514];
	int recvsize = 0;
	int hasPacket = 0;


	if (!Jtt808RecvUintil0x7e(handle,recvbuf,&recvsize)){
		// receive again
		if (!Jtt808RecvUintil0x7e(handle,recvbuf,&recvsize)){
			if (recvsize < 13){
				// receive again
				if (!Jtt808RecvUintil0x7e(handle,recvbuf,&recvsize)){
				}else{
					recvsize = 0;
				}
			}

			if (recvsize > 13){
				hasPacket = 1;
			}
		}
	}

	if (hasPacket){
#if TEST_RECV_PACKET
		PRINT(("recv raw data\n"));
		jtt808_print_data(recvbuf,recvsize);
		PRINT(("\n\n"));
#endif
		JTT808Decode0x7d01And0x7d02(recvbuf,recvsize,msg,msgLen);	
		recvsize = *msgLen;
		memcpy(recvbuf,msg,recvsize);
#if TEST_RECV_PACKET
		PRINT(("after decode 0x7d01 and 0x7d02\n"));
		jtt808_print_data(recvbuf,recvsize);
		PRINT(("\n\n"));
#endif
	}

	if (hasPacket){ 
		// checkcode 
		uint8_t checksum = recvbuf[recvsize-1];
		recvsize -= 1;

#if JTT808_CHECK_RECV_CHECKSUM
		hasPacket = 0;
		uint8_t dataCheckSum = 0;
		for (int i=0;i<recvsize;i++)
		{
			dataCheckSum ^= recvbuf[i];
		}

		if (dataCheckSum == checksum){
			hasPacket = 1;
		}else{
			ERROR(("checksum not equal %02x %02x",dataCheckSum,checksum));
		}
#endif

	}

	// check msg legth
	if (hasPacket){
		hasPacket = 0;
		jtt808header_t header;
                if (!JTT808ConvertRawDataToHeader(recvbuf,recvsize,&header)){
			int calMsgLen = recvsize - 17-(header.msgBodyProperty.attr.hasSubPkg?4:0);
			if (header.msgBodyProperty.attr.msgLength != calMsgLen){
				ERROR(("message length failed 0x%03x 0x%03x",header.msgBodyProperty.attr.msgLength,calMsgLen));
			}else{
				hasPacket = 1;
			}
		}
	}

	if (hasPacket){
		memcpy(msg,recvbuf,recvsize);
		*msgLen = recvsize;
	}

	return hasPacket;
}

/*
 *
 * receive one packet
 *
 *@return 0: no packet  1:has packet
 */
int Jtt808RecvOnePacket(jtt808handle_t* handle,uint8_t* data,int* datalen)
{
	uint8_t recvbuf[1514*2];
	int recvsize= 0;
	
	int hasPacket = 0;

	if (Jtt808RecvOneSubPacket(handle,recvbuf,&recvsize)){
		jtt808header_t header;
		if (!JTT808ConvertRawDataToHeader(recvbuf,recvsize,&header)){

			if (header.msgBodyProperty.attr.hasSubPkg){
				// recv until last packet
				if (recvsize >= 21 ){
					if (header.msgPkgItem.pkgCount < 2){
						ERROR(("pkgCount %d < 2",header.msgPkgItem.pkgCount));
					}else if (header.msgPkgItem.pkgCount > 128){
						ERROR(("pkgCount too long"));
					}else if (header.msgPkgItem.pkgNumber != 1){
						ERROR(("pkgNumber is not 1 %d",header.msgPkgItem.pkgNumber));
					}else{
						const uint16_t msgId = header.msgId;
						const uint16_t flowId = header.flowId;
						uint16_t pkgNumber = header.msgPkgItem.pkgNumber;
						const uint16_t pkgCount = header.msgPkgItem.pkgCount;
						int times = 0;
						int curDataLen = 0;
						memcpy(data,recvbuf,recvsize);
						curDataLen += recvsize;

						times = 0;
						while(Jtt808RecvOneSubPacket(handle,recvbuf,&recvsize)){
							pkgNumber += 1;
							times +=1;
							if (times >pkgCount)
								break;

							if (JTT808ConvertRawDataToHeader(recvbuf,recvsize,&header)){
								ERROR(("convert data header failed recvsize:%d",recvsize));
								break;
							}

							if (flowId != header.flowId){
								ERROR(("flowId != header.flowId"));
								break;
							}else if (msgId != header.msgId){
								ERROR(("msgId != header.msgId"));
								break;
							}else if (!header.msgBodyProperty.attr.hasSubPkg){
								ERROR(("!header.msgBodyProperty.hasSubPkg"));
								break;
							}else if (header.msgPkgItem.pkgNumber != pkgNumber){
								ERROR(("header.msgPkgItem.pkgNumber != pkgNumber %x %x",header.msgPkgItem.pkgNumber,pkgNumber));
								break;
							}else if (header.msgPkgItem.pkgCount != pkgCount){
								ERROR(("header.msgPkgItem.pkgCount != pkgCount"));
								break;
							}
							
							memcpy(data+curDataLen,recvbuf+21,recvsize-21);
							curDataLen += recvsize-21;

							if (header.msgPkgItem.pkgNumber == pkgCount){
								hasPacket = 1;
								*datalen = curDataLen;
								break;
							}
						}
					}
				}
			}else if (!header.msgBodyProperty.attr.hasSubPkg){
				hasPacket = 1;
				*datalen = recvsize;
				memcpy(data,recvbuf,recvsize);
			}
		}
	}
	return hasPacket;
}

int Jtt808InitHandle(jtt808handle_t* handle)
{
	memset(handle,0,sizeof(jtt808handle_t));

	handle->pollRecvTime = MAX_JTT808_RECV_POLL_TIME;
	handle->pollSendTime = MAX_JTT808_SEND_POLL_TIME;
	
	handle->send = Jtt808NetSend;
	handle->recv = Jtt808NetRecv;

	return 0;
}


/*
 *
 *
 *@return 0:success
 *
 */
static int Jtt808SendRawData(jtt808handle_t* handle,uint8_t* data,int size)
{

	uint8_t senddata[1514*2];
	int sendsize = 0;
	int ret = 0;

	senddata[0] = 0x7e;
	Jtt808Encode0x7eAnd0x7d(data,size,senddata+1,&sendsize);
	senddata[sendsize+1] = 0x7e;

	ret = -1;
#if TEST_SEND_PACKET
	PRINT(("send data %d\n",sendsize+2));
	jtt808_print_data(senddata,sendsize+2);
	PRINT(("\n\n"));
#endif
	if (handle->send(handle,senddata,sendsize+2) == sendsize+2){
		ret = 0;
	}
	return ret;
}
/*
 *
 *
 * @return 0:success
 *
 */
int Jtt808SendPacket(jtt808handle_t* handle,jtt808header_t* argheader,uint8_t* payload,const int payloadSize)
{
	uint16_t msgId = argheader->msgId;
	uint16_t flowId = argheader->flowId;
	int ret = 0;

	int remain = payloadSize;

	uint8_t senddata[1514*2];
	uint8_t tempbuf[1514];
	int headerSize = 0;

	jtt808header_t header;
	jtt808header_t* h = & header;
	memcpy(h,argheader,sizeof(jtt808header_t));


	uint8_t multiPkg = payloadSize > 0x1ff ?1:0;

	ret = -1;
	uint16_t pkgNumber = 0;
	const uint16_t pkgCount = (payloadSize + 0x1fe)/0x1ff;
	while(remain > 0){
		int sendSize = remain > 0x1ff ? 0x1ff:remain;
		h->msgBodyProperty.attr.msgLength = sendSize;

		if (multiPkg){
			pkgNumber += 1;
			h->msgBodyProperty.attr.hasSubPkg = 1;
			h->msgPkgItem.pkgCount = pkgCount;
			h->msgPkgItem.pkgNumber = pkgNumber;
		}

		Jtt808ConvertHeaderToRawData(h,tempbuf,&headerSize);
		 

		memcpy(senddata,tempbuf,headerSize);
		memcpy(senddata+headerSize,payload+payloadSize-remain,sendSize);

		remain -= sendSize;

#if JTT808_DO_SEND_CHECKSUM
		uint8_t checksum = 0;
		for (int i =0;i<headerSize+sendSize;i++){
			checksum ^= senddata[i];
		}
		senddata[headerSize+sendSize] = checksum;
#endif
		if (Jtt808SendRawData(handle,senddata,headerSize+sendSize+1)){
			ERROR(("send raw data failed"));
		}else{
			if (remain ==0){
				ret = 0;
			}
		}

	}

	return ret;
}

#if TEST_RECV_PACKET || TEST_SEND_PACKET
int main()
{
	jtt808handle_t rawhandle;
	jtt808handle_t* handle = & rawhandle;

	Jtt808InitHandle(handle);

	if (Jtt808CreteSocket(handle)){
		return -1;
	}

	if (Jtt808Connect(handle,JTT808_TEST_IP,JTT808_TEST_PORT)){
                return -1;
        }

	uint8_t recvbuf[1514*12];
	int recvsize = 0;
	jtt808header_t rawheader;
	jtt808header_t* header = & rawheader;

#if TEST_RECV_PACKET
	for (int i=0;i<2;i++){
		if (Jtt808RecvOnePacket(handle,recvbuf,&recvsize)){
			PRINT(("recv success size:%d\n",recvsize));
			jtt808_print_data(recvbuf,recvsize);
			PRINT(("\n\n"));
		}
	}
#endif

#if TEST_SEND_PACKET
	memset(header,0,sizeof(*header));
	header->msgId = 0x1234;
	header->flowId = 0x5678;
	header->protocolVersion = 0x1;
	header->terminalMobile[0] = 0x17;
	header->terminalMobile[9] = 0x68;

	for (int i=0;i<sizeof(recvbuf);i++){
		recvbuf[i] = 0x70+i;
	}

	if (Jtt808SendPacket(handle,header,recvbuf,100)){
		return -1;
	}

	for (int i=0;i<sizeof(recvbuf);i++){
		recvbuf[i] = 0x70+i;
	}

	if (Jtt808SendPacket(handle,header,recvbuf,sizeof(recvbuf)-100)){
		return -1;
	}

	PRINT(("send successs\n"));
#endif
	return 0;
}

#endif
