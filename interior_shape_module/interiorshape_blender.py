from interior_shape_module import interiorshape
from interior_shape_module import dml as tdml
import bpy
import bmesh

def load_dis(filename, shape_directory, texture_directory):
    dis = interiorshape.interiorshape()
    dis.load_file(f"{shape_directory}/{filename}")

    # I think there can only be one dml per shapefile?  Maybe will have to come back if there are exceptions
    dml_name = dis.get_dml_list()[0].decode('UTF-8')
    dml: tdml = tdml.dml()
    dml.load_file(f"{shape_directory}/{dml_name}")
    materials = []
    for material in dml.materials:
        material: tdml.dml_material
        png = f"{material.name[0:-4]}.png"
        materials.append(load_mat(f"{texture_directory}/{png}", png[0:-4]))

    if len(materials) == 0:
        print(f"{filename} doesn't  have any usable materials")
        return

    for dig_name in dis.get_dig_list():
        dig_str = dig_name.decode('UTF-8')
        bobj = load_dig(f"{shape_directory}/{dig_str}", dig_str[:-4], materials)
    return


def load_dig(file, obj_name, mats):
    dig = interiorshape.dig()
    dig.load_file(file)

    short_name = obj_name

    vertices = []
    edges = []
    faces = []
    uv_layer_data = []
    for surface in dig.surfaces:
        if surface.mats == 255:
            surface.mats = 0
        if not surface.mats in mats:
            surface.mats = 0
        mat = mats[surface.mats]
        width = mat[1]
        height = mat[2]
        scale = (-(surface.tsx + 1) / width, -(surface.tsy + 1) / height)
        offset = (-(surface.tox + 1) / width, -(surface.toy + 1) / height)
        for vert_id in range(surface.vert_id, surface.vert_id + surface.num_verts):
            vertices.append(dig.points3f[dig.verts[vert_id][0]])
            uv_layer_data.append(
                scale_offset_uv(dig.points2f[dig.verts[vert_id][1]],
                                scale,
                                offset))
        faces.append(range(surface.vert_id, surface.vert_id + surface.num_verts))

    mesh = bpy.data.meshes.new(short_name)  # add the new mesh
    obj = bpy.data.objects.new(mesh.name, mesh)
    col = bpy.data.collections["Collection"]
    col.objects.link(obj)
    bpy.context.view_layer.objects.active = obj

    mesh.from_pydata(vertices, edges, faces)

    # Create UV layer for the object
    uv_layer = mesh.uv_layers.new(name="UVMap")

    # Assign UV coordinates to the UV layer
    for face_index, uv_coords in enumerate(uv_layer_data):
        uv_layer.data[face_index].uv = uv_coords

    for mat in mats:
        obj.data.materials.append(mat[0])

    polyid = 0
    for surface in dig.surfaces:
        obj.data.polygons[polyid].material_index = surface.mats
        polyid += 1

    return obj


def load_mat(file, mat_name):
    # Load the PNG image into Blender
    img = bpy.data.images.load(file)

    # Create a material for the mesh
    material = bpy.data.materials.new(name=mat_name)

    # Create a shader node tree for the material
    if material.use_nodes:
        material.node_tree.links.clear()  # Clear any existing node links
    else:
        material.use_nodes = True

    # Create a texture and add it to the material
    texture = material.node_tree.nodes.new(type='ShaderNodeTexImage')
    texture.image = img
    material.node_tree.links.new(texture.outputs['Color'],
                                 material.node_tree.nodes['Principled BSDF'].inputs['Base Color'])

    return (material, img.size[0], img.size[1])


def scale_offset_uv(point, scale, offset):
    return (offset[0] + (point[0] * scale[0]),
            offset[1] + (point[1] * scale[1]))

