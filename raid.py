# -*- coding:utf-8 -*-


class Raid():
    def __init__(self, version, store):
        if int(version)==10 :
            self.version=int(version)
        self.store=store

    def getKey(self,k,i):
        return '%s--%s'%(k,i)

    def put(self, k, v):
        n = len(v)
        disk1 = self.store("./"+k+'-1')
        disk2 = self.store("./"+k+'-2')
        disk3 = self.store("./"+k+'-3')
        disk4 = self.store("./"+k+'-4')
        parts_number=8
        parts = []
        i=0
        while i<parts_number:
            parts.append(v[n // parts_number * i : n // parts_number * (i + 1)])
            i+=1
        parts.append(v[n // parts_number * parts_number:])
        for i in range(0,8):
            if i%2==0:
                disk1.put(self.getKey(k,i), parts[i])
                disk3.put(self.getKey(k,i), parts[i])
            else :
                disk2.put(self.getKey(k,i), parts[i])
                disk4.put(self.getKey(k,i), parts[i])
