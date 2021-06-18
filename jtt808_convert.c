#include "jtt808_convert.h"

/*
 *
 * convert data to header
 */
int Jtt808ConvertRawDataToHeader(uint8_t* data,int size,jtt808header_t* header)
{
	jtt808header_t* h = (jtt808header_t*)data;

	if (size < 18){
		return -1;
	}

	if ((data[2] & 0x20) && size < 21){
		return -1;
	}

	if (data[2] & 0x20)
		memcpy(header,h,21);
	else
		memcpy(header,h,17);

#if  BIGENDIAN

#else
	header->msgId = htons(h->msgId);
	header->flowId = htons(h->flowId);
	header->msgBodyProperty.value = htons(h->msgBodyProperty.value);

//	jtt808_print_data(data,22);
//	jtt808_print_header(h);
//	PRINT(("\n\n"));
	if (data[2] & 0x20){
		header->msgPkgItem.pkgCount = htons(h->msgPkgItem.pkgCount);
		header->msgPkgItem.pkgNumber = htons(h->msgPkgItem.pkgNumber);
	}
#endif
	return 0;
}

int Jtt8080GetRawDataBodyIndex(uint8_t* rawbuf,int rawlen)
{

        int index = -1;

        if ((rawbuf[2] & 0x20) && rawlen >= 21+3)
                index = 21;
        else if (!(rawbuf[2] & 0x20) && rawlen >= 17+3)
                index = 17;

        return index;
}
/*
 *
 *
 * @return ok return 0
 */

int Jtt808ConvertHeaderToRawData(jtt808header_t* argheader,uint8_t* outbuf,int* outsize)
{
	jtt808header_t* h = (jtt808header_t*)outbuf;

	// must judge before convert
	if (argheader->msgBodyProperty.attr.hasSubPkg){
		*outsize = 21;
	}else{
		*outsize = 17;
	}
	
	Jtt808ConvertRawDataToHeader((uint8_t*)argheader,21,h);

	return 0;
}

/*
 *translate 0x7d to 0x7d 0x01
 *translate 0x7e to 0x7d 0x02
 *@return translate count
 */
int Jtt808Encode0x7eAnd0x7d(uint8_t* inbuf,int insize,uint8_t* outbuf,int* outsize)
{
	int outi = 0;
	int count = 0;
	for (int i=0;i<insize-1;i++)
	{
		if (*(inbuf+i) == 0x7d){
			count += 1;
			*(outbuf+(outi++)) = 0x7d;
			*(outbuf+(outi++)) = 0x01;
		}else if (*(inbuf+i) == 0x7e){
			count += 1;
			*(outbuf+(outi++)) = 0x7d;
			*(outbuf+(outi++)) = 0x02;
		}else{
			*(outbuf+(outi++)) = *(inbuf+i);
		}
	}
	
	*(outbuf+(outi++)) = inbuf[insize-1];

	*outsize = outi;

	return count;
}

/*
 *
 * translate 0x7d 0x01 to 0x7d
 * translate 0x7d 0x02 to 0x7e
 *@return translate count
 */

int Jtt808Decode0x7d01And0x7d02(uint8_t* inbuf,int insize,uint8_t* outbuf,int* outsize)
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
 *
 * convert register struct to raw data
 *
 */
int Jtt808ConvertReigstStructToRawData(jtt808register_t* regist,uint8_t* outbuf,int* outsize)
{

#if BIGENDIAN
	memcpy(outbuf,(uint8_t*)regist,sizeof(jtt808register_t));
	*outsize = sizeof(jtt808register_t);
#else
	jtt808register_t r;
	memcpy(&r,regist,sizeof(jtt808register_t));
	r.provinceId = htons(r.provinceId);
        r.cityId = htons(r.cityId);
	memcpy(outbuf,(uint8_t*)&r,sizeof(jtt808register_t));
	*outsize = sizeof(jtt808register_t);
#endif
	return 0;
}

int Jtt808ConvertPositionStructToRawData(jtt808position_t* pos,uint8_t* outbuf,int* outsize)
{
	memcpy(outbuf,pos,sizeof(jtt808position_t));
	*outsize = sizeof(jtt808position_t);
#ifndef  BIGENDIAN
	pos->alarmFlag = htonl(pos->alarmFlag);
	pos->status = htonl(pos->status);
	pos->latitude = htonl(pos->latitude);
	pos->longitude = htonl(pos->longitude);
	pos->altitude = htons(pos->altitude);
	pos->speed = htons(pos->speed);
	pos->direction = htons(pos->direction);

	memcpy(outbuf,pos,*outsize);
#endif
	return 0;
}

int Jtt808ConvertStructToRawData(uint8_t* stct,int stctsize,uint8_t* outbuf,int* outsize)
{
	memcpy(outbuf,stct,stctsize);
	*outsize = stctsize;
	return 0;
}
