# -*- coding:utf-8 -*-

import math
import io


class Separate():
    def __init__(self, k, v):
        self.content = []
        n = len(v)
        block = io.BytesIO()
        i = 0
        while i <= math.ceil(n / 1000000):
            block = v[1000000 * i:1000000 * (i + 1)]
            self.content += block
            i+=1
        return(k, self.content)