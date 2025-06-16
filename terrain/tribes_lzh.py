from TribesToBlender.terrain import helper
from TribesToBlender.interior_shape_module import BitStream

def read_compress_block(data, start_index):
    size = helper.get_old_int(data, start_index)
    start_index += 4

    stream = BitStream.BitStream(data)
    stream.burn(start_index * 8)

    read_data = lzh_read(stream, size)

    # Need to add 4 because of the start_index += 4
    return bytes(read_data), size, stream.bit_ptr // 8 - start_index + 4


def read_compress_block_vol(data, start_index, size):
    stream = BitStream.BitStream(data)
    stream.burn(start_index * 8)

    read_data = lzh_read(stream, size)
    return bytes(read_data), size, stream.bit_ptr // 8 - start_index + 4


LZH_BUFF_SIZE = 4096  # buffer size
LZH_LOOKAHEAD = 60  # lookahead buffer size
LZH_THRESHOLD = 2  # Match len threshhold
LZH_NIL = LZH_BUFF_SIZE  # leaf of tree

LZH_NCHAR = (256 - LZH_THRESHOLD + LZH_LOOKAHEAD)
LZH_TABLE_SIZE = (LZH_NCHAR * 2 - 1)  # size of table
LZH_ROOT = (LZH_TABLE_SIZE - 1)  # position of root
LZH_MAX_FREQ = 0x8000  # updates tree when the root

text_buf = []
freq = []
prnt = []
son = []

d_getbuf = 0
d_getlen = 0
d_putbuf = 0
d_putlen = 0

DI = 0
DJ = 0
DK = 0
DR = 0

curPos = 0

initialized = False
def tribes_lzh_initialize():
    global text_buf
    global freq
    global prnt
    global son
    global initialized

    if initialized:
        return

    initialized = True
    text_buf = [0 for _ in range(LZH_BUFF_SIZE + LZH_LOOKAHEAD - 1)]
    freq = [0 for _ in range(LZH_TABLE_SIZE + 1)]
    prnt = [0 for _ in range(LZH_TABLE_SIZE + LZH_NCHAR)]
    son = [0 for _ in range(LZH_TABLE_SIZE)]


def tribes_lzh_deinitialize():
    global text_buf
    global freq
    global prnt
    global son
    text_buf = [0 for _ in range(LZH_BUFF_SIZE + LZH_LOOKAHEAD - 1)]
    freq = [0 for _ in range(LZH_TABLE_SIZE + 1)]
    prnt = [0 for _ in range(LZH_TABLE_SIZE + LZH_NCHAR)]
    son = [0 for _ in range(LZH_TABLE_SIZE)]

    initialized = False


def huff_reset():
    i = 0
    j = 0

    global d_getbuf
    global d_getlen
    global d_putbuf
    global d_putlen

    global text_buf
    global freq
    global prnt
    global son

    d_getbuf = d_getlen = 0
    d_putbuf = d_putlen = 0

    # Initialize tree

    for i in range(0, LZH_NCHAR):
        freq[i] = 1
        son[i] = i + LZH_TABLE_SIZE
        prnt[i + LZH_TABLE_SIZE] = i

    i = 0
    j = LZH_NCHAR

    while j <= LZH_ROOT:
        freq[j] = freq[i] + freq[i + 1]
        son[j] = i
        prnt[i] = prnt[i + 1] = j
        i += 2
        j += 1

    freq[LZH_TABLE_SIZE] = 0xffff
    prnt[LZH_ROOT] = 0

def reset():
    global DR
    global DJ
    global DK
    global curPos
    global text_buf

    huff_reset()

    for i in range(0, LZH_BUFF_SIZE - LZH_LOOKAHEAD):
        text_buf[i] = -111
    DR = LZH_BUFF_SIZE - LZH_LOOKAHEAD
    DJ = DK = 0
    curPos = 0

def huff_get_bit(input:BitStream.BitStream):
    global d_getlen
    global d_getbuf

    while d_getlen <= 8:
        cc = input.read_bytes(1)[0]
        d_getbuf |= cc << (8 - d_getlen)
        d_getlen += 8
    i = d_getbuf
    d_getbuf <<= 1
    d_getbuf &= 0xFFFF
    d_getlen -= 1

    if i & 0x8000: # Negative is 1
        return 1
    return 0

def huff_reconst():
    global freq, son, prnt

    j = 0
    # Step 1: Collect leaf nodes in the first half of the table
    # and replace freq by (freq + 1) // 2
    for i in range(LZH_TABLE_SIZE):
        if son[i] >= LZH_TABLE_SIZE:
            freq[j] = (freq[i] + 1) // 2
            son[j] = son[i]
            j += 1

    # Step 2: Begin constructing tree by connecting sons
    i = 0
    j = LZH_NCHAR
    while j < LZH_TABLE_SIZE:
        k = i + 1
        f = freq[j] = freq[i] + freq[k]

        k = j - 1
        while f < freq[k]:
            k -= 1
        k += 1

        l = (j - k) * 2
        freq[k + 1:k + 1 + l] = freq[k:k + l]
        freq[k] = f

        son[k + 1:k + 1 + l] = son[k:k + l]
        son[k] = i

        i += 2
        j += 1

    # Step 3: Connect prnt
    for i in range(LZH_TABLE_SIZE):
        k = son[i]
        if k >= LZH_TABLE_SIZE:
            prnt[k] = i
        else:
            prnt[k] = i
            prnt[k + 1] = i

