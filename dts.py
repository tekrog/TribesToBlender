# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
#import kaitaistruct
from .kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


#if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
#    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Dts(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self.meshes: [Dts.TsAnimmesh] = []
        self.materials: Dts.TsMatList = None
        self._read()

    def _read(self):
        self.shape = Dts.Section(self._io, self, self._root)

        if type(self.shape.data) is Dts.PersData:
            pers_data: Dts.PersData = self.shape.data

            if pers_data.classname == b"TS::Shape\x00":
                shape_data: Dts.TsShape = pers_data.obj_data

                self.meshes = [None] * (shape_data.num_meshes)
                for i in range(shape_data.num_meshes):
                    mesh = Dts.Section(self._io, self, self._root)
                    self.meshes[i] = mesh.data.obj_data

                self.has_materials = self._io.read_s4le()
                if self.has_materials == 1:
                    mats = Dts.Section(self._io, self, self._root)
                    self.materials = mats.data.obj_data


    class Keyframe(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = self._io.read_f4le()
            self.key_value = self._io.read_u2le()
            self.mat_index = self._io.read_u2le()


    class Rgb(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.red = self._io.read_u1()
            self.green = self._io.read_u1()
            self.blue = self._io.read_u1()
            self.flags = self._io.read_u1()


    class Bspsolidleaf(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dummy = self._io.read_u2le()
            self.surface_index = self._io.read_u2le()
            self.dummy2 = self._io.read_u2le()
            self.plane_index = self._io.read_u2le()
            self.surface_count = self._io.read_u2le()
            self.plane_count = self._io.read_u2le()


    class TsMatList(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.num_details = self._io.read_u4le()
            self.num_materials = self._io.read_u4le()
            self.params = [None] * (self.num_materials)
            for i in range(self.num_materials):
                self.params[i] = Dts.MaterialParams(self._io, self, self._root)



    class VertexIndexPair(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.vertex_index = self._io.read_u4le()
            self.texture_index = self._io.read_u4le()


    class Vertex(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.point_index = self._io.read_u2le()
            self.texture_index = self._io.read_u2le()


    class Quat16(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_s2le()
            self.y = self._io.read_s2le()
            self.z = self._io.read_s2le()
            self.w = self._io.read_s2le()


    class Objectv8(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.name = self._io.read_s2le()
            self.flags = self._io.read_u2le()
            self.mesh_index = self._io.read_s4le()
            self.node_index = self._io.read_s2le()
            self.object_offset = Dts.Point3f(self._io, self, self._root)
            self.num_subsequences = self._io.read_u2le()
            self.first_subsequence = self._io.read_u2le()
            self.dummy = self._io.read_u2le()


    class Surface(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.type = self._io.read_bits_int_be(1) != 0
            self.texture_scale_shift = self._io.read_bits_int_be(4)
            self.apply_ambient = self._io.read_bits_int_be(1) != 0
            self.visible_to_outside = self._io.read_bits_int_be(1) != 0
            self.plane_front = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.material = self._io.read_u1()
            self.texture_size = Dts.Point2(self._io, self, self._root)
            self.texture_offset = Dts.Point2(self._io, self, self._root)
            self.plane_index = self._io.read_u2le()
            self.vertex_index = self._io.read_u4le()
            self.point_index = self._io.read_u4le()
            self.vertex_count = self._io.read_u1()
            self.point_count = self._io.read_u1()
            self.dummy = self._io.read_u2le()


    class MaterialParams(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.flags = self._io.read_s4le()
            self.alpha = self._io.read_f4le()
            self.index = self._io.read_s4le()
            self.rgb = Dts.Rgb(self._io, self, self._root)
            if self._parent._parent.version == 1:
                self.map_file_old = (self._io.read_bytes(16))#.decode(u"ASCII")

            if self._parent._parent.version >= 2:
                self.map_file = (self._io.read_bytes(32))#.decode(u"ASCII")

            if self._parent._parent.version >= 3:
                self.type = self._io.read_s4le()

            if self._parent._parent.version >= 3:
                self.elasticity = self._io.read_f4le()

            if self._parent._parent.version >= 3:
                self.friction = self._io.read_f4le()

            if self._parent._parent.version >= 4:
                self.use_default_props = self._io.read_u4le()



    class Objectv7(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.name = self._io.read_u2le()
            self.flags = self._io.read_u2le()
            self.mesh_index = self._io.read_u4le()
            self.node_index = self._io.read_u4le()
            self.object_offset = Dts.Tmat3f(self._io, self, self._root)
            self.num_subsequences = self._io.read_u4le()
            self.first_subsequence = self._io.read_u4le()


    class ShapeData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = Dts.Section(self._io, self, self._root)


    class Keyframev7(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = self._io.read_f4le()
            self.key_value = self._io.read_u4le()
            self.mat_index = self._io.read_u4le()


    class Point2(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_u1()
            self.y = self._io.read_u1()


    class Framev2(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.first_vert = self._io.read_u4le()


    class Subsequencev7(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sequence_index = self._io.read_u4le()
            self.num_keyframes = self._io.read_u4le()
            self.first_keyframe = self._io.read_u4le()


    class VectorSequence(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.name = self._io.read_u4le()
            self.cyclic = self._io.read_u4le()
            self.duration = self._io.read_f4le()
            self.priority = self._io.read_u4le()
            self.first_frame_trigger = self._io.read_u4le()
            self.num_frame_triggers = self._io.read_u4le()
            self.num_ifl_subsequences = self._io.read_u4le()
            self.first_ifl_subsequence = self._io.read_u4le()


    class Tplanef(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.point = Dts.Point3f(self._io, self, self._root)
            self.d = self._io.read_f4le()


    class Dummy(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.no_value = self._io.read_bytes(0)


    class Section(KaitaiStruct):

        class ObjEnums(Enum):
            pers = 1397900624
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.fourcc = KaitaiStream.resolve_enum(Dts.Section.ObjEnums, self._io.read_u4le())
            _on = self.fourcc
            if _on == Dts.Section.ObjEnums.pers:
                self.data = Dts.PersData(self._io, self, self._root)
            else:
                self.data = Dts.Dummy(self._io, self, self._root)


    class ItrGeometry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.build_id = self._io.read_s4le()
            self.texture_scale = self._io.read_f4le()
            self.box = Dts.Box3f(self._io, self, self._root)
            self.surface_list_size = self._io.read_s4le()
            self.node_list_size = self._io.read_s4le()
            self.solid_leaf_list_size = self._io.read_s4le()
            self.empty_leaf_list_size = self._io.read_s4le()
            self.bit_list_size = self._io.read_s4le()
            self.vertex_list_size = self._io.read_s4le()
            self.point3_list_size = self._io.read_s4le()
            self.point2_list_size = self._io.read_s4le()
            self.plane_list_size = self._io.read_s4le()
            self.surface_list = [None] * (self.surface_list_size)
            for i in range(self.surface_list_size):
                self.surface_list[i] = Dts.Surface(self._io, self, self._root)

            self.node_list = [None] * (self.node_list_size)
            for i in range(self.node_list_size):
                self.node_list[i] = Dts.Bspnode(self._io, self, self._root)

            self.solid_leaf_list = [None] * (self.solid_leaf_list_size)
            for i in range(self.solid_leaf_list_size):
                self.solid_leaf_list[i] = Dts.Bspsolidleaf(self._io, self, self._root)

            self.empty_leaf_list = [None] * (self.empty_leaf_list_size)
            for i in range(self.empty_leaf_list_size):
                self.empty_leaf_list[i] = Dts.Bspemptyleaf(self._io, self, self._root)

            self.bitlist = [None] * (self.bit_list_size)
            for i in range(self.bit_list_size):
                self.bitlist[i] = self._io.read_u1()

            self.vertex_list = [None] * (self.vertex_list_size)
            for i in range(self.vertex_list_size):
                self.vertex_list[i] = Dts.Vertex(self._io, self, self._root)

            self.point3_list = [None] * (self.point3_list_size)
            for i in range(self.point3_list_size):
                self.point3_list[i] = Dts.Point3f(self._io, self, self._root)

            self.point2_list = [None] * (self.point2_list_size)
            for i in range(self.point2_list_size):
                self.point2_list[i] = Dts.Point2f(self._io, self, self._root)

            self.plane_list = [None] * (self.plane_list_size)
            for i in range(self.plane_list_size):
                self.plane_list[i] = Dts.Tplanef(self._io, self, self._root)

            self.highest_mip_level = self._io.read_s4le()
            self.flags = self._io.read_u4le()


    class Point3f(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()


    class Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.first_vert = self._io.read_s4le()
            self.scale = Dts.Point3f(self._io, self, self._root)
            self.origin = Dts.Point3f(self._io, self, self._root)


    class Point2f(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()


    class Bspemptyleaf(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.flags = self._io.read_bits_int_be(1) != 0
            self.pvs_count = self._io.read_bits_int_be(15)
            self._io.align_to_byte()
            self.surface_count = self._io.read_u2le()
            self.pvs_index = self._io.read_u4le()
            self.surface_index = self._io.read_u4le()
            self.plane_index = self._io.read_u4le()
            self.box = Dts.Box3f(self._io, self, self._root)
            self.plane_count = self._io.read_u2le()
            self.dummy = self._io.read_u2le()


    class TsShape(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.num_nodes = self._io.read_u4le()
            self.num_seq = self._io.read_u4le()
            self.num_subseq = self._io.read_u4le()
            self.num_keyframes = self._io.read_u4le()
            self.num_transforms = self._io.read_u4le()
            self.num_names = self._io.read_u4le()
            self.num_objects = self._io.read_u4le()
            self.num_details = self._io.read_u4le()
            self.num_meshes = self._io.read_u4le()
            self.num_transitions = self._io.read_u4le()
            self.num_frametriggers = self._io.read_u4le()
            self.radius = self._io.read_f4le()
            self.center = Dts.Point3f(self._io, self, self._root)
            if self._parent.version >= 8:
                self.bounds = Dts.Box3f(self._io, self, self._root)

            if self._parent.version == 7:
                self.nodes_v7 = [None] * (self.num_nodes)
                for i in range(self.num_nodes):
                    self.nodes_v7[i] = Dts.Nodev7(self._io, self, self._root)


            if self._parent.version == 8:
                self.nodes = [None] * (self.num_nodes)
                for i in range(self.num_nodes):
                    self.nodes[i] = Dts.Node(self._io, self, self._root)


            self.sequences = [None] * (self.num_seq)
            for i in range(self.num_seq):
                self.sequences[i] = Dts.VectorSequence(self._io, self, self._root)

            if self._parent.version == 8:
                self.subsequences = [None] * (self.num_subseq)
                for i in range(self.num_subseq):
                    self.subsequences[i] = Dts.Subsequence(self._io, self, self._root)


            if self._parent.version <= 7:
                self.subsequences_v7 = [None] * (self.num_subseq)
                for i in range(self.num_subseq):
                    self.subsequences_v7[i] = Dts.Subsequencev7(self._io, self, self._root)


            if self._parent.version == 8:
                self.keyframes = [None] * (self.num_keyframes)
                for i in range(self.num_keyframes):
                    self.keyframes[i] = Dts.Keyframe(self._io, self, self._root)


            if self._parent.version <= 7:
                self.keyframes_v7 = [None] * (self.num_keyframes)
                for i in range(self.num_keyframes):
                    self.keyframes_v7[i] = Dts.Keyframev7(self._io, self, self._root)


            if self._parent.version == 8:
                self.transforms = [None] * (self.num_transforms)
                for i in range(self.num_transforms):
                    self.transforms[i] = Dts.Transform(self._io, self, self._root)


            if self._parent.version == 7:
                self.transforms_v7 = [None] * (self.num_transforms)
                for i in range(self.num_transforms):
                    self.transforms_v7[i] = Dts.Transformv7(self._io, self, self._root)


            self.names = [None] * (self.num_names)
            for i in range(self.num_names):
                self.names[i] = (self._io.read_bytes(24))#.decode(u"ASCII")

            if self._parent.version == 8:
                self.objects = [None] * (self.num_objects)
                for i in range(self.num_objects):
                    self.objects[i] = Dts.Objectv8(self._io, self, self._root)


            if self._parent.version <= 7:
                self.objects_v7 = [None] * (self.num_objects)
                for i in range(self.num_objects):
                    self.objects_v7[i] = Dts.Objectv7(self._io, self, self._root)


            self.details = [None] * (self.num_details)
            for i in range(self.num_details):
                self.details[i] = Dts.Detail(self._io, self, self._root)

            if self._parent.version == 8:
                self.transitions = [None] * (self.num_transitions)
                for i in range(self.num_transitions):
                    self.transitions[i] = Dts.Transition(self._io, self, self._root)


            if self._parent.version == 7:
                self.transitions_v7 = [None] * (self.num_transitions)
                for i in range(self.num_transitions):
                    self.transitions_v7[i] = Dts.Transitionv7(self._io, self, self._root)


            self.frame_triggers = [None] * (self.num_frametriggers)
            for i in range(self.num_frametriggers):
                self.frame_triggers[i] = Dts.FrameTrigger(self._io, self, self._root)

            if self._parent.version >= 5:
                self.default_material = self._io.read_u4le()

            if self._parent.version >= 6:
                self.always_animate = self._io.read_s4le()



    class Face(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.vip = [None] * (3)
            for i in range(3):
                self.vip[i] = Dts.VertexIndexPair(self._io, self, self._root)

            self.material = self._io.read_u4le()


    class PersData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.size = self._io.read_u4le()
            self.classname_len = self._io.read_u2le()
            self.classname = (self._io.read_bytes(((self.classname_len + 1) & ~1)))#.decode(u"ASCII")
            self.version = self._io.read_u4le()
            _on = self.classname
            if _on == b"TS::Shape\x00":
                self.obj_data = Dts.TsShape(self._io, self, self._root)
            elif _on == b"TS::CelAnimMesh\x00":
                self.obj_data = Dts.TsAnimmesh(self._io, self, self._root)
            elif _on == b"TS::MaterialList":
                self.obj_data = Dts.TsMatList(self._io, self, self._root)
            elif _on == b"ITRGeometry\x00":
                self.obj_data = Dts.ItrGeometry(self._io, self, self._root)


    class PackedVertex(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_u1()
            self.y = self._io.read_u1()
            self.z = self._io.read_u1()
            self.normal = self._io.read_u1()


    class Transitionv7(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.start_sequence = self._io.read_u4le()
            self.end_sequence = self._io.read_u4le()
            self.start_position = self._io.read_f4le()
            self.end_position = self._io.read_f4le()
            self.transform = Dts.Transformv7(self._io, self, self._root)


    class FrameTrigger(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position = self._io.read_f4le()
            self.value = self._io.read_u4le()


    class Node(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.name = self._io.read_u2le()
            self.parent = self._io.read_s2le()
            self.num_subsequences = self._io.read_u2le()
            self.first_subsequence = self._io.read_u2le()
            self.default_transform = self._io.read_u2le()


    class Bspnode(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.plane_index = self._io.read_u2le()
            self.front = self._io.read_s2le()
            self.back = self._io.read_s2le()
            self.fill = self._io.read_s2le()


    class Subsequence(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sequence_index = self._io.read_u2le()
            self.num_keyframes = self._io.read_u2le()
            self.first_keyframe = self._io.read_u2le()


    class Detail(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.root_node_index = self._io.read_u4le()
            self.size = self._io.read_f4le()


    class Transition(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.start_sequence = self._io.read_u4le()
            self.end_sequence = self._io.read_u4le()
            self.start_position = self._io.read_f4le()
            self.end_position = self._io.read_f4le()
            self.duration = self._io.read_f4le()
            self.transform = Dts.Transform(self._io, self, self._root)


    class Tmat3f(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.flags = self._io.read_u4le()
            self.m = [None] * (9)
            for i in range(9):
                self.m[i] = self._io.read_f4le()

            self.p = Dts.Point3f(self._io, self, self._root)


    class Transformv7(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rotate = Dts.Quat16(self._io, self, self._root)
            self.translate = Dts.Point3f(self._io, self, self._root)
            self.scale = Dts.Point3f(self._io, self, self._root)


    class Nodev7(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.name = self._io.read_u4le()
            self.parent = self._io.read_u4le()
            self.num_subsequences = self._io.read_u4le()
            self.first_subsequence = self._io.read_u4le()
            self.default_transform = self._io.read_u4le()


    class TsAnimmesh(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.num_vertices = self._io.read_u4le()
            self.num_vertices_per_frame = self._io.read_u4le()
            self.num_texture_vertices = self._io.read_u4le()
            self.num_faces = self._io.read_u4le()
            self.num_frames = self._io.read_u4le()
            if self._parent.version >= 2:
                self.num_texture_vertices_per_frame = self._io.read_u4le()

            if self._parent.version < 3:
                self.scale_v2 = Dts.Point3f(self._io, self, self._root)

            if self._parent.version < 3:
                self.origin_v2 = Dts.Point3f(self._io, self, self._root)

            self.radius = self._io.read_f4le()
            self.vertices = [None] * (self.num_vertices)
            for i in range(self.num_vertices):
                self.vertices[i] = Dts.PackedVertex(self._io, self, self._root)

            self.texture_vertices = [None] * (self.num_texture_vertices)
            for i in range(self.num_texture_vertices):
                self.texture_vertices[i] = Dts.Point2f(self._io, self, self._root)

            self.faces = [None] * (self.num_faces)
            for i in range(self.num_faces):
                self.faces[i] = Dts.Face(self._io, self, self._root)

            if self._parent.version < 3:
                self.frames_v2 = [None] * (self.num_frames)
                for i in range(self.num_frames):
                    self.frames_v2[i] = Dts.Framev2(self._io, self, self._root)


            if self._parent.version >= 3:
                self.frames = [None] * (self.num_frames)
                for i in range(self.num_frames):
                    self.frames[i] = Dts.Frame(self._io, self, self._root)




    class Transform(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rotate = Dts.Quat16(self._io, self, self._root)
            self.translate = Dts.Point3f(self._io, self, self._root)


    class Box3f(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.min = Dts.Point3f(self._io, self, self._root)
            self.max = Dts.Point3f(self._io, self, self._root)
