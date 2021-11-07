#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 兼容python2和python3
from __future__ import print_function
from __future__ import unicode_literals
from concurrent.futures import TimeoutError

# import subprocess
from subprocess import Popen
from os import path, system, mknod
import json
import time
import timeout_decorator

# 镜像列表
mirrors = {
    "docker": "",  # 使用官方默认
    "docker-cn": "https://registry.docker-cn.com",  # docker官方中国镜像
    "azure": "https://dockerhub.azk8s.cn",
    "tencentyun": "https://mirror.ccs.tencentyun.com",  # 腾讯云
    "daocloud": "https://f1361db2.m.daocloud.io",  # 道客
    "netease": "https://hub-mirror.c.163.com",  # 网易
    "ustc": "https://docker.mirrors.ustc.edu.cn",  # 中科大
    "aliyun": "https://tzqukqlm.mirror.aliyuncs.com",  # 阿里云 请替换为自己的阿里云镜像加速地址
    "qiniu": "https://reg-mirror.qiniu.com"  # 七牛云
}


class DockerClient:
    def __init__(self):
        self.image = "busybox:1.34.1"  # 测试用镜像
        self.config_file = "/etc/docker/daemon.json"  # docker配置文件路径
        self.result_list = []  # 用于存储测试结果

    # 配置docker
    def set_docker_config(self, mirror_url):
        config_dict = {}
        if not path.exists(self.config_file):
            # 如果不存在则创建配置文件
            mknod(self.config_file, 0o644)
            pass
        else:
            # 如果存在则读取参数
            with open(self.config_file, "r") as file:
                config_dict = json.load(file)

        config_dict["registry-mirrors"] = mirror_url

        with open(self.config_file, "w") as file:
            json.dump(config_dict, file)

    @staticmethod
    def docker_reload_config():
        # 热加载docker配置
        system("sudo kill -SIGHUP $(pidof dockerd)")

    # 拉取镜像，超过60秒取消
    @timeout_decorator.timeout(60, timeout_exception=TimeoutError)
    def pull_image(self, mirror):
        pull = ""
        try:
            print("pulling {} from {}".format(self.image, mirror))
            begin_time = time.time()
            pull = Popen("docker pull {}".format(self.image), shell=True)
            pull.wait()
            end_time = time.time()
            cost_time = end_time - begin_time
            print("mirror {} cost time \033[32m{}\033[0m seconds".format(mirror, cost_time))
            return cost_time
        except TimeoutError:
            pull.kill()
            self.clean_image()
            print("\033[31mTime out 60 seconds, skip!\033[0m")
            return 999999999
        finally:
            print("----------------------------")

    def speed_test(self, mirror):
        self.clean_image()
        return self.pull_image(mirror)

    # 对测试结果排序
    def mirror_sort(self):
        self.result_list.sort(key=lambda cost_time: cost_time[2])

    def clean_image(self):
        # 强制删除镜像
        system("docker rmi {} -f > /dev/null 2>&1".format(self.image))


if __name__ == '__main__':
    docker_client = DockerClient()
    for mirror, mirror_url in mirrors.items():
        docker_client.set_docker_config([mirror_url])
        docker_client.docker_reload_config()
        cost_time = docker_client.speed_test(mirror)
        docker_client.result_list.append((mirror, mirror_url, cost_time))
    docker_client.mirror_sort()

    for mirror in docker_client.result_list:
        if mirror[2] == 999999999:
            print("mirror {}: \033[31mtime out\033[0m".format(mirror[0]))
        else:
            print("mirror {}: \033[32m{:.3f}\033[0m seconds".format(mirror[0], mirror[2]))

    if docker_client.result_list[0][2] == 999999999:
        print("\033[31moh, your internet is terrible, all mirror time out!\033[0m")
        print("Restore the default configuration for you.")
        docker_client.set_docker_config(mirrors["docker"])
        docker_client.docker_reload_config()
    else:
        print("\033[32mnow, set top three mirrors {}, {}, {} for you.\033[0m".format(docker_client.result_list[0][0],
                                                                                    docker_client.result_list[1][0],
                                                                                    docker_client.result_list[2][0]))
        excellent_mirror_url = [docker_client.result_list[0][1], docker_client.result_list[1][1],
                                docker_client.result_list[2][1]]
        docker_client.set_docker_config(excellent_mirror_url)
        docker_client.docker_reload_config()

    docker_client.clean_image()