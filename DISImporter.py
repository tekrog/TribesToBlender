# Original Python DIS to OBJ script created by Jobo.
# Script modified by Krogoth for Blender
######################################################
"""
Export Starsiege Tribes / Darkstar interior geometry to Wavefront OBJ.

A Tribes interior is a small ".dis" manifest (an ITRShape) that names per-detail
geometry files: "<name>-NN.dig" (ITRGeometry) and "<name>-NNN.dil" (lighting).
The real polygons live in the .dig files. This tool parses a .dig directly --
the on-disk layout is exactly what engine/Interior/code/itrgeometry.cpp
ITRGeometry::read() consumes -- and writes an .obj (+ .mtl) you can import in
Blender (File > Import > Wavefront (.obj)).

Texture names come from the sibling "<name>.dml" (TS::MaterialList) if present;
material index N in a surface maps to the Nth .bmp name in that list.

Coordinates are emitted unchanged (Tribes interiors and Blender are both Z-up).
"""

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty

import os
import re
import glob
import struct

filename = ""

def load_dis(fpath, context, flip_v=False, legacy_uv=False):
    global filepath
    filepath = fpath
    global filename
    filename = os.path.splitext(os.path.basename(filepath))[0]
    
    # Collection created, but not used yet
    obj_collection = bpy.data.collections.new(filename)
    context.scene.collection.children.link(obj_collection)
    
    # Find the corresponding .dig files
    d = os.path.dirname(os.path.abspath(filepath))
    prefix = filename + "-"
    pattern = os.path.join(d, f"{prefix}*.dig")
    digs = sorted(glob.glob(pattern))

    # Start converting .dig files
    for dig in digs:
        try:
            convert_one(dig, flip_v=flip_v, legacy_uv=legacy_uv)
        except Exception as e:
            print(f"  ERROR: {e}")
    return
    
def convert_one(dig_path, flip_v=False, legacy_uv=False):
    print(f"Converting {dig_path}")
    geo = parse_dig(dig_path)
    dml = find_dml_for(dig_path)
    materials = load_material_names(dml)
    if materials and dml:
        print(f"  (materials from {os.path.basename(dml)})")
    emit(geo, materials, dig_path=dig_path, flip_v=flip_v, legacy_uv=legacy_uv)
    
def parse_dig(path):
    # Parse one .dig file into geometry (see parse_dig_bytes).
    with open(path, "rb") as f:
        return parse_dig_bytes(f.read(), label=path)

# --- struct sizes, all confirmed byte-exact against ncity-00.dig (205164 bytes) ---
SZ_SURFACE      = 20   # see ITRGeometry::Surface (MSVC default packing)
SZ_BSPNODE      = 8
SZ_BSPLEAFSOLID = 12
SZ_BSPLEAFEMPTY = 44
SZ_VERTEX       = 4    # UInt16 pointIndex, UInt16 textureIndex
SZ_POINT3F      = 12   # 3 x float
SZ_POINT2F      = 8    # 2 x float
SZ_TPLANEF      = 16   # 4 x float

EXPECTED_VERSION = 7
SURFACE_TYPE_LINK = 1  # Surface::Type { Material = 0, Link = 1 }; bit 0 of byte 0