def huff_update(c):
    global freq, son, prnt

    if freq[LZH_ROOT] == LZH_MAX_FREQ:
        huff_reconst()

    c = prnt[c + LZH_TABLE_SIZE]

    while True:
        k = freq[c] + 1
        freq[c] = k

        # If the order is disturbed, exchange nodes
        l = c + 1
        if k > freq[l]:
            while k > freq[l]:
                l += 1
            l -= 1

            # Swap frequencies
            freq[c], freq[l] = freq[l], freq[c]

            # Swap sons and update parents
            i = son[c]
            prnt[i] = l
            if i < LZH_TABLE_SIZE:
                prnt[i + 1] = l

            j = son[l]
            son[l] = i

            prnt[j] = c
            if j < LZH_TABLE_SIZE:
                prnt[j + 1] = c
            son[c] = j

            c = l

        c = prnt[c]
        if c == 0:
            break

def huff_decode_char(input:BitStream.BitStream):
    global son, prnt, freq

    c = son[LZH_ROOT]

    # Travel from root to leaf
    while c < LZH_TABLE_SIZE:
        c += huff_get_bit(input)
        c = son[c]

    c -= LZH_TABLE_SIZE
    huff_update(c)
    return c

d_code = [
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01,
0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01,
0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02,
0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02,
0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03,
0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03,
0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04,
0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05,
0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06,
0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07,
0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08,
0x09, 0x09, 0x09, 0x09, 0x09, 0x09, 0x09, 0x09,
0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A,
0x0B, 0x0B, 0x0B, 0x0B, 0x0B, 0x0B, 0x0B, 0x0B,
0x0C, 0x0C, 0x0C, 0x0C, 0x0D, 0x0D, 0x0D, 0x0D,
0x0E, 0x0E, 0x0E, 0x0E, 0x0F, 0x0F, 0x0F, 0x0F,
0x10, 0x10, 0x10, 0x10, 0x11, 0x11, 0x11, 0x11,
0x12, 0x12, 0x12, 0x12, 0x13, 0x13, 0x13, 0x13,
0x14, 0x14, 0x14, 0x14, 0x15, 0x15, 0x15, 0x15,
0x16, 0x16, 0x16, 0x16, 0x17, 0x17, 0x17, 0x17,
0x18, 0x18, 0x19, 0x19, 0x1A, 0x1A, 0x1B, 0x1B,
0x1C, 0x1C, 0x1D, 0x1D, 0x1E, 0x1E, 0x1F, 0x1F,
0x20, 0x20, 0x21, 0x21, 0x22, 0x22, 0x23, 0x23,
0x24, 0x24, 0x25, 0x25, 0x26, 0x26, 0x27, 0x27,
0x28, 0x28, 0x29, 0x29, 0x2A, 0x2A, 0x2B, 0x2B,
0x2C, 0x2C, 0x2D, 0x2D, 0x2E, 0x2E, 0x2F, 0x2F,
0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37,
0x38, 0x39, 0x3A, 0x3B, 0x3C, 0x3D, 0x3E, 0x3F
]

d_len = [
0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03,
0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03,
0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03,
0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03,
0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04,
0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04,
0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04,
0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04,
0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04,
0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04,
0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05,
0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05,
0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05,
0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05,
0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05,
0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05,
0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05,
0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05,
0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06,
0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06,
0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06,
0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06,
0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06,
0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06,
0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07,
0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07,
0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07,
0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07,
0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07,
0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07,
0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08,
0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08]

def huff_get_byte(pInput):
    global d_getbuf, d_getlen

    while d_getlen <= 8:
        cc = pInput.read_bytes(1)[0]  # Assuming this reads a single byte as int (0–255)
        d_getbuf |= cc << (8 - d_getlen)
        d_getlen += 8

    i = d_getbuf
    d_getbuf <<= 8
    d_getlen -= 8

    return (i >> 8) & 0xFF  # Ensure return value is in 0–255


def huff_decode_position(input_stream : BitStream.BitStream):
    # Recover upper 6 bits from table
    i = huff_get_byte(input_stream)
    c = d_code[i] << 6
    j = d_len[i]

    # Read lower 6 bits verbatim
    j -= 2

    while j > 0:
        huff_bit = huff_get_bit(input_stream)
        #print(huff_bit)
        i = (i << 1) + huff_bit
        j -= 1

    return c | (i & 0x3F)

def lzh_read(input_stream : BitStream.BitStream, length):
    global curPos, DK, DR, text_buf, DI, DJ
    reset()
    count = 0
    data = [0 for _ in range(0,length)]

    if length == 0:
        return 1

    while True:
        while DK < DJ:
            c = text_buf[(DI + DK) & (LZH_BUFF_SIZE  - 1)]

            if c == -111:
                print(count)

            data[count] = c
            count += 1

            text_buf[DR] = c
            DR += 1
            DR &= (LZH_BUFF_SIZE - 1)
            DK += 1
            curPos += 1

            if count == length:
                return data

        while True:
            #First valid should be 221
            c = huff_decode_char(input_stream)
            if c >= 256:
                break

            data[count] = c
            count += 1

            text_buf[DR] = c
            DR += 1
            DR &= (LZH_BUFF_SIZE - 1)

            curPos += 1

            if count == length:
                return data

        DI = (DR - huff_decode_position(input_stream) - 1) & (LZH_BUFF_SIZE - 1)
        DJ = c - 255 + LZH_THRESHOLD
        DK = 0


tribes_lzh_initialize()