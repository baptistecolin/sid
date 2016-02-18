# -*- coding:utf-8 -*-

import file, ssh, imaps, webdav


class Raid5():
    def __init__(self, stores):
        self.size=len(stores)
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
            #print(value)
            for j in range(1, self.size-1):
                value ^= parts[j][i]
            control_sum += bytearray(chr(value).encode('ASCII'))
        parts.append(control_sum)

        for i in range(self.size):
            self.store[i].put(k + "-" + str(i+1), parts[i])


def main():
    server=file.File('.')
    raid5 = Raid5([server,server,server])
    raid5.put('helloworld',
              b'lablablab')


if __name__ == '__main__':
    main()