def parse_dig_bytes(data, label="<bytes>"):
    # Parse .dig bytes into a dict with point3List, point2List, vertexList, surfaces.
    r = Reader(data)

    cls, version = parse_pers_header(r)
    if cls != "ITRGeometry":
        raise ValueError(f"{label}: expected ITRGeometry, got {cls!r}")
    if version != EXPECTED_VERSION:
        print(f"  WARNING: {os.path.basename(label)} version {version}, "
              f"expected {EXPECTED_VERSION}; layout may differ.")

    r.i32()    # buildId
    r.f32()    # textureScale
    r.take(24) # box (Box3F)

    n_surface   = r.i32()
    n_node      = r.i32()
    n_solidleaf = r.i32()
    n_emptyleaf = r.i32()
    n_bit       = r.i32()
    n_vertex    = r.i32()
    n_point3    = r.i32()
    n_point2    = r.i32()
    n_plane     = r.i32()

    surface_blob = r.take(n_surface * SZ_SURFACE)
    r.take(n_node      * SZ_BSPNODE)
    r.take(n_solidleaf * SZ_BSPLEAFSOLID)
    r.take(n_emptyleaf * SZ_BSPLEAFEMPTY)
    r.take(n_bit       * 1)
    vertex_blob = r.take(n_vertex * SZ_VERTEX)
    point3_blob = r.take(n_point3 * SZ_POINT3F)
    point2_blob = r.take(n_point2 * SZ_POINT2F)
    r.take(n_plane * SZ_TPLANEF)

    r.i32()  # highestMipLevel
    r.i32()  # flags

    point3 = [struct.unpack_from("<fff", point3_blob, i * SZ_POINT3F)
              for i in range(n_point3)]
    point2 = [struct.unpack_from("<ff", point2_blob, i * SZ_POINT2F)
              for i in range(n_point2)]
    vertices = [struct.unpack_from("<HH", vertex_blob, i * SZ_VERTEX)
                for i in range(n_vertex)]  # (pointIndex, textureIndex)

    # Surface layout (offsets within the 20-byte record):
    #   0 bitfield, 1 material, 2-3 textureSize(x,y), 4-5 textureOffset(x,y),
    #   8-11 vertexIndex, 16 vertexCount.
    # The engine maps a surface's 0..1 point2List coords onto a sub-rectangle of
    # the bitmap: texel = textureOffset + point2*(textureSize+1)  (itrgeometry.cpp
    # getTextureCoord / itrrender.cpp registerTexture). Exporting raw point2List
    # stretches the FULL texture across every panel, squishing narrow ones; we
    # carry the rectangle so write_obj can reproduce the real per-panel mapping.
    surfaces = []
    for i in range(n_surface):
        off = i * SZ_SURFACE
        bits        = surface_blob[off]
        material    = surface_blob[off + 1]
        texSizeX    = surface_blob[off + 2] + 1
        texSizeY    = surface_blob[off + 3] + 1
        texOffX     = surface_blob[off + 4]
        texOffY     = surface_blob[off + 5]
        vertexIndex = struct.unpack_from("<I", surface_blob, off + 8)[0]
        vertexCount = surface_blob[off + 16]
        if (bits & 1) == SURFACE_TYPE_LINK:
            continue  # portal/link, not renderable geometry
        if vertexCount < 3:
            continue
        surfaces.append((material, vertexIndex, vertexCount,
                         texSizeX, texSizeY, texOffX, texOffY))

    return {
        "point3": point3,
        "point2": point2,
        "vertices": vertices,
        "surfaces": surfaces,
        "bytes_used": r.p,
        "total_bytes": len(r.d),
    }

class Reader:
    def __init__(self, data):
        self.d = data
        self.p = 0

    def take(self, n):
        b = self.d[self.p:self.p + n]
        if len(b) != n:
            raise EOFError(f"unexpected end of file at offset {self.p} (wanted {n})")
        self.p += n
        return b

    def u16(self): return struct.unpack_from("<H", self.take(2))[0]
    def i32(self): return struct.unpack_from("<i", self.take(4))[0]
    def f32(self): return struct.unpack_from("<f", self.take(4))[0]
    
def parse_pers_header(r):
    # Consume the PERS block header + class name + version. Returns (classname, version).
    magic = r.take(4)
    if magic != b"PERS":
        raise ValueError(f"not a PERS block (magic={magic!r}) -- not a .dig geometry file?")
    _blocksize = r.i32()                      # bytes following this field
    namesize = r.u16()
    raw = r.take((namesize + 1) & ~1)         # name is padded to an even length
    name = raw[:namesize].decode("ascii", "replace")
    version = r.i32()
    return name, version
    
