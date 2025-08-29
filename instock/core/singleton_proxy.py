#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os.path
import sys
from instock.lib.singleton_type import singleton_type

# 在项目运行时，临时将项目路径添加到环境变量
cpath_current = os.path.dirname(os.path.dirname(__file__))
cpath = os.path.abspath(os.path.join(cpath_current, os.pardir))
sys.path.append(cpath)
proxy_filename = os.path.join(cpath_current, 'config', 'proxy.txt')

__author__ = 'myh '
__date__ = '2025/1/6 '


# 读取代理
class proxys(metaclass=singleton_type):
    def __init__(self):
        # try:
        #     with open(proxy_filename, "r") as file:
        #         self.data = list(set(line.strip() for line in file.readlines() if line.strip()))
        # except Exception:
        #    pass
        # proxy = "brd-customer-hl_9f40147b-zone-residential_proxy1:0n1pvrenc3mi@brd.superproxy.io:33335"
        proxy = "http://t15636478555787:5bdglxh5@f174.kdltps.com:15818"
        self.proxies = {"http": proxy, "https": proxy}

    def get_data(self):
        return self.data

    def get_proxies(self):
        # if self.data is None or len(self.data)==0:
        #     return None

        # proxy = random.choice(self.data)
        # return {"http": proxy, "https": proxy}
        return self.proxies
