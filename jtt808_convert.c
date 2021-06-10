#include "jtt808_convert.h"

/*
 *
 * convert data to header
 */
int JTT808ConvertRawDataToHeader(jtt808header_t* header,uint8_t* data,int size)
{
	jtt808header_t* h = (jtt808header_t*)data;

	if (size < 17){
		return -1;
	}

	if ((data[3] & 0x20) && size < 21){
		return -1;
	}

	if (data[3] & 0x20)
		memcpy(header,h,21);
	else
		memcpy(header,h,17);

#if  BIGENDIAN

#else
	uint16_t* setval= (uint16_t*)&header->msgBodyProperty;
	uint16_t* getval = (uint16_t*)&h->msgBodyProperty;
	*setval = htons(*getval);

	header->msgId = htons(h->msgId);
	header->flowId = htons(h->flowId);

	if (data[3] & 0x20){
		header->msgPkgItem.pkgCount = htons(h->msgPkgItem.pkgCount);
		header->msgPkgItem.pkgNumber = htons(h->msgPkgItem.pkgNumber);
	}
#endif
	return 0;
}


