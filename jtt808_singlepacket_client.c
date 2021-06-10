#include <stdio.h>
#include "jtt808_common.h"
#include "jtt808_netutil.h"
#include "jtt808_convert.h"

#define TEST_RECV_SUBPACKET 1


/*
 *
 * translate 0x7d 0x01 to 0x7d
 * translate 0x7d 0x02 to 0x7e
 *@return translate count
 */
static int JTT808Decode0x7d01And0x7d02(uint8_t* inbuf,int insize,uint8_t* outbuf,int* outsize)
{
	int count = 0;
	int outi  =0;
	for (int i=0;i<insize-1;i++){
		uint8_t c1 = *(inbuf+i+0);
		uint8_t c2 = *(inbuf+i+1);
		if (c1 == 0x7d && c2 == 0x01){
			i += 1;
			count +=1;
			if (outbuf)
				outbuf[outi++] = 0x7d;
		}else if (c1 == 0x7d && c2 == 0x02){
			i += 1;
			count +=1;
			if (outbuf)
				outbuf[outi++] = 0x7e;
		}else{
			if (outbuf)
				outbuf[outi++] = c1;
		}
	}
	outbuf[outi++] = *(inbuf+insize -1);

	*outsize = insize - count;
	return count;
}
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
#if TEST_RECV_SUBPACKET
		PRINT(("recv raw data\n"));
		jtt808_print_data(recvbuf,recvsize);
		PRINT(("\n\n"));
#endif
		JTT808Decode0x7d01And0x7d02(recvbuf,recvsize,msg,msgLen);	
		recvsize = *msgLen;
		memcpy(recvbuf,msg,recvsize);
#if TEST_RECV_SUBPACKET
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
                if (!JTT808ConvertRawDataToHeader(&header,recvbuf,recvsize)){
			int calMsgLen = recvsize - (header.msgBodyProperty.hasSubPkg?4:0);
			if (header.msgBodyProperty.msgLength != calMsgLen){
				ERROR(("message length failed 0x%03x 0x%03x",header.msgBodyProperty.msgLength,calMsgLen));
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
	uint8_t recvbuf[1514];
	int recvsize= 0;
	
	int hasPacket = 0;

	if (Jtt808RecvOneSubPacket(handle,recvbuf,&recvsize)){
		jtt808header_t header;
		if (!JTT808ConvertRawDataToHeader(&header,recvbuf,recvsize)){
			if (header.msgBodyProperty.hasSubPkg){
				// recv until last packet
				if (recvsize >= 21){
					if (header.msgPkgItem.pkgCount > 128){
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
							if (times >128)
								break;

							if (!JTT808ConvertRawDataToHeader(&header,recvbuf,recvsize)){
								ERROR(("convert data header failed"));
								break;
							}

							if (flowId != header.flowId){
								ERROR(("flowId != header.flowId"));
								break;
							}else if (msgId != header.msgId){
								ERROR(("msgId != header.msgId"));
								break;
							}else if (!header.msgBodyProperty.hasSubPkg){
								ERROR(("!header.msgBodyProperty.hasSubPkg"));
								break;
							}else if (header.msgPkgItem.pkgNumber != pkgNumber){
								ERROR(("header.msgPkgItem.pkgNumber != pkgNumber"));
								break;
							}else if (header.msgPkgItem.pkgCount != pkgCount){
								ERROR(("header.msgPkgItem.pkgCount != pkgCount"));
								break;
							}
							
							memcpy(data+curDataLen,recvbuf+22,recvsize-22);
							curDataLen += recvsize-22;

							if (header.msgPkgItem.pkgCount == pkgCount){
								hasPacket = 1;
								*datalen = curDataLen;
								break;
							}
						}
					}
				}
			}else{
				hasPacket = 1;
				*datalen = recvsize;
				memcpy(data,recvbuf,recvsize);
			}
		}
	}
	return hasPacket;
}

#if TEST_RECV_SUBPACKET
int main()
{
	jtt808handle_t rawhandle;
	jtt808handle_t* handle = & rawhandle;

	memset(handle,0,sizeof(jtt808handle_t));

	handle->pollRecvTime = MAX_JTT808_RECV_POLL_TIME;
	handle->pollSendTime = MAX_JTT808_SEND_POLL_TIME;
	
	handle->send = Jtt808NetSend;
	handle->recv = Jtt808NetRecv;

	if (Jtt808CreteSocket(handle)){
		return -1;
	}

	if (Jtt808Connect(handle,JTT808_TEST_IP,JTT808_TEST_PORT)){
                return -1;
        }

	uint8_t recvbuf[1514];
	int recvsize = 0;

	if (Jtt808RecvOnePacket(handle,recvbuf,&recvsize)){
		PRINT(("recv size:%d\n",recvsize));
		for (int i=0;i<recvsize;i++){
			PRINT(("%02x ",recvbuf[i]));
			if (i%16 == 15)
				PRINT(("\n"));
		}
		PRINT(("\n\n"));
	}

	return 0;
}
#endif
