# -*- coding:utf-8 -*-

import math
import io


class Separate():
    def __init__(self, storage, maxsize=1000000):
        self.maxsize = maxsize
        self.storage = storage

    def put(self, k, v):
        self.content = []
        n = len(v)
        i = 0
        while i < n // self.maxsize:
            self.content.append(v[self.maxsize * i:self.maxsize * (i + 1)])
            i+=1
        self.content.append(v[self.maxsize * i:])
        # k ?