#if USE_OLD_NETCLINET  // no used

#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <arpa/inet.h>
#include <errno.h>
#include <unistd.h>
#include <time.h>

#include "jtt808_common.h"

static jtt808_t g_lastSendPacket;

static int Jtt808FillOtherAttributes(jtt808_t* jtt)
{
	jtt->identify = 0x7e;
	jtt808header_t* header = &jtt->header;
	jtt808MsgBodyProperty_t* msgBodyProperty = &header->msgBodyProperty;
	
	header->protocolVersion=1;
	header->terminalMobile[0] = 0x17;
	header->terminalMobile[1] = 0x31;
	header->terminalMobile[2] = 0x84;
	header->terminalMobile[3] = 0x53;
	header->terminalMobile[4] = 0x26;
	header->terminalMobile[5] = 0x80;
	header->terminalMobile[6] = 0x0;
	header->terminalMobile[7] = 0x0;
	header->terminalMobile[8] = 0x0;
	header->terminalMobile[9] = 0x0;

	msgBodyProperty->reserved = 0;
	msgBodyProperty->versionIdentify = 0x1;
	msgBodyProperty->encodeType =0x0;
	msgBodyProperty->encodeType = 0x0;
	/*
	 * msgBodyProperty->hasSubPkg;
	 * msgBodyProperty->msgLength
	 */

	return 0;
}

static int Jtt808HeaderConvertNetStream(jtt808header_t* header)
{
#ifndef BIGENDIAN
	header->msgId = htons(header->msgId);
	header->flowId = htons(header->flowId);

	if (header->msgPkgItem.pkgCount > 0){
		header->msgPkgItem.pkgCount = htons(header->msgPkgItem.pkgCount);
		header->msgPkgItem.pkgNumber = htons(header->msgPkgItem.pkgNumber);
	}
#endif
	return 0;
}
static int Jtt808ConvertNetStream(jtt808_t* jtt)
{
	jtt808header_t* header = &jtt->header;
	return Jtt808HeaderConvertNetStream(header);
}

/*
 * send heart pkg to keep live
 *
 */
static int Jtt808SendKeepLive(jtt808handle_t* handle)
{
        jtt808_t jtt;
        memset(&jtt,0,sizeof(jtt));

	Jtt808FillOtherAttributes(&jtt);
	Jtt808ConvertNetStream(&jtt);
	return 0;
}


/*
 * return: 0x7e and 0x7d count
 */
static int Jtt808Replace0x7eAnd0x7d(const uint8_t* inbuf,int insize,uint8_t* outbuf,int* outsize)
{
	int count =0;
	int outi = 0;
	for (int i=0;i<insize;i++)
	{
		if (inbuf[i] == 0x7e){
			count++;
			if (outbuf){
				outbuf[outi++] = 0x7d;
				outbuf[outi++] = 0x02;
			}
		}else if (inbuf[i] == 0x7d){
			count++;
			if (outbuf){
				outbuf[outi++] = 0x7d;
				outbuf[outi++] = 0x01;
			}
		}else{
			if (outbuf){
				outbuf[outi++] = inbuf[i];
			}
		}
	}

	if (outsize){
		*outsize = count + insize;
	}

	return count;
}

static int Jtt808ReplyConvertNetStream(jtt808CommonReply_t* reply)
{
#ifndef BIGENDIAN
	reply->flowId = htons(reply->flowId);
#endif
	return 0;
}

