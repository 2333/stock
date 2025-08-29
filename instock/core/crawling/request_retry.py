# -*- coding:utf-8 -*-
import random
import requests
import time

import inspect

def request_with_retry(url, proxies=None, params=None, headers=None, method="get", max_retry=3, sleep_sec=1, timeout=10):
    caller = inspect.stack()[1].function
    for i in range(max_retry):
        try:
            if method.lower() == "post":
                r = requests.post(url, proxies=proxies, json=params, timeout=timeout, headers=headers)
            else:
                r = requests.get(url, proxies=proxies, params=params, timeout=timeout, headers=headers)
            if r.status_code == 200:
                return r
            elif r.status_code == 441:
                # 针对并发过大进行随机等待
                sec = random.randint(1,10)
                print(f"[WARN][{caller}] 请求被限制: {r.status_code}, {sec}后第{i+1}次重试...")
                time.sleep(sec)
            else:
                print(f"[WARN][{caller}] 请求返回码: {r.status_code}, 第{i+1}次重试...")
        except Exception as e:
            print(f"[ERROR][{caller}] 请求异常: {e}, 第{i+1}次重试...")
        time.sleep(sleep_sec)
    print(f"[ERROR][{caller}] 请求失败，已跳过: {url} 参数: {params}")
    return None
