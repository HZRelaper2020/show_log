#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <arpa/inet.h>
#include <errno.h>
#include <unistd.h>
#include <time.h>

#include "jtt808_common.h"

static int Jtt808AddMessageHeader()
{
	return 0;
}

static int Jtt808FillOtherAttributes(jtt808_t* jtt)
{
	jtt->identify = 0x7e;
	return 0;
}

static int Jtt808ConvertNetStream(jtt808_t* jtt)
{
#ifdef BIGENDIAN
#else
	jtt808header_t* header = &jtt->header;
	header->msgId = htons(header->msgId);
	header->flowId = htons(header->flowId);

	if (header->msgPkgItem.pkgCount > 0){
		header->msgPkgItem.pkgCount = htons(header->msgPkgItem.pkgCount);
		header->msgPkgItem.pkgNumber = htons(header->msgPkgItem.pkgNumber);
	}
#endif
	return 0;
}

/*
 * send heart pkg to keep live
 *
 */
static int Jtt808SendKeepLive(jtt808handle_t* handle)
{
        jtt808_t jtt;
        memset(&jtt,0,sizeof(jtt));
	return 0;
}

static int Jtt808RegisterClient(jtt808handle_t* handle,const uint8_t* username,const uint8_t* pwd,jtt808authorToken_t* authorToken)
{
	
	return 0;
}

static int Jtt808NetworkSetSendTimeout(jtt808handle_t* handle,int timeout)
{
#ifdef ARMGCC
	return setsockopt(handle->sk,SOL_SOCKET,SO_SNDTIMEO,&timeout,sizeof(int));
#else
	struct timeval timeStruct={timeout/1000,timeout%1000};
	return setsockopt(handle->sk,SOL_SOCKET,SO_SNDTIMEO,&timeStruct,sizeof(timeStruct));
#endif
}

static int Jtt808NetworkSetRecvTimeout(jtt808handle_t* handle,int timeout)
{
#ifdef ARMGCC
	return setsockopt(handle->sk,SOL_SOCKET,SO_RECVTIMEO,&timeout,sizeof(int));
#else
	struct timeval timeStruct={timeout/1000,timeout%1000};
	return setsockopt(handle->sk,SOL_SOCKET,SO_RECVTIMEO,&timeStruct,sizeof(timeStruct));
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

	int sk = socket(AF_INET,SOCK_STREAM,0);
	if (sk < 0){
		perror("scoket failed");
		ERROR(("scoket"));
		return -1;
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

		if (Jtt808RegisterClient(sk,username,pwd,&handle.token)){
			ERROR(("register failed\n"));
			break;
		}

		time_t sendLastHeartTime = 0;

		while(1)
		{
			if (time(NULL) - sendLastHeartTime > 5 || time(NULL) - sendLastHeartTime < 0){
				if (Jtt808SendKeepLive(sk)){
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