static int Jtt808RecvOnePacketSub(jtt808handle_t* handle,jtt808header_t* header,uint8_t* payload,int* payloadSize)
{
	uint8_t recvbuf[2];
	uint8_t recvsize = 0;

	int retry = 0;
	int sk = handle->sk;

	while(retry < handle-><pre>maxRecvRetryTimes){
		retry += 1;
		int recvsuccess = 0;
		int times = 0;

		int curRecvSize = 0;
		int curRecvBuf[1514];
		// recv until 0x7e
		while(1){
			times += 1;
			if (times > 1516/2)
				break

			recvsize = recv(sk,recvbuf,2,0);
			int preok = 0;	

			if (recvsize != 2){
				perror("recv");
				ERROR(("recvsize != 2"));
				break;
			}

			if (recvbuf[1] == 0x7e){
				curRecvSize = 0;
				recvsuccess = 1;
				break;
			}else if (recvbuf[0] == 0x7e){
				curRecvSize = 1;
				curRecvBuf[0] = recvbuf[1];
				recvsuccess = 1;
				break;
			}

		}

		// recv until end
		if (recvsuccess){
			recvsuccess = 0;
			times = 0;
			while (1){
				times += 1;
				if (times > 1514)
					break;	
				recvsize = recv(sk,recvbuf,1);
				if (recvsize <= 0){
					perror("recv");
					ERROR(("recv size <=0"));
					break;
				}

				if (recvbuf[0] == 0x7e){
					recvsuccess = 1;
					break;
				}
				curRecvBuf[curRecvSize++] = recvbuf[0];
			}
		}

		
	}

	//					handle->token.len = strlen(reply->authorCode);
	//					memcpy(handle->token.payload,reply->authorCode,handle->token.len);

	return 0;
}

static int Jtt808RecvReply(jtt808handle_t* handle,jtt808_t* jtt)
{
	jtt808header_t* header = &jtt->header;

	int ret = -1;
	int retry = 0;
	const int sk = handle->sk;
	uint8_t recvbuf[500];
	const uint16_t flowId = header->flowId;


	return ret;

}

