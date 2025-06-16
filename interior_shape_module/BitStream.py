import struct
from TribesToBlender.interior_shape_module import huffman
import math

class BitStream:
    def __init__(self, byte_data):
        self.byte_data = byte_data
        self.bit_ptr = 0

    def burn(self, num_bits):
        self.bit_ptr += num_bits

    def isEOF(self):
        return (len(self.byte_data) * 8 <= self.bit_ptr)

    def read_aligned(self, num_bytes):
        byte_start = self.bit_ptr // 8
        self.bit_ptr += num_bytes * 8
        return BitStream(self.byte_data[byte_start : byte_start + num_bytes])

    def read_bytes(self, num_bytes):
        bt = self.read_bits(num_bytes * 8)
        return bt

    def read_byte_string(self, num_bytes):
        bt = self.read_bits(num_bytes * 8)
        if isinstance(bt, bytearray):
            return bytes(bt)
        return ''.join(bt)

    #  Reads the bits into a byte array
    def read_bits(self, num_bits):
        num_bytes_to_read = ((num_bits - 1)//8 + 1)
        byte_array = []
        curr_byte_index = self.bit_ptr//8
        bit_byte_pos = self.bit_ptr % 8

        self.bit_ptr += num_bits

        # we are lucky, the bits to read and the bit pointer is aligned to a byte
        # if bit_byte_pos == 0 and num_bits % 8 == 0:
        #    return self.byte_data[curr_byte_index : curr_byte_index + num_bytes_to_read]

        # figure out how much of the byte is left hand side and how much right
        rsh = bit_byte_pos
        lsh = 0x8 - rsh
        cbyte = int(self.byte_data[curr_byte_index])
        if len(self.byte_data) == curr_byte_index + 1:
            nbyte = 0
        else:
            nbyte = int(self.byte_data[curr_byte_index + 1])
        for _ in range(num_bytes_to_read):
            new_byte = (cbyte >> rsh) | ((nbyte << lsh) & 0xFF)
            byte_array.append(new_byte)
            cbyte = nbyte
            curr_byte_index += 1
            if len(self.byte_data) <= curr_byte_index + 1:
                nbyte = 0
            else:
                nbyte = self.byte_data[curr_byte_index + 1]

        if num_bits % 8 == 0:
            return bytearray(byte_array)

        # Calculate the mask as we have read some leftover bytes
        mask = ((1 << (num_bits%8)) - 1)
        byte_array[-1] &= mask

        return bytearray(byte_array)

    def read_uint(self, num_bits):
        byte_array = self.read_bits(num_bits)
        if len(byte_array) < 4:
            byte_array.extend([0] * (4 - len(byte_array)))

        if num_bits == 32: # because of course Tribes sometimes reads an uint as an int
            [res] = struct.unpack('i', byte_array)
        else:
            [res] = struct.unpack('I', byte_array)
        return res

    def read_int16(self):
        byte_array = self.read_bits(16)
        [res] = struct.unpack('h', byte_array)
        return res

    def read_normal_vector(self, num_bits):
        self.bit_ptr += num_bits + num_bits + 1

    def read_float(self, num_bits):
        return self.read_uint(num_bits) / ((1 << num_bits) - 1) - 1

    def read_flag(self):
        curr_byte = self.bit_ptr//8
        mask = 1 << (self.bit_ptr % 8)
        self.bit_ptr += 1
        return int(self.byte_data[curr_byte]) & mask != 0

    def read_string(self):
        compressed = self.read_flag()
        str_len = self.read_uint(8)

        if str_len == 0:
            return ""
        res = ""
        if not compressed:
            #simple case, just read str_len * 8 bits
            return self.read_bits(8 * str_len).decode('utf-8', errors="ignore")

        result = huffman.huffman_decode(self, str_len)
        return result

    def read_point3f(self):
        buff = self.read_bits(96)
        [x, y, z] = struct.unpack('fff', buff)
        return (x,y,z)

    def read_point2f(self):
        buff = self.read_bits(64)
        [x, y] = struct.unpack('ff', buff)
        return (x,y)


    def read_colorf(self):
        buff = self.read_bits(96)
        result = struct.unpack('fff', buff)
        return result

    def read_truefloat(self):
        buff = self.read_bits(32)
        result = struct.unpack('f', buff)[0]
        return result

    def read_mat3(self):
        res = [self.read_point3f(), self.read_point3f(), self.read_point3f()]
        return res

    def read_mask(self, num_bits):
        byte_array = self.read_bits(num_bits)
        if len(byte_array) < 4:
            byte_array.extend([0] * (4 - len(byte_array)))

        [res] = struct.unpack('I', byte_array)
        return res

    def read_signed_float(self, num_bits):
        return self.read_uint(num_bits) * 2 / ((1 << num_bits) - 1) - 1

    def read_normal_vector(self, num_bits):
        x = self.read_signed_float(num_bits)
        y = self.read_signed_float(num_bits)
        zsquared = 1 - (x * x) - (y * y)
        if zsquared < 0:
            z = 0
            self.read_flag()
        else:
            z = math.sqrt(zsquared)
            if self.read_flag():
                z = -z
        return [x, y, z]