def find_dml_for(dig_path):
    # ncity-00.dig -> ncity.dml in the same directory, if it exists.
    d = os.path.dirname(os.path.abspath(dig_path))
    stem = os.path.basename(dig_path)
    base = re.sub(r"-\d+\.dig$", "", stem, flags=re.IGNORECASE)
    cand = os.path.join(d, base + ".dml")
    return cand if os.path.isfile(cand) else None
    
# TS::MaterialList (.dml) layout, confirmed byte-exact against ncity.dml:
#   PERS header (8) + namesize(2) + "TS::MaterialList"(16) + version(4)
#   then MaterialList::read: int fnDetails, int fnMaterials,
#   then fnDetails*fnMaterials Material::Params records of 64 bytes each,
#   with the char fMapFile[32] name at offset 16 within each record.
DML_MAT_RECORD = 64
DML_NAME_OFFSET = 16
DML_NAME_LEN = 32


def load_material_names(dml_path):
    # Texture names from a TS::MaterialList .dml file, in material-index order.
    if not dml_path or not os.path.isfile(dml_path):
        return None
    with open(dml_path, "rb") as f:
        return material_names_from_bytes(f.read())
           
def material_names_from_bytes(data):
    # Texture names from TS::MaterialList .dml bytes, in exact material-index order.
    if not data or data[:4] != b"PERS":
        return None
    namesize = struct.unpack_from("<H", data, 8)[0]
    off = 10 + ((namesize + 1) & ~1)   # past class name
    off += 4                            # version
    fnDetails, fnMaterials = struct.unpack_from("<ii", data, off)
    off += 8
    names = []
    for m in range(fnDetails * fnMaterials):
        rec = off + m * DML_MAT_RECORD
        raw = data[rec + DML_NAME_OFFSET: rec + DML_NAME_OFFSET + DML_NAME_LEN]
        name = raw.split(b"\x00", 1)[0].decode("latin1")
        names.append(name)
        create_materials(name)
    return names

def create_materials(bitmap_name):
    # Blender - Create a new material based on the model name and material id
    if bitmap_name.split('.')[0] not in bpy.data.materials:
        mat = bpy.data.materials.new(bitmap_name.split('.')[0])
        mat.use_nodes = True
        mat_nodes = mat.node_tree.nodes
        # check alpha paramater, may need to flip 0 to 1, and 1 to 0
        mat_nodes["Principled BSDF"].inputs[0].default_value = (1, 1, 1, 1)

        if len(bitmap_name):
            bitmap_name = bitmap_name.replace('.bmp', '.png')
            bitmap_name = bitmap_name.replace('.BMP', '.png')

            # Blender - Create the image texture node
            shader_node = mat_nodes.new("ShaderNodeTexImage")
            shader_node.location = -400, 200
            shader_node.select = True
            # Create the path to the image based on the model path
            image_path = os.path.dirname(filepath) + os.path.sep + bitmap_name

            # Check if .png exists
            if os.path.exists(image_path):
                shader_node.image = bpy.data.images.load(image_path)
            # Check if .bmp exists
            else:
                image_path = image_path.rsplit('.', 1)[0] + ".bmp"
                if os.path.exists(image_path):
                    shader_node.image = bpy.data.images.load(image_path)
            
            # Link the image texture node to the color slot on the BSDF node
            links = mat.node_tree.links
            link = links.new(shader_node.outputs["Color"], mat_nodes["Principled BSDF"].inputs["Base Color"])

            # Link the alpha input/output
            links.new(shader_node.outputs["Alpha"], mat_nodes["Principled BSDF"].inputs["Alpha"])
            print(f"  Material created for {bitmap_name}.")
        
    else:
        print(f" Material for {bitmap_name} already exists, skipping.")

def emit(geo, materials, dig_path, flip_v=False, legacy_uv=False):
    # Shared back-end: write OBJ/MTL (+ optional PNG textures) for parsed geometry.
    if geo["bytes_used"] != geo["total_bytes"]:
        print(f"  WARNING: parsed {geo['bytes_used']} of {geo['total_bytes']} bytes "
              f"(layout mismatch?)")
    if materials:
        print(f"  materials: {len(materials)}")
    else:
        print("  materials: none (using numeric names)")

    create_mesh(geo, materials, dig_path=dig_path, flip_v=flip_v, legacy_uv=legacy_uv)

