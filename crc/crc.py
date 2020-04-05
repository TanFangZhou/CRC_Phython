#!/usr/bin/env python3
"""calculate crc values
"""

class crc():
    def bit_reverse(self, data, bits=32):
        data_r = 0
        for i in range(bits):
            data_r <<= 1
            if data & 1:
                data_r |= 1
            data >>= 1
        return data_r

    def bit_reverse_test(self):
        data = 0x87654321
        data_r = self.bit_reverse(data)
        print('Function \'bit_reverse()\' testing:')
        print('before:', hex(data).zfill(8).upper(), bin(data)[2:].zfill(32))
        print('after :', hex(data_r).zfill(8).upper(), bin(data_r)[2:].zfill(32))

    def table_gen(self, data_bit=8, poly_bit=32, poly=0x04C11DB7, refin=1):
        data_max = 2 ** data_bit - 1
        poly_max = 2 ** poly_bit - 1
        table = list(0 for i in range(data_max + 1))
        crc = 0
        if refin:
            poly = self.bit_reverse(poly, poly_bit)
            for i in range(data_max + 1):
                crc = i
                for j in range(data_bit):
                    if crc & 1:
                        crc >>= 1
                        crc ^= poly
                    else:
                        crc >>= 1
                table[i] = crc & poly_max
        else:
            if poly_bit > data_bit:
                crc_msb = 1 << (poly_bit - 1)
                shift_data = poly_bit - data_bit
                shift_crc = 0
            else:
                crc_msb = 1 << (data_bit - 1)
                shift_data = 0
                shift_crc = data_bit - poly_bit
            poly <<= shift_crc
            for i in range(data_max + 1):
                crc = i << shift_data
                for j in range(data_bit):
                    if crc & crc_msb:
                        crc <<= 1
                        crc ^= poly
                    else:
                        crc <<= 1
                crc >>= shift_crc
                table[i] = crc & poly_max
        return table

    def data_msb(self,data):
        bits = 0
        while data:
            bits += 1
            data >>= 1
        return bits

    def list_max(self, list):
        max = 0
        for i in range(len(list)):
            if max < list[i]:
                max = list[i]
        return max

    def table_show(self, table, coloum=4):
        table_max = self.list_max(table)
        bits = self.data_msb(table_max)
        if bits & 0x3:
            bits = (bits >> 2) + 1
        else:
            bits >>= 2
        for i in range(len(table)):
            print(hex(table[i]).upper()[2:].zfill(bits), end=' ')
            if i % coloum == (coloum - 1):
                print()

    def crc_cal_dir(self, list0, data_bit=8, poly_bit=32, poly=0x04C11DB7, refin=1, refout=1, init=0xFFFFFFFF, xrout=0xFFFFFFFF):
        crc = 0
        crc_mask = 2 ** poly_bit - 1
        init &= crc_mask
        len_d = len(list0)
        if poly_bit > data_bit:
            crc_msb = poly_bit - 1
            shift_data = poly_bit - data_bit
            shift_crc = 0
        else:
            crc_msb = data_bit - 1
            shift_data = 0
            shift_crc = data_bit - poly_bit
        if poly_bit > data_bit:
            bytes = poly_bit // data_bit
        else:
            bytes = 1
        if len_d < bytes:
            len_i = len_d
        else:
            len_i = bytes
        if refin:
            for i in range(len_i):
                crc = (crc >> data_bit) | (list0[i] << shift_data)
            crc >>= data_bit * (bytes - len_i)
            poly = self.bit_reverse(poly, poly_bit)
            init = self.bit_reverse(init, poly_bit)
            crc ^= init
            for i in range(bytes, len_d):
                data_t = list0[i]
                for j in range(data_bit):
                    tap = crc & 1
                    crc >>= 1
                    if data_t & 1:
                        crc |= (1 << crc_msb)
                    data_t >>= 1
                    if tap:
                        crc ^= poly
            for i in range(len_i * data_bit):
                if crc&1:
                    crc >>= 1
                    crc ^= poly
                else:
                    crc >>= 1
            if refout == 0:
                crc = self.bit_reverse(crc, poly_bit)
        else:
            for i in range(len_i):
                crc = (crc << data_bit) | list0[i]
            crc <<= data_bit * (bytes - len_i)
            crc ^= init
            poly <<= shift_crc
            for i in range(bytes, len_d):
                data_t = list0[i]
                for j in range(data_bit):
                    tap = crc & (1 << crc_msb)
                    crc <<= 1
                    if data_t & (1 << (data_bit - 1)):
                        crc |= 1
                    data_t <<= 1
                    if tap:
                        crc ^= poly
            for i in range(len_i*data_bit):
                if crc & (1 << crc_msb):
                    crc <<= 1
                    crc ^= poly
                else:
                    crc <<= 1
            crc >>= shift_crc
            if refout:
                crc = self.bit_reverse(crc, poly_bit)
        crc ^= xrout
        crc &= crc_mask
        return crc

    def crc_cal_table(self, list0, data_bit=8, poly_bit=32, poly=0x04C11DB7, refin=1, refout=1, init=0xFFFFFFFF, xrout=0xFFFFFFFF):
        crc = 0
        crc_mask = 2 ** poly_bit - 1
        data_mask = 2 ** data_bit - 1
        init &= crc_mask
        len_d = len(list0)
        table = self.table_gen(data_bit, poly_bit, poly, refin)
        if poly_bit > data_bit:
            shift_data = poly_bit - data_bit
            shift_crc = 0
        else:
            shift_data = 0
            shift_crc = data_bit - poly_bit
        if poly_bit > data_bit:
            bytes = poly_bit // data_bit
        else:
            bytes = 1
        if len_d < bytes:
            len_i = len_d
        else:
            len_i = bytes
        if refin:
            for i in range(len_i):
                crc = (crc >> data_bit) | (list0[i] << shift_data)
            crc >>= data_bit * (bytes - len_i)
            init = self.bit_reverse(init, poly_bit)
            crc ^= init
            for i in range(bytes, len_d):
                data_t = list0[i] << shift_data
                crc = ((crc >> data_bit) | data_t) ^ table[crc & data_mask]
            for i in range(len_i):
                crc = (crc >> data_bit) ^ table[crc & data_mask]
            if refout==0:
                crc = self.bit_reverse(crc, poly_bit)
        else:
            for i in range(len_i):
                crc = (crc << data_bit) | list0[i]
            crc <<= data_bit * (bytes - len_i)
            crc ^= init
            for i in range(bytes, len_d):
                data_t = list0[i]
                crc = (crc << data_bit | data_t) ^ (table[(crc >> shift_data) & data_mask] << shift_crc)
            for i in range(len_i):
                crc = (crc << data_bit) ^ (table[(crc >> shift_data) & data_mask] << shift_crc)
            crc >>= shift_crc
            if refout:
                crc = self.bit_reverse(crc, poly_bit)
        crc ^= xrout
        crc &= crc_mask
        return crc

    def crc_cal_table_opt(self, list0, data_bit=8, poly_bit=32, poly=0x04C11DB7, refin=1, refout=1, init=0xFFFFFFFF, xrout=0xFFFFFFFF):
        crc_mask = 2 ** poly_bit - 1
        data_mask = 2 ** data_bit - 1
        init &= crc_mask
        len_d = len(list0)
        table = self.table_gen(data_bit, poly_bit, poly, refin)
        if refin:
            init = self.bit_reverse(init, poly_bit)
            crc = init
            for i in range(len_d):
                crc = (crc >> data_bit) ^ table[(crc ^ list0[i]) & data_mask]
            if refout == 0:
                crc = self.bit_reverse(crc, poly_bit)
        else:
            crc = init
            if poly_bit > data_bit:
                shift_data = poly_bit - data_bit
                shift_crc = 0
            else:
                shift_data = 0
                shift_crc = data_bit - poly_bit
            for i in range(len_d):
                crc = (crc << data_bit) ^ (table[((crc >> shift_data) ^ list0[i]) & data_mask] << shift_crc)
            crc >>= shift_crc
            if refout:
                crc = self.bit_reverse(crc, poly_bit)
        crc ^= xrout
        crc &= crc_mask
        return crc

    def str2int_list(self, string):
        list0 = []
        for i in range(len(string)):
            list0.append(string[i].encode('ascii')[0])
        return list0

    def crc_32(self, list0):
        return self.crc_cal_table_opt(list0)

    def crc_16_usb(self, list0):
        return self.crc_cal_table_opt(list0, poly_bit=16, poly=0x8005, init=0xffff, xrout=0xffff)

    def crc_8(self, list0):
        return self.crc_cal_table_opt(list0, poly_bit=8, poly=0x07, refin=0, refout=0, init=0, xrout=0)

    def crc_4_itu(self, list0):
        return self.crc_cal_table_opt(list0, poly_bit=4, poly=0x3, refin=1, refout=1, init=0, xrout=0)

    def crc_check(self):
        string = '123456789'
        list0 = self.str2int_list(string)
        crc32 = self.crc_32(list0)
        crc16 = self.crc_16_usb(list0)
        crc8 = self.crc_8(list0)
        crc4 = self.crc_4_itu(list0)
        print(string)
        print('CRC-32    :', hex(crc32).zfill(32//4).upper())
        print('CRC-16/USB:', hex(crc16).zfill(16//4).upper())
        print('CRC-8     :', hex(crc8 ).zfill(8 //4).upper())
        print('CRC-4/ITU :', hex(crc4 ).zfill(4 //4).upper())

    def verilog(self, data_bit=8, poly_bit=32, poly=0x04C11DB7, refin=1, debugen=1, xoren=0):
        if data_bit > poly_bit:
            bit = data_bit
        else:
            bit = poly_bit
        crc = ['' for i in range(bit)]
        table = ['' for i in range(bit)]
        if debugen:
            print(crc)
            print(table)
            print()
        for i in range(poly_bit):
            if refin:
                crc[i] = 'c' + str(i)
            else:
                crc[i] = 'c' + str(poly_bit - 1 - i)
        if debugen:
            print(crc)
            print(table)
            print()
        for i in range(data_bit):
            if refin:
                table[i] = 'd' + str(i) + crc[i]
            else:
                table[i] = 'd' + str(data_bit - 1 - i) + crc[i]
            crc.append('')
        crc = crc[data_bit:]
        if debugen:
            print(crc)
            print(table)
            print()
        temp = [1]
        for i in range(data_bit):
            lsb = table[0]
            table = table[1:]
            table.append('')
            tap = 1 << (poly_bit - 1)
            for j in range(poly_bit):
                if tap & poly:
                    temp[0] = table[j] + lsb
                    if xoren:
                        temp = self.str2lst(temp)
                        temp = self.lst_xor(temp)
                        table[j] = self.lst2str_and(temp)[0]
                tap >>= 1
            if debugen:
                print(table)
        if poly_bit<data_bit:
            crc = table[0:poly_bit]
        else:
            for i in range(poly_bit):
                crc[i] += table[i]
            if xoren:
                crc = self.str2lst(crc)
                crc = self.lst_xor(crc)
                crc = self.lst2str_and(crc)
        if refin==0:
            crc.reverse()
        if debugen:
            print(crc)
        return crc

    def lst_xor(self, list0):
        len0 = len(list0)
        for i in range(len0):
            list1 = list0[i]
            len1 = len(list1)
            j = 0
            while j < len1:
                entry = list1[j]
                cnt = list1.count(entry) // 2
                if cnt != 0:
                    cnt *= 2
                    len1 -= cnt
                    for k in range(cnt):
                        list1.remove(entry)
                else:
                    j += 1
        return list0

    def str2lst(self, list0):
        len0 = len(list0)
        list1 = [[] for i in range(len0)]
        for i in range(len0):
            string = list0[i]
            len1 = len(string)
            j = 0
            while j < len1:
                k = j+1
                while k < len1:
                    if string[k].isdecimal():
                        k += 1
                    else:
                        break
                list1[i].append(string[j:k])
                j = k
            list1[i].sort()
        return list1

    def lst2str_xor(self,list0):
        len0 = len(list0)
        list1 = ['' for i in range(len0)]
        for i in range(len0):
            list3 = ''
            list2 = list0[i]
            for j in range(len(list2)):
                list3 += list2[j][0] + '[' + list2[j][1:] + ']^'
            list1[i] = list3[:-1]
        return list1

    def lst2str_and(self,list0):
        len0 = len(list0)
        list1 = ['' for i in range(len0)]
        for i in range(len0):
            list3 = ''
            list2 = list0[i]
            for j in range(len(list2)):
                list3 += list2[j]
            list1[i] = list3
        return list1

    def verilog_show(self,list0):
        for i in range(len(list0)):
            print(list0[i])

    def verilog_check(self, data_bit=32, poly_bit=32, poly=0x1EDC6F41, refin=0, debugen=1, xoren=1):
        table0 = self.verilog(data_bit, poly_bit, poly, refin, debugen, xoren)
        if xoren==0:
            table1 = self.str2lst(table0)
            if debugen:
                print()
                print(table1)
            table2 = self.lst_xor(table1)
            if debugen:
                print()
                print(table2)
                print()
            table3 = self.lst2str_xor(table2)
        else:
            table1 = self.str2lst(table0)
            table3 = self.lst2str_xor(table1)
        self.verilog_show(table3)


if __name__ == '__main__':
    crc = crc()
    crc.verilog_check()

