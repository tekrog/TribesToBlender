from TribesToBlender.terrain import helper
from TribesToBlender.terrain import tribes_lzh


class volumer:
    # data_with_filename = []

    def __init__(self):
        self.data_with_filename = None

    def load_binary(self, volume_data):
        if volume_data[:4] != b"PVOL":
            print("Wrong PVOL header")
            return

        # After all the VBLK data is done (so where the footer information begins
        stringBlockOffset = helper.get_old_int(volume_data, 4)  # int.from_bytes(bytes=volume_data[4:8], byteorder='little')

        # Lets read the footer data, as it becomes important later
        if len(volume_data)-4 <= stringBlockOffset:
            print("Missing footer data")
            return

        if volume_data[stringBlockOffset:stringBlockOffset+4] != b"vols":
            print("Wrong VOLS footer")
            return

        curr_data_index = stringBlockOffset+4
        vol_size = helper.get_old_int(volume_data, curr_data_index)
        curr_data_index += 4
        file_name_list = volume_data[curr_data_index:curr_data_index+vol_size].split(b"\x00")

        vol_size = (vol_size + 1) & (~1) # Because Tribes aligns the block size apparently
        curr_data_index += vol_size

        if volume_data[curr_data_index:curr_data_index+4] != b"voli":
            print(f"Wrong Voli footer got: {volume_data[curr_data_index:curr_data_index+4]}")
            return
        curr_data_index += 4  # Consume Voli

        voli_size = helper.get_old_int(volume_data, curr_data_index)
        curr_data_index += 4

        file_name_offset = []
        file_offset = []
        file_size = []
        file_flags = []
        for file_name in file_name_list:
            if file_name == b'':
                continue
            curr_data_index += 4  # These 4 bytes will always be zero in tribes

            file_name_offset.append(helper.get_old_int(volume_data, curr_data_index))
            curr_data_index += 4

            file_offset.append(helper.get_old_int(volume_data, curr_data_index))
            curr_data_index += 4

            file_size.append(helper.get_old_int(volume_data, curr_data_index))
            curr_data_index += 4

            file_flags.append(volume_data[curr_data_index:curr_data_index+1])
            curr_data_index += 1

        # Could have done this in the other loop, but doing it in a separate loop because if I recall I found a few
        # vol files that were misbehaving so keeping it separate so I can easier debug later
        self.data_with_filename = []
        for index in range(0, len(file_name_list)):
            if file_name_list[index] == b'':
                continue
            if volume_data[file_offset[index]:file_offset[index] + 4] != b'VBLK':
                print(f"Wrong VBLK for {file_name_list[index]}")
                continue

            sanity_check_size = helper.get_old_int(volume_data, file_offset[index] + 4)
            if file_flags[index] == b'\x00':
                # Standard non-compressed
                self.data_with_filename.append([file_name_list[index],
                                                volume_data[file_offset[index]+8:file_offset[index] + 8 + file_size[index]]])
            elif file_flags[index] == b'\x01':
                # RLE
                print("Bov hasn't written the code for RLE")
            elif file_flags[index] == b'\x02':
                # LZH
                print("Bov hasn't written the code for LHSS")
            elif file_flags[index] == b'\x03':
                # LHA
                decomp, bytes_read, consumed = tribes_lzh.read_compress_block_vol(volume_data, file_offset[index]+8, file_size[index])
                self.data_with_filename.append([file_name_list[index],decomp])

    def load_file(self, file):
        with open(file, "rb") as file:
            data = file.read()
            return self.load_binary(data)

    def get_file_data(self, target_name, partial_match=False):
        if partial_match:
            for file in self.data_with_filename:
                if target_name in file[0]:
                    return file[1]
        else:
            for file in self.data_with_filename:
                if target_name == file[0]:
                    return file[1]

    def get_file(self, target_name, partial_match=False):
        if partial_match:
            for file in self.data_with_filename:
                if target_name in file[0]:
                    return file
        else:
            for file in self.data_with_filename:
                if target_name == file[0]:
                    return file