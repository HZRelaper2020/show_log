#ifndef  __JTT808_ACTION_H
#define __JTT808_ACTION_H

#include "jtt808_common.h"

jtt808err_t Jtt808DoActionRegister(jtt808handle_t* handle,jtt808header_t* header,jtt808register_t* regist);

jtt808err_t Jtt808DoActionSendHeartPacket(jtt808handle_t* handle,jtt808header_t* header);

jtt808err_t Jtt808DoActionSendPosition(jtt808handle_t* handle,jtt808header_t* header,jtt808position_t* pos);

jtt808err_t Jtt808DoActionSendAccelerationA1(jtt808handle_t* handle,jtt808header_t* header,jtt808accelerationA1_t* acce);

jtt808err_t Jtt808DoActionSendAccelerationC1(jtt808handle_t* handle,jtt808header_t* header,jtt808accelerationC1_t* acce);

jtt808err_t Jtt808DoActionSendOtherData(jtt808handle_t* handle,jtt808header_t* header,jtt808otherData_t * other);


#endif


