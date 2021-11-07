# docker-mirror

查找国内最快的docker镜像源。

Python编写，需要**root**权限，支持Centos 7.5，其他操作系统还未测试。

脚本会自动从收集的镜像列表下载`busybox:1.34.1`镜像，并计算使用的时间，如果超过60s则跳过，对测试结果根据时间进行排序，为你自动设置时间最短的前三个镜像源，**请勿在生产环境使用**。

---

## 使用教程

### 二进制（推荐）

1. 下载二进制包[docker-mirror.tar.gz](https://github.com/jiaxinonly/docker-mirror/releases/download/0.1.0/docker-mirror.tar.gz)

2. 解压包

   ```shell
   tar -xzvf docker-mirror.tar.gz
   ```

3. 执行

   ```shell
   ./docker-mirror
   ```

   ![测试结果](https://source.accepted.fun/image/article/image-20211107183157773.png)

---

### 源码

> 支持python2和python3

1. 安装yum源和python-pip，如果有python和pip环境请跳过

   ```shell
   yum install -y epel-release
   yum install -y python-pip
   ```

2. pip安装依赖

   ```shell
   pip install futures timeout-decorator -i https://mirrors.aliyun.com/pypi/simple
   ```

3. 下载[docker-mirror.py](https://raw.githubusercontent.com/jiaxinonly/docker-mirror/main/docker-mirror.py) 文件到本地

2. 执行脚本

   ```shell
   python docker-mirror.py
   ```

   ![测试结果](https://source.accepted.fun/image/article/image-20211107183157773.png)

---

## 目前收录的国内镜像源

docker官方中国镜像源：https://registry.docker-cn.com

Azure镜像源：https://dockerhub.azk8s.cn

腾讯云镜像源：https://mirror.ccs.tencentyun.com

道客镜像源：https://f1361db2.m.daocloud.io

网易镜像源：https://hub-mirror.c.163.com

中科大镜像源：https://docker.mirrors.ustc.edu.cn

阿里云镜像源：https://tzqukqlm.mirror.aliyuncs.com

七牛云镜像源：https://reg-mirror.qiniu.com