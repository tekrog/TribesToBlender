from TribesToBlender.terrain import helper
from TribesToBlender.terrain import tribes_lzh
from TribesToBlender.terrain import volumer
import numpy as np
#import cv2 as cv


class terrain:
    def __init__(self):
        self.block_map = None
        self.dfl_block_pattern = None
        self.dfl_size_y = None
        self.dfl_size_x = None
        self.height_range_max = None
        self.height_range_min = None
        self.origin_y = None
        self.origin_x = None
        self.bounds_tr = None
        self.bounds_bl = None
        self.scale = None
        self.last_block_id = None
        self.dml_name = None
        self.heightmap = None
        self.detail_count = 0
        self.name_id = ""
        self.light_scale = 0
        self.height_fmin = 1.0
        self.height_fmax = -1.0
        self.size_x = 0
        self.size_y = 0
        self.mat_flags = []
        self.mat_index = []

    def load_dtf_binary(self, data):
        if data[:4] != b"GFIL":
            print("Wrong GFIL header")
            return

        curr_data_index = [4] # Skipping the block size...as I don't think I will use it...after all Tribes doesn't bother

        size_of_block = helper.get_int(data, curr_data_index)
        version = helper.get_int(data, curr_data_index)

        str_len = helper.get_int(data, curr_data_index)
        self.dml_name = data[curr_data_index[0]:curr_data_index[0] + str_len]
        curr_data_index[0] += str_len
        self.last_block_id = helper.get_int(data, curr_data_index)
        self.detail_count = helper.get_int(data, curr_data_index)
        self.scale = helper.get_int(data, curr_data_index)

        self.bounds_bl = helper.get_float3d(data, curr_data_index)
        self.bounds_tr = helper.get_float3d(data, curr_data_index)
        self.origin_x = helper.get_int(data, curr_data_index)
        self.origin_y = helper.get_int(data, curr_data_index)
        self.height_range_min = helper.get_float(data, curr_data_index)
        self.height_range_max = helper.get_float(data, curr_data_index)

        self.dfl_size_x = helper.get_int(data, curr_data_index)
        self.dfl_size_y = helper.get_int(data, curr_data_index)

        if version == 1:
            self.dfl_block_pattern = helper.get_int(data, curr_data_index)

        self.block_map = []
        for i in range(0, self.dfl_size_x * self.dfl_size_y):
            self.block_map.append(helper.get_int(data, curr_data_index))

    def load_binary(self, data):
        if data[:4] != b"GBLK":
            print("Wrong GBLK header")
            return

        curr_data_index = [4]

        size_of_block = helper.get_int(data, curr_data_index)
        gblk_version = helper.get_int(data, curr_data_index)
        self.name_id = data[curr_data_index[0]:curr_data_index[0]+16]
        curr_data_index[0] += 16
        self.detail_count = helper.get_int(data, curr_data_index)
        self.light_scale = helper.get_int(data, curr_data_index)
        self.height_fmin = helper.get_float(data, curr_data_index)
        self.height_fmax = helper.get_float(data, curr_data_index)
        self.size_x = helper.get_int(data, curr_data_index)
        self.size_y = helper.get_int(data, curr_data_index)

        if gblk_version == 0:
            print("Bov hasn't implemented v0 yet...although this should be almost a raw height map without compression")
            return
        if gblk_version < 5:
            print(f"Bov hasn't implemented v{gblk_version} yet...1 Rick0 compression, 2 pin maps, 3 high res light")
            return

        # heightmap decompression
        self.heightmap = np.zeros((self.size_y + 1, self.size_x + 1), np.single)
        decomp, size, bytes_read = tribes_lzh.read_compress_block(data, curr_data_index[0])
        curr_data_index[0] += bytes_read
        decomp_index = [0]
        for i in reversed(range(0, self.size_y + 1)):
            self.heightmap[i:i+1] = helper.get_float_array(decomp, self.size_x + 1, decomp_index)

        # material information
        self.mat_flags = np.zeros((self.size_y, self.size_x), np.uint8)
        self.mat_index = np.zeros((self.size_y, self.size_x), np.uint8)
        decomp, size, bytes_read = tribes_lzh.read_compress_block(data, curr_data_index[0])
        curr_data_index[0] += bytes_read
        for i in range(0, self.size_y):
            self.mat_flags[i:i+1, 0:] = [list(decomp[2 * (self.size_y - i - 1) * self.size_x: 2 * ((self.size_y - i - 1) + 1) * self.size_x: 2])]
            self.mat_index[i:i+1, 0:] = [list(decomp[2 * (self.size_y - i - 1) * self.size_x + 1: 2 * ((self.size_y - i - 1) + 1) * self.size_x: 2])]

        # There are pin maps and light scale stuff...but I don't think there is much use for it
        return True

    def load_file(self, file, file_name_extension = b".ted"):
        if file[-3:] == 'vol':
            volume = volumer.volumer()
            volume.load_file(file)
            return self.load_binary(volume.get_file_data(file_name_extension, True))
        if file[-3:] == 'ted':
            volume = volumer.volumer()
            volume.load_file(file)
            self.load_dtf_binary(volume.get_file_data(b'.dtf', True))
            return self.load_binary(volume.get_file_data(b'.dtb', True))

        print("For a full solution for terrain load a ted file or a vol file with a ted file inside of it."
              "Otherwise you will get partial information")

        with open(file, "rb") as file:
            data = file.read()
            return self.load_binary(data)

    def get_height_0_65535(self, height):
        terrain_total_range = self.height_fmax - self.height_fmin
        return (height - self.height_fmin) / terrain_total_range * 65535

    def get_heightmap_0_65535(self, repeat_size_x = 1, repeat_size_y = 1):
        terrain_total_range = self.height_fmax - self.height_fmin
        res = np.zeros((self.size_y * repeat_size_y + 1, self.size_x * repeat_size_x + 1), np.uint16)
        res[0:self.size_y + 1, 0:self.size_x + 1] = ((self.heightmap - self.height_fmin) / terrain_total_range) * 65535

        for x in range(1, repeat_size_x):
            res[0:self.size_y + 1, x * self.size_x:self.size_x + x * self.size_x + 1] = res[0:self.size_y + 1, 0:self.size_x + 1]
        for y in range(1, repeat_size_y):
            res[y * self.size_y:self.size_y + y * self.size_y + 1, 0:] = res[0:self.size_y + 1, 0:]
        return res

    def get_true_height_range(self):
        return np.min(self.heightmap), np.max(self.heightmap)

    def get_heightmap_image(self):
        return self.get_heightmap_0_65535(1, 1)

    def get_material_map_image(self, repeat_size_x = 1, repeat_size_y = 1):
        res = np.zeros((self.size_y * repeat_size_y, self.size_x * repeat_size_x), np.uint16)
        res[0:self.size_y, 0:self.size_x] = self.mat_index

        for x in range(1, repeat_size_x):
            res[0:self.size_y, x * self.size_x:self.size_x + x * self.size_x] = res[0:self.size_y, 0:self.size_x]
        for y in range(1, repeat_size_y):
            res[y * self.size_y:self.size_y + y * self.size_y, 0:] = res[0:self.size_y, 0:]

        return res

    def get_material_flags_image(self, repeat_size_x = 1, repeat_size_y = 1):
        res = np.zeros((self.size_y * repeat_size_y, self.size_x * repeat_size_x), np.uint16)
        res[0:self.size_y, 0:self.size_x] = self.mat_flags

        for x in range(1, repeat_size_x):
            res[0:self.size_y, x * self.size_x:self.size_x + x * self.size_x] = res[0:self.size_y, 0:self.size_x]
        for y in range(1, repeat_size_y):
            res[y * self.size_y:self.size_y + y * self.size_y, 0:] = res[0:self.size_y, 0:]

        return res

    def render_material_image(self, dml, material_size=128):
        # reading in all image files from lush.dml
        mat_image = []
        for mat in dml.materials:
            img = cv.resize(cv.imread(f".\\terrain_files\\{mat.name}"), (material_size, material_size),
                            interpolation=cv.INTER_AREA)
            mat_image.append(img)

        img = np.zeros((self.size_y * material_size, self.size_x * material_size, 3), np.uint8)
        for pos_y in range(0, self.size_y):
            for pos_x in range(0, self.size_x):
                mat_index = self.mat_index[pos_y, pos_x]
                flag = self.mat_flags[pos_y, pos_x] & 7
                current_image = np.copy(mat_image[mat_index])

                rot_direction = 3
                # FlipY apparently means to flip an image along the y-axis and not across the Y axis
                # Order of operations is important, flip before rotating
                if flag & 2 == 2:  # vertical
                    current_image = np.flip(current_image, 1)
                if flag & 4 == 4:  # horizontal
                    current_image = np.flip(current_image, 0)
                if flag & 1 == 1:
                    current_image = np.rot90(current_image, k=rot_direction)

                img[(pos_y * material_size):(pos_y * material_size) + material_size,
                (pos_x * material_size):(pos_x * material_size) + material_size] = current_image

        return img

    #In theory Tribes actually has an internal shadow mask for the terrain textures, but in this case I want a better command map
    # def get_shadow_mask_image(self, height_map, shadow_pronounceness = 5, max_shade = 0.5):
    #     grad_kernel_h = np.array([[1, -1]])
    #     grad_kernel_v = np.array([[1], [-1]])
    #     height_grad_map_h = np.abs(cv.filter2D(src=height_map, ddepth=cv.CV_32F, kernel=grad_kernel_h))
    #     height_grad_map_v = np.abs(cv.filter2D(src=height_map, ddepth=cv.CV_32F, kernel=grad_kernel_v))
    #     height_grad_map = height_grad_map_h + height_grad_map_v
    #     max_grad = np.max(height_grad_map)
    #     shadow_map = ((1 - height_grad_map / max_grad) ** shadow_pronounceness) * (1 - max_shade) + max_shade
    #     return shadow_map

    def print_stats(self):
        print("Stats for ted")
        print(f"Name: {self.name_id}")
        print(f"Detail count: {self.detail_count}")
        print(f"Light scale: {self.light_scale}")
        print(f"Height range: {self.height_fmin}, {self.height_fmax}")
        print(f"DFL Height range: {self.height_range_min}, {self.height_range_max}")
        print(f"Size: x={self.size_x}, y={self.size_y}")
        print(f"DFL Size: x={self.dfl_size_x}, y={self.dfl_size_y}")
        print(f"Origin: x={self.origin_x}, y={self.origin_y}")
        print(f"Bounds: BL={self.bounds_bl}, TR={self.bounds_tr}")
        print(f"Scale: {self.scale}")
        print(f"DML: {self.dml_name}")
        print(f"Block Map: {self.block_map}")
        print(f"Block Pattern: {self.dfl_block_pattern}")

        #print("Height Map")
        #for i in range(0, self.size_y):  # Flipping vertically
        #    print(self.heightmap[i * (self.size_x + 1):i * (self.size_x + 1) + (self.size_x + 1)])

