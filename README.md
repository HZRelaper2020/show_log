## 演示版（画图只能连接一个客户端)
### v2 版
* 解析文件 
    * py v2_decode_data.py hex文件
    * 保存文件名会打印出来
* 画图   py v2_draw_data.py 解析出来的文件
* 实时数据传输 py v2_draw_dynamic_script.py log文件
* 解析txt
	*  py v2_draw_data.py struct_A1.txt
	*  py v2_draw_data_col.py struct_A3.txt
	*  修改数据都在 self_process_data 函数里面
<br/><br/><br/><br/>

### jtt808开头的都是关于jtt808协议的
#### 基础功能
* 注册
* 发送心跳包
* 传输gps数据
* 传输三轴传感器数据
* 传输六轴传感器数据
* 传输其它数据如文件等

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
   * 输入 1表示画图传感器a1，2表示画图传感器c1，3表示画图gps，c表示关闭
   * l&emsp;小写的L，打印列出连接的客户端
   * d&emsp;删除全部客户端
   * 空格 &emsp;退出


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
