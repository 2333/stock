# -*- coding:utf-8 -*-
import random
import requests
import time
import inspect
from loguru import logger
from requests.exceptions import ProxyError, ConnectTimeout, SSLError
from instock.core.singleton_proxy import proxys

def request_with_retry(url, proxies=None, params=None, headers=None, method="get", max_retry=3, sleep_sec=1, timeout=10):
    caller = inspect.stack()[1].function
    i = 0
    while i < max_retry:
        try:
            if method.lower() == "post":
                r = requests.post(url, proxies=proxies, json=params, timeout=timeout, headers=headers)
            else:
                r = requests.get(url, proxies=proxies, params=params, timeout=timeout, headers=headers)
            if r.status_code == 200:
                return r
            elif r.status_code == 503:
                sec = random.randint(30,60)
                logger.warning(f"[WARN][{caller}] 服务暂时不可用: {r.status_code}, {sec}后第{i+1}次重试...")
                time.sleep(sec)
            else:
                logger.warning(f"[WARN][{caller}] 请求返回码: {r.status_code}, 第{i+1}次重试...")
            i += 1
        except (ProxyError, ConnectTimeout, SSLError) as e:
            logger.warning(f"[PROXY][{caller}] 代理异常: {e}, 尝试更换代理...")
            # 上报并移除异常代理
            if proxies is not None:
                proxys().report_bad_proxy(proxies)
            proxies = proxys().get_proxies()
            # 不递增i，直接更换代理重试
            continue
        except Exception as e:
            logger.error(f"[ERROR][{caller}] 请求异常: {e}, 第{i+1}次重试...")
            i += 1
        time.sleep(sleep_sec)
    logger.error(f"[ERROR][{caller}] 请求失败，已跳过: {url} 参数: {params}")
    return None
