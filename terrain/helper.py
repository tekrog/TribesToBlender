import struct


def get_int(data, byte_offset_arr):
    res = int.from_bytes(bytes=data[byte_offset_arr[0]:byte_offset_arr[0] + 4], byteorder='little')
    byte_offset_arr[0] += 4
    return res

def get_uint(data, byte_offset_arr):
    [res] = struct.unpack('I', data[byte_offset_arr[0]:byte_offset_arr[0] + 4])
    byte_offset_arr[0] += 4
    return res

def get_int16(data, byte_offset_arr):
    [res] = struct.unpack('h', data[byte_offset_arr[0]:byte_offset_arr[0] + 2])
    byte_offset_arr[0] += 2
    return res

def get_uint16(data, byte_offset_arr):
    [res] = struct.unpack('H', data[byte_offset_arr[0]:byte_offset_arr[0] + 2])
    byte_offset_arr[0] += 2
    return res

def get_uint8(data, byte_offset_arr):
    [res] = struct.unpack('B', data[byte_offset_arr[0]:byte_offset_arr[0] + 1])
    byte_offset_arr[0] += 1
    return res

def get_int8(data, byte_offset_arr):
    [res] = struct.unpack('b', data[byte_offset_arr[0]:byte_offset_arr[0] + 1])
    byte_offset_arr[0] += 1
    return res

def get_float(data, byte_offset_arr):
    [res] = struct.unpack('f', data[byte_offset_arr[0]:byte_offset_arr[0] + 4])
    byte_offset_arr[0] += 4
    return res


def get_byte_array(data, array_size, byte_offset_arr):
    res = data[byte_offset_arr[0]:byte_offset_arr[0] + array_size]
    byte_offset_arr[0] += array_size
    return res

def get_float_array(data, array_size, byte_offset_arr):
    array_res = []
    for i in range(0, array_size):
        [res] = struct.unpack('f', data[byte_offset_arr[0]:byte_offset_arr[0] + 4])
        byte_offset_arr[0] += 4
        array_res.append(res)
    return array_res

def get_float3d(data, byte_offset_arr):
    [x, y, z] = struct.unpack('fff', data[byte_offset_arr[0]:byte_offset_arr[0] + 12])
    byte_offset_arr[0] += 12
    return (x,y,z)

def get_float2d(data, byte_offset_arr):
    [x, y] = struct.unpack('ff', data[byte_offset_arr[0]:byte_offset_arr[0] + 8])
    byte_offset_arr[0] += 8
    return (x,y)

def get_old_int(data, byte_offset):
    return int.from_bytes(bytes=data[byte_offset:byte_offset+4], byteorder='little')

def get_old_int16(data, byte_offset):
    [res] = struct.unpack('h', data[byte_offset:byte_offset+2])
    return res

def get_old_float(data, byte_offset):
    [res] = struct.unpack('f', data[byte_offset:byte_offset+4])
    return res

def get_old_float3d(data, byte_offset):
    [x, y, z] = struct.unpack('fff', data[byte_offset:byte_offset+12])
    return (x,y,z)

def get_bit_string(data):
    res = ""
    return res.join([str(get_bit(data, i)) for i in range(len(data) * 8)])

def get_bit(data, bit_offset):
    byte_offset = int(bit_offset // 8)
    position = int(bit_offset % 8)
    return (data[byte_offset] >> position) & 0x1

def bit_read_flag(bits, bit_offset):
    bit = bits[bit_offset[0]]
    bit_offset[0] += 1
    if bit == 1:
        return True
    return False

def bit_read_uint(bits, bit_offset, bits_to_read):
    res = int(bits[bit_offset[0]:bit_offset[0] + bits_to_read], 2)
    bit_offset[0] += bits_to_read
    return res

def bit_burn(bits, bit_offset, bits_to_burn):
    bit_offset[0] += bits_to_burn

