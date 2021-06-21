### jtt808开头的都是关于jtt808协议的
#### 基础功能
* 注册
* 发送心跳包
* 传输gps数据
* 传输三轴传感器数据
* 传输六轴传感器数据

#### 客户端使用(C语言)
* 拷贝.c及.h文件，并 include此目录，以便包含.h文件
* linux或arm (jtt808_common.h 第三行 ARMGCC 1就是选择arm, 删除就是 ubuntu)
* jtt808_action.c下面有个main函数，里面有注册等一系列test,填写相应的结构体即可
   *  注册是根据 终端ID(terminalId)进行注册的
   *  心跳包， Jtt808SendActionSendHeartPacket()
   *   gps,填写 jtt808position_t结构体,调用 Jtt808DoActionSendPosition
   *  加速度，填写 jtt808accleration?结构体, ? 可以是A1或C1


#### 服务器 (python)
* py jtt808_main.py


<br/><br/><br/><br/><br/><br/>
### client.py 解析log数据
运行 py client.py arg1 arg2<br/>
&nbsp;&nbsp;&nbsp;&nbsp;arg1表示要输入hex的文件<br/> 
&nbsp;&nbsp;&nbsp;&nbsp;arg2  0 表示画三轴的图，1 表示画6轴的图<br/>
&nbsp;&nbsp;&nbsp;&nbsp;运行之后会在当前目录产生三个txt文件

<p>安装python<p>
 &nbsp;&nbsp;&nbsp;&nbsp;官网下载 https://www.python.org/<br/> 
  &nbsp;&nbsp;&nbsp;&nbsp;安装好之后，安装需要的库，打开命令行输入如下 <br/>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;py -m pip install matplotlib<br/>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;py -m pip install numpy<br/>
