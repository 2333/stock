#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from threading import RLock


__author__ = 'myh '
__date__ = '2023/3/10 '


class singleton_type(type):
    single_lock = RLock()

    def __call__(cls, *args, **kwargs):  # 创建cls的对象时候调用
        if getattr(cls, "_instance", None) is None:
            with singleton_type.single_lock:
                if getattr(cls, "_instance", None) is None:
                    cls._instance = super(singleton_type, cls).__call__(*args, **kwargs)
        return cls._instance
