from TribesToBlender.interior_shape_module import helper
import json

class dml:
    def __init__(self):
        self.materials = []
        self.num_mats = None
        self.num_details = None
        self.version = None

    def load_binary(self, data):
        if data[:4] != b"PERS":
            print("Wrong GBLK header")
            return
        curr_data_index = [4]

        block_size = helper.get_int(data, curr_data_index)
        version_guess = helper.get_int16(data, curr_data_index)
        if data[curr_data_index[0]:curr_data_index[0] + 16] != b'TS::MaterialList':
            print("Not a TS::MaterialList")
            return
        curr_data_index[0] += 16

        self.version = helper.get_int(data, curr_data_index)
        self.num_details = helper.get_int(data, curr_data_index)
        self.num_mats = helper.get_int(data, curr_data_index)

        self.materials = []
        for _ in range(0, self.num_mats * self.num_details):
            mat = dml_material()
            mat.read(data, curr_data_index, self.version)
            self.materials.append(mat)

        return True

    def get_material(self, ind):
        # Chances are this will match...so make it an O(1) operation...if not will need to search
        if len(self.materials) <= ind and self.materials[ind].index == ind:
            return self.materials[ind]

        for mat in self.materials:
            if mat.index == ind:
                return mat

    def load_file(self, file):
        if file[-3:] != 'dml':
            print("Haven't implemented anything other than dml")
            return False

        with open(file, "rb") as file:
            data = file.read()
            return self.load_binary(data)

    def eliminate_transitions(self):
        for mat in self.materials:
            r = s = f = n = g = c = h = 0
            for char in mat.name[1:5]:
                if char == 'r':
                    r += 1
                elif char == 's':
                    s += 1
                elif char == 'f':
                    f += 1
                elif char == 'n':
                    n += 1
                elif char == 'g':
                    g += 1
                elif char == 'c':
                    c += 1
                elif char == 'h':
                    h += 1

            if r >= 4 or s >= 4 or f >= 4 or n >= 4 or g >= 4 or c >= 4:
                continue

            if r >= 2:
                mat.name = 'lrrrr.bmp'
            if s >= 2:
                mat.name = 'lssss.bmp'
            if f >= 2:
                mat.name = 'lffff.bmp'
            if n >= 2:
                mat.name = 'lnnnn.bmp'
            if g >= 2:
                mat.name = 'lgggg.bmp'
            if c >= 2:
                mat.name = 'lcccc.bmp'

            if r >= 1:
                mat.name = 'lrrrr.bmp'
            if s >= 1:
                mat.name = 'lssss.bmp'
            if f >= 1:
                mat.name = 'lffff.bmp'
            if n >= 1:
                mat.name = 'lnnnn.bmp'
            if g >= 1:
                mat.name = 'lgggg.bmp'
            if c >= 1:
                mat.name = 'lcccc.bmp'

        return

    def export_dictionary(self, file):
        mat_dict = {}
        for mat in self.materials:
            mat_dict[mat.index] = mat.name

        json_object = json.dumps(mat_dict, indent=4)

        # Writing to sample.json
        with open(file, "w") as outfile:
            outfile.write(json_object)


class dml_material:

    def __init__(self):
        self.flags = None
        self.alpha = None
        self.index = None
        self.rgbf = None  # f is for flags
        self.name = None
        self.type = None
        self.elasticity = None
        self.friction = None
        self.default_props = None

    def read(self, data, curr_data_index, version):
        if version <= 1:
            print("Haven't implemented lower version")
            return

        self.flags = helper.get_int(data, curr_data_index)
        self.alpha = helper.get_float(data, curr_data_index)
        self.index = helper.get_int(data, curr_data_index)
        self.rgbf = helper.get_int(data, curr_data_index)
        self.name = data[curr_data_index[0]:curr_data_index[0] + 32].decode('utf8').split("\x00")[0]
        curr_data_index[0] += 32
        self.type = helper.get_int(data, curr_data_index)
        if version > 2:
            self.elasticity = helper.get_float(data, curr_data_index)
            self.friction = helper.get_float(data, curr_data_index)
        if version > 3:
            self.default_props = helper.get_int(data, curr_data_index)

    def print_stats(self):
        print(f"Name: {self.name}")
