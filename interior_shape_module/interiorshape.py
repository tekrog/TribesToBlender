from TribesToBlender.interior_shape_module import BitStream


class interiorshape:
    def __init__(self):
        self.states = []
        self.lods = []
        self.lod_lightstate_offset = []
        self.lightstate_name_offset = []
        self.name_buffer = ""
        self.name_list = []
        self.material_list_offset = 0
        self.linked_interior = False

    def load_file(self, file_name):
        with open(file_name, "rb") as file:
            data = file.read()
            return self.load_binary(data)

    def load_binary(self, data):
        return self.load_bitstream(BitStream.BitStream(data))

    def load_bitstream(self, stream:BitStream.BitStream):
        if stream.read_byte_string(4) != b'ITRs':
            print("Wrong ITRs header")
            return

        chunk_size = stream.read_uint(32)
        version = stream.read_uint(32) # I don't know, guessing
        num_states = stream.read_uint(32)
        for _ in range(num_states):
            self.states.append(is_state(stream))

        num_lods = stream.read_uint(32)
        for _ in range(num_lods):
            self.lods.append(is_lod(stream))

        num_lod_lights = stream.read_uint(32)
        for _ in range(num_lod_lights):
            self.lod_lightstate_offset.append(stream.read_uint(32))

        num_lightstates = stream.read_uint(32)
        for _ in range(num_lightstates):
            self.lightstate_name_offset.append(stream.read_uint(32))

        name_size = stream.read_uint(32)
        self.name_buffer = stream.read_byte_string(name_size)
        self.name_list = self.name_buffer.split(sep=b'\00')

        self.material_list_offset = stream.read_uint(32)
        linked = stream.read_uint(8)
        if linked != 0:
            self.linked_interior = True
        else:
            self.linked_interior = False

    def get_dig_list(self):
        dig_list = []
        for name in self.name_list:
            if name[-3:].lower() == b'dig':
                dig_list.append(name)

        return dig_list

    def get_dml_list(self):
        dml_list = []
        for name in self.name_list:
            if name[-3:].lower() == b'dml':
                dml_list.append(name)

        return dml_list

class dig:
    def __init__(self):
        self.build_id = 0
        self.texture_scale = 0.0
        self.min_point = (0.0, 0.0, 0.0)
        self.max_point = (0.0, 0.0, 0.0)
        self.surfaces = []
        self.bsp_nodes = []
        self.leaves_solid = []
        self.leaves_empty = []
        self.pvs_bits = []
        self.verts = []
        self.points3f = []
        self.points2f = []
        self.planes = []
        self.highest_mip = 0
        self.flags = 0

    def load_file(self, file_name):
        with open(file_name, "rb") as file:
            data = file.read()
            return self.load_binary(data)

    def load_binary(self, data):
        return self.load_bitstream(BitStream.BitStream(data))

    def load_bitstream(self, stream:BitStream.BitStream):
        if stream.read_byte_string(4) != b'PERS':
            print("Wrong PERS header")
            return

        chunk_size = stream.read_uint(32)
        version = stream.read_uint(16) # I don't know, guessing

        if stream.read_byte_string(11) != b'ITRGeometry':
            print("Wrong Geometry header")
            return

        stream.burn(8) # Null character after header
        chunk_size = stream.read_uint(32)

        self.build_id = stream.read_uint(32)
        self.texture_scale = stream.read_truefloat()
        self.min_point = stream.read_point3f()
        self.max_point = stream.read_point3f()

        num_surface = stream.read_uint(32)
        num_node = stream.read_uint(32)
        num_solid_leaf = stream.read_uint(32)
        num_empty_leaf = stream.read_uint(32)
        num_bit = stream.read_uint(32)
        num_vertex = stream.read_uint(32)
        num_point3 = stream.read_uint(32)
        num_point2 = stream.read_uint(32)
        num_plane = stream.read_uint(32)

        for _ in range(num_surface):
            self.surfaces.append(dig_surface(stream))
        for _ in range(num_node):
            self.bsp_nodes.append(dig_bsp_node(stream))
        for _ in range(num_solid_leaf):
            self.leaves_solid.append(dig_leaf_solid(stream))
        for _ in range(num_empty_leaf):
            self.leaves_empty.append(dig_leaf_empty(stream))
        for _ in range(num_bit):
            self.pvs_bits.append(stream.read_uint(8))
        for _ in range(num_vertex):
            self.verts.append((stream.read_uint(16), stream.read_uint(16))) #Point index, texture index
        for _ in range(num_point3):
            self.points3f.append(stream.read_point3f())
        for _ in range(num_point2):
            self.points2f.append(stream.read_point2f())
        for _ in range(num_plane):
            self.planes.append(dig_plane(stream))

        self.highest_mip = stream.read_uint(32)
        self.flags = stream.read_uint(32)


class is_state:
    def __init__(self, stream:BitStream.BitStream):
        self.name_index = stream.read_uint(32)
        self.lod_index = stream.read_uint(32)
        self.num_LODS = stream.read_uint(32)


class is_lod:
    def __init__(self, stream:BitStream.BitStream):
        self.min_pixels = stream.read_uint(32)
        self.geometry_file_offset = stream.read_uint(32)
        self.light_state_index = stream.read_uint(32)
        self.linkable_faces = stream.read_uint(32)


class dig_surface:
    def __init__(self, stream:BitStream.BitStream):
        self.flags = stream.read_uint(8)
        self.mats = stream.read_uint(8)
        self.tsx = stream.read_uint(8) #texture size
        self.tsy = stream.read_uint(8)
        self.tox = stream.read_uint(8) #texture offset
        self.toy = stream.read_uint(8)
        self.plane_id = stream.read_uint(16)
        self.vert_id = stream.read_uint(32)
        self.point_id = stream.read_uint(32)
        self.num_verts = stream.read_uint(8)
        self.num_points = stream.read_uint(8)
        stream.burn(16) # I honestly don't know...maybe the packing is placing it to align with a dword?


class dig_bsp_node:
    def __init__(self, stream:BitStream.BitStream):
        self.plane_id = stream.read_int16()
        self.front = stream.read_int16()
        self.back = stream.read_int16()
        self.fill = stream.read_int16()


class dig_leaf_solid:
    def __init__(self, stream:BitStream.BitStream):
        self.surf_id = stream.read_uint(32)
        self.plane_id = stream.read_uint(32)
        self.num_surf = stream.read_int16()
        self.num_planes = stream.read_int16()


class dig_leaf_empty:
    def __init__(self, stream:BitStream.BitStream):
        self.flags = stream.read_uint(16)
        self.num_surf = stream.read_int16()
        self.pvs_id = stream.read_uint(32)
        self.surface_id = stream.read_uint(32)
        self.plane_id = stream.read_uint(32)
        self.min_bounds = stream.read_point3f()
        self.max_bounds = stream.read_point3f()
        self.num_planes = stream.read_int16()
        stream.burn(16) # word alignment

class dig_plane:
    def __init__(self, stream:BitStream.BitStream):
        self.x = stream.read_truefloat()
        self.y = stream.read_truefloat()
        self.z = stream.read_truefloat()
        self.d = stream.read_truefloat()

