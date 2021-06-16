#include "jtt808_netutil.h"

/*
 *
 * have data return 0
 *
 *
 */

#define TEST_NETWORK_POLL 0

/*
 *
 *
 *@return 0:has data  1:timeout
 *
 */
static int Jtt808PollReadOrWrite(jtt808handle_t* handle,int dir,int ptime)
{

        int ret = 0;
        struct pollfd pfd;
        memset(&pfd,0,sizeof(pfd));

        pfd.fd = handle->sk;
        pfd.events = dir;
        pfd.revents = 1;

        ret = poll(&pfd,1,ptime);

        if (ret < 0){ // error
                perror("poll");
                ERROR(("poll error"));
        }else if (ret == 1){ // have data
                ret = 0;
        }else if (ret == 0){ // timeout
                ret = 1;
        }

        return ret;
}

/*
 *
 * clear socket recv buffer
 * @return 0 success
 *
 */
int Jtt808ClearNetRecvBuffer(jtt808handle_t* handle,int ptime)
{
	int ret = 0;
	uint8_t recvbuf[1024];
	while(1){
		ret = Jtt808PollReadOrWrite(handle,POLLIN,ptime);
		if (ret == 0){ // has data
			if (handle->recv(handle,recvbuf,sizeof(recvbuf)) > 0){
				ERROR(("Jtt808ClearRecvBuffer recv_data failed"));
			}else{
				ret = -1;
				break;
			}
		}else if (ret == 1){
			ret = 0;
			break;
		}else if (ret < 0){
			break;
		}
	}
	return ret;
}

int Jtt808CreteSocket(jtt808handle_t* handle)
{
	int ret = 0;
        int sk = socket(AF_INET,SOCK_STREAM,0);

        ret = -1;
        if (sk < 0){
                perror("socket");
                ERROR(("create socket"));
        }else{
		handle->sk = sk;
		ret = 0;
        }
        return ret;
}

void Jtt808CloseSocket(jtt808handle_t* handle)
{
	if (handle->sk > -1){
#if ARMGCC
		closeSocket(handle->sk);
#else
		close(handle->sk);
#endif
		handle->sk = -1;
	}
}

int Jtt808Connect(jtt808handle_t* handle,const uint8_t* ip,uint16_t port)
{
	int ret = 0;

	ret = -1;
	struct sockaddr_in addr;
	memset(&addr,0,sizeof(addr));
	addr.sin_family = AF_INET;
	addr.sin_port = htons(port);
	addr.sin_addr.s_addr = inet_addr(ip);

	if (connect(handle->sk,(struct sockaddr*)&addr,sizeof(addr))){
		perror("connect");
		ERROR(("connect failed"));
	}else{
		ret  = 0;
	}
	return ret;
}

/*
 *
 *
 *@return send count, send < 0 when error
 *
 */
int Jtt808NetSend(jtt808handle_t* handle,uint8_t* senddata,int sendsize)
{
	int totSize = 0;

	int times = 0;
	while(1){
		times += 1;
		if (times > 0xff)
			break;

		int ret = Jtt808PollReadOrWrite(handle,POLLOUT,handle->pollSendTime);

		if (ret == 0){
			ret= send(handle->sk,senddata,sendsize,0);
			if (ret < 0){
				totSize = -1;
				perror("send");
				ERROR(("send failed"));
				break;
			}else{
				totSize += ret;
				if (totSize == sendsize)
					break;
			}
		}
	}

        return totSize; 
}

/*
 *
 *
 *@return recv data count ,error return <0
 *
 */
int Jtt808NetRecv(jtt808handle_t* handle,uint8_t* recvdata,int recvsize)
{
        int ret = 0;

        ret = Jtt808PollReadOrWrite(handle,POLLIN,handle->pollRecvTime);

        if (ret == 0){
                ret= recv(handle->sk,recvdata,recvsize,0);
                if (ret < 0){
                        perror("recv");
                        ERROR(("recv failed"));
                }
        }else{
		ret = 0;
	}

        return ret;
}

#if TEST_NETWORK_POLL
int main()
{
	jtt808handle_t rawhandle;
	jtt808handle_t* handle = &rawhandle;
	uint8_t buf[1024];

	handle->pollRecvTime = 1000;
	handle->pollSendTime = 1000;
	// pollrecv
	if (Jtt808CreteSocket(handle)){
		return -1;
	}

	if (Jtt808Connect(handle,TT808_TEST_IP,JTT808_TEST_POR)){
		return -1;
	}

	int recvsize = 0;
	for (int i=0;i<100;i++){
		int len = Jtt808NetRecv(handle,buf,1);

		recvsize += len;
		PRINT(("recv len:%d recvsize:%d\n",len,recvsize));
		if (len > 0){
			buf[len+1] = 0;
			for (int j = 0;j<len;j++){
				PRINT(("%02x ",buf[j]));
				if (j%16 == 15)
					PRINT(("\n"));
			} PRINT(("\n\n"));
		}
	}
	PRINT(("recvsize:%d\n",recvsize));

	buf[0] = 0x30;
	buf[1] = 0x31;
	buf[2] = 0x32;
	buf[3] = 0x33;
	buf[4] = 0x34;
	buf[5] = 0x35;
	buf[6] = 0x36;
	buf[7] = 0x37;
	buf[8] = 0x38;
	buf[9] = 0x39;

	int len = Jtt808NetSend(handle,buf,10);
	if (len > 0){
		PRINT(("send len:%d\n",len));
		for (int i=0;i<len;i++){
			PRINT(("%02x ",buf[i]));
			if (i%16 == 15)
				PRINT(("\n"));
		} PRINT(("\n\n"));
	}

	Jtt808CloseSocket(handle);
	PRINT(("test poll success\n"));

	return 0;
}
#endif
