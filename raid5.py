# -*- coding:utf-8 -*-

from file import *


class Raid5():
    def __init__(self, store):
        self.store = store

    def getKey(self, k, i):
        return '%s--%s' % (k, i)

    def put(self, k, v):
        disk1 = self.store("./" + k + '-1')
        disk2 = self.store("./" + k + '-2')
        disk3 = self.store("./" + k + '-3')

        n = len(v)
        parts = []
        parts.append(v[:n // 2])
        parts.append(v[n // 2:])
        control_sum = b''
        for i in range(0, n // 2):
            control_sum += v[i] ^ v[n // 2 + i]
        parts.append(control_sum)
        if n % 2 != 0: control_sum += v[n]

        disk1.put(self.getKey(k, 1), parts[0])
        disk2.put(self.getKey(k, 2), parts[1])
        disk3.put(self.getKey(k, 3), parts[2])


def main():
    raid5 = Raid5(File('.'))
    raid5.put('helloworld',
              b'blablablabalbalbalbalbalablabalbalbalabalbalbalabalbalablabalbalbalbalablabalbalbalbalbalablabalbalbalbalablabalbalbalbalbalablablablablabalbalblabalbalbalablab')


if __name__ == '__main__':
    main()