static int Jtt808SendPacket(jtt808handle_t* handle,const uint16_t msgId,uint8_t* payload,const int payloadSize)
{
#ifdef ARMGCC
	pthread_mutex_lock();
#endif
	int ret = 0;
	int sk = handle->sk;

	uint8_t retry = 0;
	uint8_t sendsuccess = 0;

	uint8_t totSendBuf[1514];
	const uint16_t flowId = g_lastSendPacket.header.flowId==0 ? 0: g_lastSendPacket.header.flowId+1;

	while (retry < handle->maxSendRetryTimes && !sendsuccess){
		jtt808_t jtt;
		jtt808_t* lastPkg = &g_lastSendPacket;
		jtt808header_t* header = &jtt.header;
		jtt808MsgBodyProperty_t* msgBodyProperty = &header->msgBodyProperty;
		jtt808MsgPkgItem_t* msgItemPkg = &header->msgPkgItem;


		memset(&jtt,0,sizeof(jtt));

		header->msgId = msgId;
		header->flowId = flowId;


		int remain = payloadSize;
		uint8_t hasSubItem =remain > 0x1ff ?1:0 ;
		int subItemNum =0;
		int subItemCount = (Jtt808Replace0x7eAnd0x7d(payload,payloadSize,NULL,NULL) + payloadSize + 0x1fe) / 0x1ff;

		while(remain > 0){
			subItemNum +=1;

			jtt808MsgBodyProperty_t* headerProperty = &header->msgBodyProperty;	

			// msg body
			uint8_t msgBodyBuf[0x1ff*2];
			int msgBodySize = 0;
			int sendsize = remain > 0x1ff ?0x1ff:remain;
			uint8_t* startPayload = payload + (payloadSize - remain);
			int count7eAnd7d = Jtt808Replace0x7eAnd0x7d(startPayload,sendsize,NULL,NULL);
			if (sendsize + count7eAnd7d > 0x1ff){
				sendsize -= count7eAnd7d;
				hasSubItem = 1;
			}
			Jtt808Replace0x7eAnd0x7d(startPayload,sendsize,msgBodyBuf,&msgBodySize); // msg body is ok
			// msg header
			if (subItemCount > 1){
				msgBodyProperty->hasSubPkg = 0x1;
				msgItemPkg->pkgCount = (uint16_t)subItemCount;
				msgItemPkg->pkgNumber = (uint16_t)subItemNum;
			}else{

				msgBodyProperty->hasSubPkg = 0x0;
			}
			Jtt808FillOtherAttributes(&jtt);
			Jtt808ConvertNetStream(&jtt);

			uint8_t headerBuf[22*2];
			int headerSize = 0;
			Jtt808Replace0x7eAnd0x7d((uint8_t*)header,subItemCount>1?21:17,headerBuf,&headerSize); // msg header is ok
			
			// check sum
			uint8_t checkSum ;
			uint8_t checkSumBuf[2];
			int checkSumSize=0;

			checkSum = 0x0;
			for (int i = 0 ;i< msgBodySize;i++){
				checkSum  ^= msgBodyBuf[i]; 
			}
			for (int i=0;i<headerSize;i++){
				checkSum  ^= headerBuf[i]; 
			}

			Jtt808Replace0x7eAnd0x7d(&checkSum,1,checkSumBuf,&checkSumSize); // msg header is ok
			// end 0x7e	
			
			int totSendSize = 0;
			totSendBuf[0] = 0x7e;
			memcpy(totSendBuf + 1,headerBuf,headerSize);
			totSendSize = 1 + headerSize;
			memcpy(totSendBuf + totSendSize,msgBodyBuf,msgBodySize);
			totSendSize += msgBodySize;
			memcpy(totSendBuf + totSendSize,checkSumBuf,checkSumSize);
			totSendSize += checkSumSize;
			totSendBuf[totSendSize] = 0x7e;
			totSendSize += 1;



			int curSendSize = send(sk,totSendBuf,totSendSize,0);
#if JTT808_DEBUG_SEND_MSG
			PRINT(("totsendsize:%d\n",totSendSize));
			for (int i=0;i<totSendSize;i++){
				PRINT(("%02x ",totSendBuf[i]));
				if (i%16 == 15) PRINT(("\n"));
			} PRINT(("\n"));
#endif
			
			if (curSendSize != totSendSize){
				perror("send");
				ERROR(("send pkg failed totlen:%d len%d",totSendSize,curSendSize));
				break;
			}else{
				remain -= sendsize;
			}
		} // end while

		// wait for response
		if (remain == 0){
			 Jtt808ConvertNetStream(&jtt);
			 if (Jtt808RecvReply(handle,&jtt)){
				// recv error
			 }else{
				 sendsuccess = 1;
			 }
		}

		retry += 1;
		
	}

#ifdef ARMGCC
	pthread_mutex_unlock();
#endif
	if (!sendsuccess){
		ret = -1;
	}else{
		ret = 0;
	}

	return ret;
}

static int Jtt808RegisterClient(jtt808handle_t* handle,const uint8_t* username,const uint8_t* pwd)
{
	jtt808Register_t body;
	memset(&body,0,sizeof(body));

	strcpy(body.manufacturerId,"1234");
	strcpy(body.terminalId,"5678");

	body.totLen = sizeof(body) - sizeof(body.carPlate) + 10;   
	return Jtt808SendPacket(handle,JTT808_MSGID_REGISTER,(uint8_t*)&body,body.totLen);
}

static int Jtt808NetworkSetSendTimeout(jtt808handle_t* handle,int timeout)
{
#ifdef ARMGCC
	int ret =setsockopt(handle->sk,SOL_SOCKET,SO_SNDTIMEO,&timeout,sizeof(int));
#else
	struct timeval timeStruct={timeout/1000,timeout%1000};
	int ret= setsockopt(handle->sk,SOL_SOCKET,SO_SNDTIMEO,&timeStruct,sizeof(timeStruct));
#endif
	if (ret < 0)
		perror("setsockopt");
	return ret;
}

static int Jtt808NetworkSetRecvTimeout(jtt808handle_t* handle,int timeout)
{
#ifdef ARMGCC
	return setsockopt(handle->sk,SOL_SOCKET,SO_RCVTIMEO,&timeout,sizeof(int));
#else
	struct timeval timeStruct={timeout/1000,timeout%1000};
	return setsockopt(handle->sk,SOL_SOCKET,SO_RCVTIMEO,&timeStruct,sizeof(timeStruct));
#endif
}

