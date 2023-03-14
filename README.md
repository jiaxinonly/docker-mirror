# docker-mirror

查找最快的docker镜像源:sparkles:

Python编写，需要**root**权限，支持Centos 7/Ubuntu 20/Debain 11，其他操作系统还未测试。

脚本会自动从收集的镜像列表下载`busybox:1.34.1`镜像，并计算使用的时间，如果超过设置的时间则跳过，避免长时间的等待，对测试结果根据时间进行排序，为你自动设置耗时最短的前三个镜像源，**请勿在生产环境中使用**。

## 使用教程

1. 下载二进制包[docker-mirror.tar.gz](https://github.com/jiaxinonly/docker-mirror/releases/latest/download/docker-mirror.tar.gz)

2. 解压包

   ```shell
   tar -xzvf docker-mirror.tar.gz
   ```

3. 执行

   ```shell
   ./docker-mirror
   ```

   ![测试结果](https://source.accepted.fun/image/article/image-20211107183157773.png)

> 你可以使用-i选项指定镜像或使用-t选项指定超时时间，具体请使用-h选项查看帮助

## 目前收录的国内镜像源

docker官方中国镜像源：https://registry.docker-cn.com

Azure镜像源：https://dockerhub.azk8s.cn

腾讯云镜像源：https://mirror.ccs.tencentyun.com

道客镜像源：https://f1361db2.m.daocloud.io

网易镜像源：https://hub-mirror.c.163.com

中科大镜像源：https://docker.mirrors.ustc.edu.cn

阿里云镜像源：https://tzqukqlm.mirror.aliyuncs.com

七牛云镜像源：https://reg-mirror.qiniu.com