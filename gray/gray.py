#!/usr/bin/env python3
"""gray to bin
"""

class gray():
    def to_bin(self,bit_width=22):
        gray = ['' for i in range(bit_width)]
        for i in range(bit_width):
            gray[i] = 'g[' + str(i).zfill(2) + ']'
        print(gray)
        for i in range(bit_width):
            for j in range(i+1,bit_width):
                gray[i] += '^' + gray[j]
        for i in range(bit_width):
            print(gray[i])


if __name__ == '__main__':
    gray = gray()
    gray.to_bin()