static int Jtt808NetworkRecv(jtt808handle_t* handle,uint8_t* buf,int size,int polltime)
{
	int sk = handle->sk;
	struct pollfd pfd;
	int ret=0;
	int recvsize=0;

	memset(&pfd,0,sizeof(pfd));
	pfd.fd = sk;
	pfd.events = POLLIN;
	pfd.revents = 1;

	if (Jtt808NetworkSetRecvTimeout(handle,polltime)){
		ERROR(("set recv timeout failed"));
	}

	recvsize = recv(sk,buf,size,0);
	if (recvsize < 0){
		ERROR(("recv failed"));
		perror("recv");
	}

	return ret;
}

static int Jtt808RecvOnePaket(jtt808handle_t* handle,int polltime)
{
	uint8_t buf[2];
	int preStepOk = 0;

	while (Jtt808NetworkRecv(handle,buf,2,polltime) == 2){
		if (buf[0] == 0x7e && buf[1] != 0x2){
			preStepOk = 1;
			break;
		}
	}


	return 0;
}

static int Jtt808SendOnePaket(jtt808handle_t* handle,int polltime,int retrys)
{
	return 0;
}

int main()
{
	const uint16_t port = 8837;
	const uint8_t* ip = "192.168.5.7";
	const uint8_t* username = "admin";
	const uint8_t* pwd = "123456";
	
	jtt808handle_t handle;
	memset(&handle,0,sizeof(handle));

	handle.maxSendRetryTimes = MAX_JTT808_SEND_RETRY_TIMES;
	handle.maxRecvRetryTimes = MAX_JTT808_RECV_RETRY_TIMES;

	// last send packet
	memset(&g_lastSendPacket,0,sizeof(g_lastSendPacket));

	int sk = socket(AF_INET,SOCK_STREAM,0);
	if (sk < 0){
		perror("scoket failed");
		ERROR(("scoket"));
		return -1;
	}


	handle.sk = sk;
	if (Jtt808NetworkSetSendTimeout(&handle,MAX_JTT808_SEND_POLL_TIME)){
		ERROR(("set send poll time failed"));
	}
	if (Jtt808NetworkSetRecvTimeout(&handle,MAX_JTT808_RECV_POLL_TIME)){
		ERROR(("set recv poll time failed"));
	}

	struct sockaddr_in addr;
	memset(&addr,0,sizeof(addr));
	addr.sin_family = AF_INET;
	addr.sin_port = htons(port);
	addr.sin_addr.s_addr = inet_addr(ip);

	do {
		if (connect(sk,(struct sockaddr*)&addr,sizeof(addr))){
			ERROR(("connect failed\n"));
			perror("connect");
			break;
		}

		if (Jtt808RegisterClient(&handle,username,pwd)){
			ERROR(("register failed\n"));
			break;
		}

		printf("regsiter ok\n");
		time_t sendLastHeartTime = 0;

		while(0)
		{
			if (time(NULL) - sendLastHeartTime > 5 || time(NULL) - sendLastHeartTime < 0){
				if (Jtt808SendKeepLive(&handle)){
					ERROR(("send keep alive failed\n"));
				}else{
					sendLastHeartTime = time(NULL);
				}
			}

			int rxStatus=0;
			do{
				rxStatus= Jtt808RecvOnePaket(&handle,10);
			}while(rxStatus > 0);
			if (rxStatus < 0)
				break;

			uint32_t txStatus =0;
			do{
				txStatus = Jtt808SendOnePaket(&handle,1000,3);
			}while(txStatus > 0);
			if (txStatus < 0)
				break;


		}
	}while(0);
	
#ifdef ARMGCC
	closeSocket(sk);
#else
	close(sk);
#endif

	return 0;
}

#endif
