# -*- coding:utf-8 -*-

import file, ssh, imaps, webdav


class Raid5():
    def __init__(self, stores):
        self.size=len(stores)
		# 2 stores ok, more or less raid1?
		assert self.size >= 2, "at least to disks for RAID5"
        self.store = stores

    def put(self, k, v):
        len_v = len(v)
        block_size = (len_v + self.size - 2) // (self.size - 1)
        last_padding = block_size * (self.size - 1) -len_v
        parts = []
        for i in range(self.size-2):
            parts.append(v[i*block_size:(i+1)*block_size]+bytearray(chr(1).encode('ASCII')))
        parts.append(v[(self.size - 2)*block_size:] + bytearray((chr(last_padding+1) * (last_padding+1)).encode('ASCII')))

        # xor
        control_sum = b''
        for i in range(block_size+1):
            value=parts[0][i]
            for j in range(1, self.size-1):
                value ^= parts[j][i]
            control_sum += bytearray(chr(value).encode('ASCII'))
        parts.append(control_sum)

        for i in range(self.size):
            self.store[i].put(k, parts[i])

    def get(self, k):
        content=[]
        error=[]
        for i in range(self.size):
            try:
                value = self.store[i].get(k)
                assert value is not None
            except FileNotFoundError:
                value = None
                error.append(i)
            content.append(value)
        assert len(error) <= 1,"Impossible de reconstituer le fichier, trop de parties manquantes"
        if len(error) == 1:
            recovery = None
            for i in range(len(content)):
                if content[i] is None: # skip
                    continue
                if recovery is None:
                    recovery = bytearray(content[i])
                else:
                    # combine: recovery ^= content
                    for j in range(len(recovery)):
                            recovery[j] ^= content[i][j]
            content[error[0]] = recovery
        output=content[0][:-1]
        for i in range(1,self.size-2):
            output+=content[i][:-1]
        last_padding=int(content[self.size-2][-1])
        output+=content[self.size-2][:-last_padding]
        return output

    def delete(self,k):
        for i in range(self.size):
            try:
                self.store[i].delete(k)
            except:
                print("raid5: backend %d missing key %s" % (i, k))


def main():
    server=file.File('.')
    raid5 = Raid5([server,server,server])
    raid5.put('helloworld',b'lablablab')
    input('effacer un des fichiers...')
    print(raid5.get('helloworld'))

if __name__ == '__main__':
    main()
