#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os.path
import random
import sys
from instock.lib.singleton_type import singleton_type
from loguru import logger
from concurrent.futures import ThreadPoolExecutor, as_completed

# 在项目运行时，临时将项目路径添加到环境变量
cpath_current = os.path.dirname(os.path.dirname(__file__))
cpath = os.path.abspath(os.path.join(cpath_current, os.pardir))
sys.path.append(cpath)
proxy_filename = os.path.join(cpath_current, 'config', 'proxy.txt')

__author__ = 'myh '
__date__ = '2025/1/6 '


# 读取代理
class proxys(metaclass=singleton_type):
    def report_bad_proxy(self, proxy):
        """上报异常代理并移除，支持dict格式"""
        if isinstance(proxy, dict):
            # 还原为字符串格式
            try:
                proxy_str = proxy['http'].replace('http://','')
            except Exception:
                logger.warning(f"report_bad_proxy参数异常: {proxy}")
                return
        else:
            proxy_str = proxy
        if proxy_str in self.data:
            self.data.remove(proxy_str)
            logger.info(f"移除异常代理: {proxy_str}")
            self.save_proxies(self.data)
    def ensure_pool(self):
        """补充代理池到目标数量"""
        if not self.data or len(self.data) < self.min_size:
            need_count = self.pool_size - len(self.data) if self.data else self.pool_size
            logger.info(f"代理池数量不足{self.min_size}，补充{need_count}条代理")
            self.fetch_and_save_proxies(need_count, append=True)
            self.data = self.test_proxies(self.load_proxies())
            self.save_proxies(self.data)
            if not self.data:
                logger.error("补充代理后仍无可用代理")
    def __init__(self):
        self.api_url_base = 'http://api2.uuhttp.com:39003/index/api/return_data?mode=http&connect_type=account&show_up=1&b_time=450&return_type=1&line_break=1&balance=0&secert=MTM4MTEyNzU3Mzc6Mzg2YWQ0ZjY3MzZkNjQxZDE0M2E2MGM1ZmU2Zjk5ZDQ%3D'
        self.test_url = 'http://myip.ipip.net'
        self.proxy_filename = proxy_filename
        self.pool_size = 20
        self.min_size = 10
        # 先加载代理并检测有效性
        proxies = self.load_proxies()
        self.data = self.test_proxies(proxies) if proxies else []
        self.save_proxies(self.data)
        # 再补充代理池
        self.ensure_pool()

    def fetch_and_save_proxies(self, count, append=False):
        import requests
        api_url = f'{self.api_url_base}&count={count}'
        try:
            resp = requests.get(api_url, timeout=10)
            if resp.status_code == 200:
                proxies = resp.text.strip().split()
                if append:
                    # 追加到现有代理池
                    current = set(self.load_proxies())
                    proxies = [p for p in proxies if p not in current]
                    all_proxies = list(current) + proxies
                    self.save_proxies(all_proxies)
                else:
                    self.save_proxies(proxies)
            else:
                logger.error(f"代理API响应异常: {resp.status_code}")
        except Exception as e:
            logger.error(f"获取代理失败: {e}")

    def load_proxies(self):
        if not os.path.exists(self.proxy_filename):
            return []
        with open(self.proxy_filename, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]

    def save_proxies(self, proxies):
        with open(self.proxy_filename, 'w', encoding='utf-8') as f:
            for proxy in proxies:
                f.write(proxy + '\n')

    def test_proxies(self, proxies):
        import requests
        valid = []
        def test_one(proxy_str):
            try:
                user_pass, host_port = proxy_str.split('@')
                user, password = user_pass.split(':')
                ip, port = host_port.split(':')
                proxy = {
                    'http': f'http://{user}:{password}@{ip}:{port}',
                    'https': f'http://{user}:{password}@{ip}:{port}'
                }
                resp = requests.get(self.test_url, proxies=proxy, timeout=5)
                if resp.status_code == 200:
                    return proxy_str
                else:
                    logger.info(f"代理不可用: {proxy_str} 响应码: {resp.status_code}")
            except Exception as e:
                logger.info(f"代理不可用: {proxy_str} 错误: {e}")
            return None

        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_proxy = {executor.submit(test_one, p): p for p in proxies}
            for future in as_completed(future_to_proxy):
                result = future.result()
                if result:
                    valid.append(result)
        return valid

    def get_data(self):
        return self.data

    def get_proxies(self):
        self.ensure_pool()
        if not self.data:
            return None
        proxy_str = random.choice(self.data)
        user_pass, host_port = proxy_str.split('@')
        user, password = user_pass.split(':')
        ip, port = host_port.split(':')
        proxy = {
            'http': f'http://{user}:{password}@{ip}:{port}',
            'https': f'http://{user}:{password}@{ip}:{port}'
        }
        return proxy

"""
    def get_proxies(self):
        if self.data is None:
            return None

        while len(self.data) > 0:
            proxy = random.choice(self.data)
            if https_validator(proxy):
                return {"http": proxy, "https": proxy}
            self.data.remove(proxy)

        return None


from requests import head
def https_validator(proxy):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
               'Accept': '*/*',
               'Connection': 'keep-alive',
               'Accept-Language': 'zh-CN,zh;q=0.8'}
    proxies = {"http": f"{proxy}", "https": f"{proxy}"}
    try:
        r = head("https://data.eastmoney.com", headers=headers, proxies=proxies, timeout=3, verify=False)
        return True if r.status_code == 200 else False
    except Exception as e:
        return False
"""
