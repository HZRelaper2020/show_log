### jtt808开头的都是关于jtt808协议的
#### 基础功能
* 注册
* 发送心跳包
* 传输gps数据
* 传输三轴传感器数据
* 传输六轴传感器数据


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
