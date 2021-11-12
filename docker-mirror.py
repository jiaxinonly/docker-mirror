#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 兼容python2和python3
from __future__ import print_function
from __future__ import unicode_literals
from concurrent.futures import TimeoutError

from subprocess import Popen
from os import path, system, mknod
import json
import time
import timeout_decorator
import sys
from getopt import getopt, GetoptError

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
    def __init__(self, image, timeout):
        self.image = image  # 测试用镜像
        self.timeout = timeout
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
        # os.system默认使用sh，不支持kill -SIGHUP，使用kill -1代替，或者使用sudo切换到bash，或者使用/bin/bash -c "kill -SIGHUP"
        system("sudo kill -SIGHUP $(pidof dockerd)")

    # 拉取镜像，超时取消
    def pull_image(self, mirror):
        @timeout_decorator.timeout(self.timeout, timeout_exception=TimeoutError)
        def pull_start():
            pull = ""
            try:
                print("pulling {} from {}".format(self.image, mirror))
                begin_time = time.time()
                pull = Popen("docker pull {}".format(self.image), shell=True)
                exit_code = pull.wait()
                if exit_code == 0:
                    end_time = time.time()
                    cost_time = end_time - begin_time
                    print("mirror {} cost time \033[32m{}\033[0m seconds".format(mirror, cost_time))
                    return cost_time
                else:
                    # 退出码为1
                    # net/http: TLS handshake timeout
                    # image not found
                    return 1000000000

            except TimeoutError:
                pull.kill()
                self.clean_image()
                print("\033[31mTime out {} seconds, skip!\033[0m".format(self.timeout))
                return 666666666

        cost_time = pull_start()
        print("--------------------------------------------")
        return cost_time

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
    image = "busybox:1.34.1"  # 默认拉取的镜像
    timeout = 60  # 默认超过60秒取消
    version = "0.1.1"  # 版本号

    # 获取参数
    try:
        options_list = getopt(sys.argv[1:], "i:t:vh", ["image=", "timeout=", "version", "help"])[0]
        for option, option_value in options_list:
            if option in ("-i", "--image"):
                image = option_value  # 设置要拉取的镜像
            elif option in ("-t", "--timeout"):
                timeout = float(option_value)  # 设置超时时间，并转换为float型数据
                if timeout < 10:  # 超时时间必须大于10秒
                    print("\033[31mError, timeout value must be greater than 10.\033[0m")
                    exit()
            elif option in ("-v", "--version"):
                print("docker-mirror version \033[32m{}\033[0m".format(version))  # 当前版本号
                exit()
            elif option in ("-h", "--help"):
                print("Usage:  docker-mirror [OPTIONS]")
                print("Options:")
                print("   -h, --help".ljust(25), "Print usage")
                print(
                    "   -i, --image string".ljust(25),
                    "Docker image for testing speed, use the default busybox:1.34.1 (e.g., busybox:1.34.1)")
                print("   -t, --timeout float".ljust(25),
                      "Docker pull timeout threshold, must be greater than 10, use the default 60,  (e.g., 88.88)")
                print("   -v, --version".ljust(25), "Print version information and quit")
                exit()

        # 创建类
        docker_client = DockerClient(image, timeout)

        # 读取镜像列表，依次测试速度
        for mirror, mirror_url in mirrors.items():
            docker_client.set_docker_config([mirror_url])  # 设置docker仓库镜像源
            docker_client.docker_reload_config()  # 重载配置
            cost_time = docker_client.speed_test(mirror)  # 测试该镜像源拉取镜像花费时间
            docker_client.result_list.append((mirror, mirror_url, cost_time))  # 保存测试结果
        docker_client.mirror_sort()  # 对测试结果进行排序

        # 输出测试结果
        for mirror in docker_client.result_list:
            if mirror[2] == 666666666:
                print("mirror {}: \033[31mtime out\033[0m".format(mirror[0]))
            elif mirror[2] == 1000000000:
                print("mirror {}: \033[31mpull error\033[0m".format(mirror[0]))
            else:
                print("mirror {}: \033[32m{:.3f}\033[0m seconds".format(mirror[0], mirror[2]))

        if docker_client.result_list[0][2] == 666666666:  # 全部超时
            print("\033[31moh, your internet is terrible, all mirror time out!\033[0m")
            print("Restore the default configuration.")
            docker_client.set_docker_config(mirrors["docker"])
            docker_client.docker_reload_config()
        else:
            print(
                "\033[32mnow, set top three mirrors {}, {}, {} for you.\033[0m".format(docker_client.result_list[0][0],
                                                                                       docker_client.result_list[1][0],
                                                                                       docker_client.result_list[2][0]))
            excellent_mirror_url = [docker_client.result_list[0][1], docker_client.result_list[1][1],
                                    docker_client.result_list[2][1]]
            docker_client.set_docker_config(excellent_mirror_url)
            docker_client.docker_reload_config()

        # 清理镜像
        docker_client.clean_image()

    # 错误的参数输入导致解析错误
    except GetoptError:
        print("Your command is error.")
        print('You can use the "docker-mirror -h" command to get help.')
        exit()
    # timeout的值不为float
    except ValueError:
        print("\033[31mError, timeout value must a number.\033[0m")
        exit()
    # 用户使用ctrl+c取消
    except KeyboardInterrupt:
        print("\033[31m\nUser manual cancel, restore the default configuration.\033[0m")
        docker_client.set_docker_config(mirrors["docker"])
        docker_client.docker_reload_config()
        exit()