def get_material_texture_size(mat_name):
    mat = bpy.data.materials.get(mat_name)

    if mat is None:
        return 256, 256

    if not mat.use_nodes:
        return 256, 256

    for node in mat.node_tree.nodes:
        if node.type == 'TEX_IMAGE' and node.image:
            return node.image.size[0], node.image.size[1]

    return 256, 256

def get_mat_name_from_index(mat_idx, materials):
    if materials and mat_idx < len(materials):
        return os.path.splitext(materials[mat_idx])[0]
    elif mat_idx == 255:
        return "NoMaterial"
    else:
        return f"material_{mat_idx}"

def create_mesh(geo, materials, dig_path, flip_v=False, legacy_uv=False):
    obj_name = os.path.splitext(os.path.basename(dig_path))[0]

    mesh = bpy.data.meshes.new(obj_name)
    obj = bpy.data.objects.new(obj_name, mesh)

    bpy.data.collections[filename].objects.link(obj)

    obj.data = mesh

    # Set origin-related cursor position
    bpy.context.scene.cursor.location = (0, 0, 0)
    bpy.context.scene.cursor.rotation_quaternion = (1, 0, 0, 0)
    bpy.context.scene.cursor.rotation_euler = (0, 0, 0)

    obj.location = (0, 0, 0)
    obj.rotation_mode = 'QUATERNION'

    # Vertices
    array_verts_all = []

    for x, y, z in geo["point3"]:
        array_verts_all.append((x, y, z))

    # Faces, material indexes, and UVs
    array_faces = []
    array_faces_material = []
    array_uvs = []

    verts = geo["vertices"]
    pt2 = geo["point2"]

    for surf in geo["surfaces"]:
        geo_mat, vertexIndex, vertexCount, texSizeX, texSizeY, texOffsetX, texOffsetY = surf

        mat_name = get_mat_name_from_index(geo_mat, materials)
        tex_w, tex_h = get_material_texture_size(mat_name)

        face = []
        face_uvs = []

        for k in range(vertexCount):
            point_idx, tex_idx = verts[vertexIndex + k]

            face.append(point_idx)

            pu, pv = pt2[tex_idx]

            u = (texOffsetX + pu * texSizeX) / tex_w
            v = (texOffsetY + pv * texSizeY) / tex_h

            if legacy_uv:
                u = 1.0 - u

            if flip_v:
                v = 1.0 - v

            face_uvs.append((u, v))

        array_faces.append(face)
        array_faces_material.append(geo_mat)
        array_uvs.extend(face_uvs)

    # Create Blender mesh
    mesh.from_pydata(array_verts_all, [], array_faces)
    mesh.update()

    # Add materials and create material slot map
    material_slot_map = {}

    used_material_indices = sorted(set(array_faces_material))

    for mat_idx in used_material_indices:
        mat_name = get_mat_name_from_index(mat_idx, materials)

        mat = bpy.data.materials.get(mat_name)

        if mat is None:
            mat = bpy.data.materials.new(mat_name)
            mat.use_nodes = True

        material_slot_map[mat_idx] = len(obj.data.materials)
        obj.data.materials.append(mat)

    # Assign material to each polygon
    for poly_index, poly in enumerate(mesh.polygons):
        original_mat_idx = array_faces_material[poly_index]
        poly.material_index = material_slot_map.get(original_mat_idx, 0)

    # Create UV map
    uv_layer = mesh.uv_layers.new(name='UV Map')
    
    if len(array_uvs) != len(mesh.loops):
        print(f" WARNING: UV count mismatch on {obj_name}. UVs={len(array_uvs)}, loops={len(mesh.loops)}")

    uv_i = 0
    uv_i = 0
    for poly in mesh.polygons:
        for loop_index in poly.loop_indices:
            if uv_i < len(array_uvs):
                uv_layer.data[loop_index].uv = array_uvs[uv_i]
            uv_i += 1

    # Select imported object
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)