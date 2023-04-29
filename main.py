from .dts import Dts
import sys
import os
import os.path
import pprint
import re
import math
import bpy
import bmesh
import mathutils
from bpy import ops
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, FloatProperty


'''
Keyframe matIndex flags:
if( visible )
    fMatIndex |= 0x8000;
if( visMatters )        // Uses visibility track
    fMatIndex |= 0x4000;
if( matMatters )        // Uses material track
    fMatIndex |= 0x2000;
if( frameMatters )      // Uses frame track
    fMatIndex |= 0x1000;

Material frame index: fMatIndex & 0x0fff
pa->useTextures( &fTextureVerts[matFrameIndex*fnTextureVertsPerFrame] );


v7 Keyframe matIndex is u4 instead of u2
fMatIndex & 0x80000000
fMatIndex & 0x40000000
fMatIndex & 0x20000000
fMatIndex & 0x10000000
mat index = fMatIndex & 0x0fffffff
'''
FLAG_FRAME_TRACK = 0x1000
FLAG_MATERIAL_TRACK = 0x2000
FLAG_VISIBILITY_TRACK = 0x4000
FLAG_IS_VISIBLE = 0x8000

FLAG_MATTYPE_NULL = 0x0
FLAG_MATTYPE_FLAGS = 0xF
FLAG_MATTYPE_PALETTE = 0x1
FLAG_MATTYPE_RGB = 0x2
FLAG_MATTYPE_TEXTURE = 0x3

FLAG_SHADING_FLAGS = 0xF00
FLAG_SHADING_NONE = 0x100
FLAG_SHADING_FLAT = 0x200
FLAG_SHADING_SMOOTH = 0x400

FLAG_TEXTURE_FLAGS = 0xF000
FLAG_TEXTURE_TRANSPARENT = 0x1000
FLAG_TEXTURE_TRANSLUCENT = 0x2000

frame_id = 0


class ImportDTS(bpy.types.Operator, ImportHelper):
    bl_idname = "dynamix.dts"
    bl_label = "Import Starsiege: Tribes .dts"
    bl_description = 'Imports Starsiege: Tribes .dts file.'

    filter_glob : StringProperty(default="*.dts", options={'HIDDEN'})
    filename_ext = ".dts"    
    
    def execute(self, context):
        global frame_id
        import re

        filename = self.filepath.split(os.path.sep)[-1].split('.')[0]
        path = self.filepath
        
        # Collection created, but not used yet
        obj_collection = bpy.data.collections.new(filename)
        context.scene.collection.children.link(obj_collection)

        with open(path, 'r') as f:
            def store(str=''):
                pass
#                print(str)
#                with open(out_path, 'a') as f:
#                    f.write(str + "\n")
                
            def short2float(short):
                if short == 0:
                    return 0
                return float(short) / float(0x7FFF)

            # Blender uses linear rgb
            def srgb_to_linear_rgb(srgb: int) -> float:
                srgb = srgb / 255
                if srgb <= 0.04045:
                    linear = srgb / 12.92
                else:
                    linear = math.pow((srgb + 0.055) / 1.055, 2.4)

                return linear
            
            def create_nodes(node: Dts.Node, nodes, transforms, node_tree):
                store('var node_{} = new THREE.Group();'.format(node.id))

                def_trans = transforms[nodes[node.id].default_transform]
                if nodes[node.id].parent == -1:
                    store('node_{}.position.set({}, {}, {});'.format(node.id, def_trans.translate.x, def_trans.translate.y, def_trans.translate.z))
                    store('node_{}.applyQuaternion(new THREE.Quaternion({}, {}, {}, {}));'.format(
                        node.id, short2float(def_trans.rotate.x), short2float(def_trans.rotate.y), short2float(def_trans.rotate.z), short2float(def_trans.rotate.w)
                    ))
                    store('group.add(node_{});'.format(node.id))
                else:
                    #store('console.log(node_{}.quaternion);'.format(nodes[node.id].parent))
                    store('node_{}.translateX({});'.format(node.id, def_trans.translate.x))
                    store('node_{}.translateY({});'.format(node.id, def_trans.translate.y))
                    store('node_{}.translateZ({});'.format(node.id, def_trans.translate.z))
                    store('node_{}.applyQuaternion(node_{}.quaternion);'.format(node.id, nodes[node.id].parent))
                    store('node_{}.applyQuaternion(new THREE.Quaternion({}, {}, {}, {}).invert());'.format(
                        node.id, short2float(def_trans.rotate.x), short2float(def_trans.rotate.y), short2float(def_trans.rotate.z), short2float(def_trans.rotate.w)
                    ))
                    store('node_{}.add(node_{});'.format(nodes[node.id].parent, node.id))

                for child in node_tree[node.id]:
                    create_nodes(nodes[child], nodes, transforms, node_tree)


            def animate_meshes(mesh, obj, names, keyframes, sequences, subsequences, scene):
                global frame_id

                if hasattr(mesh, 'frames'):
                    frames = mesh.frames
                elif hasattr(mesh, 'frames_v2'):
                    frames = mesh.frames_v2

                # Objects only have sequences if they have more than one frame on the mesh
                if len(frames) == 1:
                    print('{} has no frames'.format(names[obj.name]))
                    return

                # Assume meshes can only have one subsequence
                subseq = subsequences[obj.first_subsequence]
                seq = subseq.sequence_index
                seq_name = names[sequences[seq].name]
                print('Seq:', seq_name, 'Subseq id:', obj.first_subsequence)
                scene.timeline_markers.new(seq_name, frame=frame_id)

                first_keyframe = subseq.first_keyframe
                isFrameTrackKeyframe = keyframes[first_keyframe].mat_index & FLAG_FRAME_TRACK
                isMaterialTrackKeyframe = keyframes[first_keyframe].mat_index & FLAG_MATERIAL_TRACK
                isVisibilityTrack = keyframes[first_keyframe].mat_index & FLAG_VISIBILITY_TRACK

                object = bpy.context.scene.objects[names[obj.name]]
                if isFrameTrackKeyframe:
                    print('Frame track!!!')
                    # Frame 0 is the Basis, keyframes start with frame 1
                    first_vert = frames[0].first_vert
                    sk_basis = object.shape_key_add(name='Basis', from_mix=False)
                    sk_basis.interpolation = 'KEY_LINEAR'
                    object.data.shape_keys.use_relative = True

                    sks = []
                    for key in range(first_keyframe, first_keyframe + subseq.num_keyframes):
                        frametrack_key = keyframes[key].key_value

                        # Create new shape key
                        sk = object.shape_key_add(name='Frame {}'.format(frametrack_key), from_mix=False)
                        sk.interpolation = 'KEY_LINEAR'

                        start_vertex = frames[frametrack_key].first_vert
                        for vrt_idx in range(mesh.num_vertices_per_frame):
                            print('{}, {}, {} -> {}, {}, {}'.format(
                                sk.data[vrt_idx].co.x,
                                sk.data[vrt_idx].co.y,
                                sk.data[vrt_idx].co.z,
                                mesh.vertices[start_vertex + vrt_idx].x,
                                mesh.vertices[start_vertex + vrt_idx].y,
                                mesh.vertices[start_vertex + vrt_idx].z
                            ))
                            sk.data[vrt_idx].co.x = mesh.vertices[start_vertex + vrt_idx].x
                            sk.data[vrt_idx].co.y = mesh.vertices[start_vertex + vrt_idx].y
                            sk.data[vrt_idx].co.z = mesh.vertices[start_vertex + vrt_idx].z
                        print('=============')
                        sk.value = 0
                        sk.keyframe_insert(data_path="value", index=-1)
                        sks.append(sk)
                    
                    prev_sk = None
                    for sk_idx in range(len(sks)):
                        scene.frame_set(frame_id)

                        # Set prev frame back to zero
                        if prev_sk is not None:
                            prev_sk.value = 0
                            prev_sk.keyframe_insert(data_path="value", index=-1)

                        # Set current frame to 1
                        sks[sk_idx].value = 1
                        sks[sk_idx].keyframe_insert(data_path="value", index=-1)

                        # Queue up next frame, setting it to zero, so there's no automatic transition to 1
                        if sk_idx != len(sks) - 1:
                            sks[sk_idx + 1].value = 0
                            sks[sk_idx + 1].keyframe_insert(data_path="value", index=-1)

                        prev_sk = sks[sk_idx]
                        frame_id += 1

                if isMaterialTrackKeyframe:
                    print('Material track!!!')
                if isVisibilityTrack:
                    print('Visibility track!!!')
                if not isFrameTrackKeyframe and not isMaterialTrackKeyframe and not isVisibilityTrack:
                    print('Transform track!!!')

            def generate_ifl_materials(sequences, keyframes):
                ifl_materials = {}
                for seq_id in range(len(sequences)):
                    sequence: Dts.VectorSequence = sequences[seq_id]
                    seq_name = names[sequence.name]

                    # IFL subsequences
                    if sequence.num_ifl_subsequences > 0:
                        # A sequence may have multiple IFL subsequences, for different materials
                        ifl_frame_id = 0
                        for subseq_count in range(sequence.num_ifl_subsequences):
                            subseq = subsequences[sequence.first_ifl_subsequence + subseq_count]
                            first_keyframe = subseq.first_keyframe

                            ifl_mat = bpy.data.materials.new(name='ifl_{}_{}'.format(seq_name, subseq_count))
                            ifl_mat.use_nodes = True
                            shader_nodes = ifl_mat.node_tree.nodes
                            shader_links = ifl_mat.node_tree.links

                            if keyframes[first_keyframe].mat_index not in ifl_materials:
                                ifl_materials[keyframes[first_keyframe].mat_index] = 'ifl_{}_{}'.format(seq_name, subseq_count)

                            # Texture nodes
                            texture_nodes = []
                            ifl_sequence = []
                            node_num = 0
                            for key in range(first_keyframe, first_keyframe + subseq.num_keyframes):
                                # The material index represents the default material, while the key_value represents the new material to replace it with
                                old_map = d.materials.params[keyframes[key].mat_index].map_file
                                old_map = old_map[:old_map.find(b'\0')].decode('ascii')
                                new_map = d.materials.params[keyframes[key].key_value].map_file
                                new_map = new_map[:new_map.find(b'\0')].decode('ascii')
                                print("Key:", key, "Material Idx:", keyframes[key].mat_index, "Map name:", old_map, "->", new_map)

                                image_path = os.path.dirname(self.filepath) + os.path.sep + new_map
                                image_path = image_path.rsplit('.', 1)[0] + ".png"
                                ifl_sequence.append(image_path)

                                # See if we've already made a texture node and re-use it
                                for tex in texture_nodes:
                                    if tex.image.filepath == image_path:
                                        texture_nodes.append(tex)
                                        break
                                else:
                                    # Make a new texture shader
                                    image = None
                                    if os.path.exists(image_path):
                                        image = bpy.data.images.load(image_path, check_existing=False)
                                    else:
                                        print("Missing image: {}".format(image_path))

                                    shader_node = shader_nodes.new("ShaderNodeTexImage")

                                    if image:
                                        image.name = new_map  # "sequence_{}_{}".format(seq_name, ifl_frame_id)
                                        image.use_fake_user = True
                                        shader_node.image = image
                                        shader_node.image.source = "FILE"

                                    shader_node.location = node_num * 250, 100
                                    texture_nodes.append(shader_node)
                                    node_num += 1

                            # Create mix and math nodes
                            prev_mix_node_color = None
                            prev_mix_node_alpha = None
                            greater_nodes = []
                            for mix_idx in range(len(texture_nodes) - 1):
                                mix_node_color = shader_nodes.new("ShaderNodeMixRGB")
                                mix_node_color.location = 300 + mix_idx * 250, 550

                                mix_node_alpha = shader_nodes.new("ShaderNodeMixRGB")
                                mix_node_alpha.location = 300 + mix_idx * 250, 350

                                # Math node to toggle between the two textures
                                math_node = shader_nodes.new("ShaderNodeMath")
                                math_node.operation = "GREATER_THAN"
                                math_node.inputs[1].default_value = mix_idx + 1  # Threshold
                                math_node.location = 50 + mix_idx * 250, 750
                                shader_links.new(math_node.outputs["Value"], mix_node_color.inputs["Fac"])
                                shader_links.new(math_node.outputs["Value"], mix_node_alpha.inputs["Fac"])
                                greater_nodes.append(math_node)

                                # For the first mix node, use the first two textures
                                if prev_mix_node_color is None:
                                    shader_links.new(texture_nodes[mix_idx].outputs["Color"], mix_node_color.inputs["Color1"])
                                    shader_links.new(texture_nodes[mix_idx + 1].outputs["Color"], mix_node_color.inputs["Color2"])

                                    shader_links.new(texture_nodes[mix_idx].outputs["Alpha"], mix_node_alpha.inputs["Color1"])
                                    shader_links.new(texture_nodes[mix_idx + 1].outputs["Alpha"], mix_node_alpha.inputs["Color2"])
                                else:
                                    # Otherwise, use the previous mix node and the next texture
                                    shader_links.new(prev_mix_node_color.outputs["Color"], mix_node_color.inputs["Color1"])
                                    shader_links.new(texture_nodes[mix_idx + 1].outputs["Color"], mix_node_color.inputs["Color2"])

                                    shader_links.new(prev_mix_node_alpha.outputs["Color"], mix_node_alpha.inputs["Color1"])
                                    shader_links.new(texture_nodes[mix_idx + 1].outputs["Alpha"], mix_node_alpha.inputs["Color2"])

                                prev_mix_node_color = mix_node_color
                                prev_mix_node_alpha = mix_node_alpha

                            # Create an Add node that inputs into all of the "greater than" nodes
                            add_node = shader_nodes.new("ShaderNodeMath")
                            add_node.operation = "ADD"
                            add_node.inputs[1].default_value = 0.01
                            add_node.location = -150, 850
                            for g_node in greater_nodes:
                                shader_links.new(add_node.outputs["Value"], g_node.inputs["Value"])

                            # Create an input value node for keyframing and attach it to the "Add" node
                            input_node = shader_nodes.new("ShaderNodeValue")
                            input_node.name = "IFL Input Value"
                            input_node.location = -350, 850
                            shader_links.new(input_node.outputs["Value"], add_node.inputs[0])

                            # Link the final mix output to the BSDF
                            bsdf_node = shader_nodes.get("Principled BSDF")
                            bsdf_node.location = (len(texture_nodes) + 1) * 250, 100
                            shader_links.new(prev_mix_node_color.outputs["Color"], bsdf_node.inputs["Base Color"])

                            # Update the material's blend mode if there are alpha channels
                            mat_flags = d.materials.params[keyframes[first_keyframe].key_value].flags
                            if mat_flags & FLAG_TEXTURE_TRANSPARENT == FLAG_TEXTURE_TRANSPARENT or mat_flags & FLAG_TEXTURE_TRANSLUCENT == FLAG_TEXTURE_TRANSLUCENT:
                                ifl_mat.blend_method = "BLEND"
                                shader_links.new(prev_mix_node_alpha.outputs["Color"], bsdf_node.inputs["Alpha"])

                            mat_out_node = shader_nodes.get("Material Output")
                            mat_out_node.location = bsdf_node.location[0] + 300, bsdf_node.location[1]

                return ifl_materials


            
            d = Dts.from_file(path)

            MAX_VAL = float(0x7FFF)
            names = []
            nodes = []
            objects = []
            textures = []
            mapFiles = []
            transforms = []
            pngORbmp = ""
            node_tree = {}
            obj_dts_to_blender_map = {}


            if b'TS::Shape' in d.shape.data.classname:
                shape_data: Dts.TsShape = d.shape.data.obj_data

                for name in shape_data.names:
                    names.append(name[:name.find(b'\0')].decode('ascii'))

                if hasattr(shape_data, 'objects'):
                    objects = shape_data.objects
                elif hasattr(shape_data, 'objects_v7'):
                    objects = shape_data.objects_v7

                if hasattr(shape_data, 'transforms'):
                    transforms = shape_data.transforms
                elif hasattr(shape_data, 'transforms_v7'):
                    transforms = shape_data.transforms_v7

                if hasattr(shape_data, 'nodes'):
                    nodes = shape_data.nodes
                elif hasattr(shape_data, 'nodes_v7'):
                    nodes = shape_data.nodes_v7

                if hasattr(shape_data, 'keyframes'):
                    keyframes = shape_data.keyframes
                elif hasattr(shape_data, 'keyframes_v7'):
                    keyframes = shape_data.keyframes_v7

                sequences = shape_data.sequences
                if hasattr(shape_data, 'subsequences'):
                    subsequences = shape_data.subsequences
                elif hasattr(shape_data, 'subsequences_v7'):
                    subsequences = shape_data.subsequences_v7
            else:
                print("Shape was not of TS::Shape")
                sys.exit(1)



            # Load textures
            if d.has_materials and d.materials:
                material_count = 0
                i = 0

                iflTextures = generate_ifl_materials(sequences, keyframes)
                    
                # Make a list of mapFiles, needed for IFL sequences
                for param in d.materials.params:
                    bitmap_name: bytes = param.map_file[:param.map_file.find(b'\0')]
                    mapFiles.append(bitmap_name.decode('ascii'))
                        
                for param in d.materials.params:
                    if i not in iflTextures:
                        bitmap_name: bytes = param.map_file[:param.map_file.find(b'\0')]
                        #texture = None
                        #if len(bitmap_name):
                        #    bitmap_name = bitmap_name.replace(b'.bmp', b'.png')
                        #    bitmap_name = bitmap_name.replace(b'.BMP', b'.png')
                        #   texture = 'const texture_' + str(i) + " = textureLoader.load('textures/{}')".format(
                        #       bitmap_name.decode('ascii'))

                        # Blender - Create a new material based on the model name and material id
                        mat = bpy.data.materials.new(filename.split(os.path.sep)[-1] + '.' + str(i))
                        mat.use_nodes = True

                        if param.flags & FLAG_TEXTURE_TRANSPARENT == FLAG_TEXTURE_TRANSPARENT or param.flags & FLAG_TEXTURE_TRANSLUCENT == FLAG_TEXTURE_TRANSLUCENT:
                            mat.blend_method = "BLEND"

                        mat_nodes = mat.node_tree.nodes
                        # check alpha paramater, may need to flip 0 to 1, and 1 to 0
                        mat_nodes["Principled BSDF"].inputs[0].default_value = (
                        srgb_to_linear_rgb(param.rgb.red), srgb_to_linear_rgb(param.rgb.green), srgb_to_linear_rgb(param.rgb.blue), param.alpha)

                        if len(bitmap_name):
                            store('map: {},'.format('texture_' + str(i)))
                            store('transparent: true,')

                            bitmap_name = bitmap_name.replace(b'.bmp', b'.png')
                            bitmap_name = bitmap_name.replace(b'.BMP', b'.png')

                            # Blender - Create the image texture node
                            shader_node = mat_nodes.new("ShaderNodeTexImage")
                            shader_node.location = -400, 200
                            shader_node.select = True
                            # Create the path to the image based on the model path
                            image_path = os.path.dirname(self.filepath) + os.path.sep + bitmap_name.decode('ascii')

                            # Check if .png exists
                            if os.path.exists(image_path):
                                shader_node.image = bpy.data.images.load(image_path)
                                pngORbmp = ".png"
                            # Check if .bmp exists
                            else:
                                image_path = image_path.rsplit('.', 1)[0] + ".bmp"
                                if os.path.exists(image_path):
                                    shader_node.image = bpy.data.images.load(image_path)
                                    pngORbmp = ".bmp"
                            # Link the image texture node to the color slot on the BSDF node
                            links = mat.node_tree.links
                            link = links.new(shader_node.outputs["Color"], mat_nodes["Principled BSDF"].inputs[0])

                            # Link the alpha input/output
                            links.new(shader_node.outputs["Alpha"], mat_nodes["Principled BSDF"].inputs[21])

                        textures.append(mat.name)
                    else:
                        textures.append(iflTextures[i])

                    # Blender - count materials, used for face maps
                    material_count += 1
                    i += 1

            # Make nodes
            # Create a dictionary of the nodes' children
            for j in range(0, len(nodes)):
                node_tree[j] = []
                nodes[j].id = j  # Set an ID on the nodes so we can reference it later
                for node2 in range(0, len(nodes)):
                    if nodes[node2].parent == j:
                        node_tree[j].append(node2)
            #pprint.pprint(node_tree)


            # Start with the roots, which come from the LODs
            # Find any needed parents for the roots. Should only be the bounds box (0)
            needed_parents = set()
            for lod_idx in range(0, len(shape_data.details)):
                if nodes[lod_idx].parent != -1:
                    needed_parents.add(nodes[lod_idx].parent)
            #print(needed_parents)

            # Root node (bounds)
            store('var node_0 = new THREE.Group();')
            store('node_0.position.set({}, {}, {});'.format(transforms[nodes[0].default_transform].translate.x, transforms[nodes[0].default_transform].translate.y, transforms[nodes[0].default_transform].translate.z))
            store('node_0.applyQuaternion(new THREE.Quaternion({}, {}, {}, {}));'.format(
                short2float(transforms[nodes[0].default_transform].rotate.x), short2float(transforms[nodes[0].default_transform].rotate.y), short2float(transforms[nodes[0].default_transform].rotate.z), short2float(transforms[nodes[0].default_transform].rotate.w)
            ))
            store('group.add(node_0);')

            # Set up the node hierarchy
            for child in node_tree[0]:
                create_nodes(nodes[child], nodes, transforms, node_tree)



            # Set up the node hierarchy
            # for j in range(0, len(nodes)):
            #     store('var node_{} = new THREE.Group();'.format(j))

            #     def_trans = transforms[nodes[j].default_transform]
            #     parent_trans = transforms[nodes[j].parent]
            #     store('node_{}.position.set({}, {}, {});'.format(j, def_trans.translate.x, def_trans.translate.y, def_trans.translate.z))
            #     #store('node_{}.setRotationFromQuaternion(new THREE.Quaternion({}, {}, {}, {}));'.format(
            #     #store('node_{}.applyQuaternion(new THREE.Quaternion({}, {}, {}, {}));'.format(
            #     #    j, short2float(def_trans.rotate.x), short2float(def_trans.rotate.y), short2float(def_trans.rotate.z), short2float(def_trans.rotate.w)
            #     #))

            #     if nodes[j].parent == -1: # or nodes[j].parent == 0xFFFFFFFF:
            #         store('node_{}.applyQuaternion(new THREE.Quaternion({}, {}, {}, {}));'.format(
            #             j, short2float(def_trans.rotate.x), short2float(def_trans.rotate.y), short2float(def_trans.rotate.z), short2float(def_trans.rotate.w)
            #         ))
            #         store('group.add(node_{});'.format(j))
            #     else:
            #         #store('console.log(node_{}.quaternion);'.format(nodes[j].parent))
            #         store('node_{}.applyQuaternion(new THREE.Quaternion({}, {}, {}, {}));'.format(
            #             j, short2float(parent_trans.rotate.x), short2float(parent_trans.rotate.y), short2float(parent_trans.rotate.z), short2float(parent_trans.rotate.w)
            #         ))
            #         store('node_{}.applyQuaternion(new THREE.Quaternion({}, {}, {}, {}));'.format(
            #             j, short2float(def_trans.rotate.x), short2float(def_trans.rotate.y), short2float(def_trans.rotate.z), short2float(def_trans.rotate.w)
            #         ))
            #         store('node_{}.add(node_{});'.format(nodes[j].parent, j))


            # Set up LoDs
            for lod in shape_data.details:
                store("""
                lods.push({{
                    node: node_{},
                    level: {}
                }});""".format(lod.root_node_index, lod.size))
                store('node_{}.visible = false;'.format(lod.root_node_index))
            store('lods[0].node.visible = true;')


            # Add meshes
            print('meshes')
            print()
            obj_id = 0
            mesh_data: Dts.TsAnimmesh
            for mesh_data in d.meshes:
                obj = objects[obj_id]
                obj_name = names[objects[obj_id].name]
                print(obj_name)
                parent_node = objects[obj_id].node_index
                array_verts_all = []  # Blender
                array_faces = []  # Blender
                array_faces_material = []  # Blender
                array_texvert = []  # Blender
                array_uvs = []  # Blender

                if hasattr(mesh_data, 'frames'):
                    frames = mesh_data.frames
                elif hasattr(mesh_data, 'frames_v2'):
                    frames = mesh_data.frames_v2

                if len(mesh_data.faces) == 0:
                    obj_id += 1
                    continue

                # Vertices
                # Add only vertices from Frame 0, this will be our Basis
                start_vertex = frames[0].first_vert
                for vrt_idx in range(mesh_data.num_vertices_per_frame):
                    # Blender - Put all the vertices in an array of [x, y, z]
#                    array_val = [vert.x * mesh_data.frames[0].scale.x, vert.y * mesh_data.frames[0].scale.y, vert.z * mesh_data.frames[0].scale.z]
                    array_val = [mesh_data.vertices[start_vertex + vrt_idx].x, mesh_data.vertices[start_vertex + vrt_idx].y, mesh_data.vertices[start_vertex + vrt_idx].z]
                    array_verts_all.append(array_val)

                # Faces
                for face in mesh_data.faces:
                    store('geometry.faces.push( new THREE.Face3( {}, {}, {}, null, null, {} ) );'.format(
                        face.vip[0].vertex_index,
                        face.vip[1].vertex_index,
                        face.vip[2].vertex_index,
                        face.material
                    ))
                    # Blender - Put all the faces in an array of [v1, v2, v3]
                    array_val = [face.vip[0].vertex_index, face.vip[1].vertex_index, face.vip[2].vertex_index]
                    array_faces.append(array_val)
                    array_faces_material.append(face.material)

                # Invert the normals
                store("""
                for ( var i = 0; i < geometry.faces.length; i ++ ) {

                    var face = geometry.faces[ i ];
                    var temp = face.a;
                    face.a = face.c;
                    face.c = temp;

                }

                geometry.computeFaceNormals();
                geometry.computeVertexNormals();
                            """)

                # Texture vertices
                store('textureVerts = [')
                for vert in mesh_data.texture_vertices:
                    # store('new THREE.Vector2({}, {}),'.format(
                    #     vert.x, vert.y
                    # ))
                    # Blender - Put all the texture vertices in an array of [x, 1-y]. Blender uses a different texture space coordinate.
                    array_val = [vert.x, 1 - vert.y]
                    array_texvert.append(array_val)
                store('];')

                # Set up UVs
                # store('geometry.faceVertexUvs = [[')
                for face in mesh_data.faces:
                    # store(' [ textureVerts[{}], textureVerts[{}], textureVerts[{}] ],'.format(
                    #     face.vip[0].texture_index, face.vip[1].texture_index, face.vip[2].texture_index
                    # ))
                    # Blender - Look up texture vertices from face indices
                    array_val = array_texvert[face.vip[0].texture_index]
                    array_uvs.append(array_val)
                    array_val = array_texvert[face.vip[1].texture_index]
                    array_uvs.append(array_val)
                    array_val = array_texvert[face.vip[2].texture_index]
                    array_uvs.append(array_val)
                # store(']];')

                # Flip UV normals
                store("""
                var faceVertexUvs = geometry.faceVertexUvs[ 0 ];
                for ( var i = 0; i < faceVertexUvs.length; i ++ )
                {
                    var temp = faceVertexUvs[ i ][ 0 ];
                    faceVertexUvs[ i ][ 0 ] = faceVertexUvs[ i ][ 2 ];
                    faceVertexUvs[ i ][ 2 ] = temp;
                }
                            """)

                # Scale it
                store('geometry.scale({}, {}, {});'.format(
                    mesh_data.frames[0].scale.x,
                    mesh_data.frames[0].scale.y,
                    mesh_data.frames[0].scale.z
                ))

                # Create the mesh
                #store('mesh = new THREE.Mesh( geometry, [{}] );'.format(', '.join(textures)))

                # Position the mesh
                store('mesh.position.set({}, {}, {});'.format(
                    mesh_data.frames[0].origin.x,
                    mesh_data.frames[0].origin.y,  # + (lod if is_lod_shape else 0),
                    mesh_data.frames[0].origin.z  # - (15 if (is_debris or is_hulk) else 0)
                ))

                # Add the mesh to the node's group
                store('node_{}.add(mesh);'.format(parent_node))

                # Blender - Create an object with the node's id
                mesh = bpy.data.meshes.new(obj_name)
                object = bpy.data.objects.new(obj_name, mesh)
                actual_object_name = object.name # Blender may append a .00x
                bpy.data.collections[filename].objects.link(object)
                object = bpy.context.scene.objects[actual_object_name]
                obj_dts_to_blender_map[obj_id] = actual_object_name
                object.data = mesh
                # Move Blender 3d cursor to object's pivot point, then set object pivot to 3d cursor
                bpy.context.scene.cursor.location = (0, 0, 0) #(transforms[nodes[0].default_transform].translate.x, transforms[nodes[0].default_transform].translate.y, transforms[nodes[0].default_transform].translate.z)
                bpy.context.scene.cursor.rotation_quaternion = (1, 0, 0, 0)
                bpy.context.scene.cursor.rotation_euler = (0, 0, 0)
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
                
                # Set the location and rotation of the object
                object.location = mathutils.Vector((mesh_data.frames[0].origin.x, mesh_data.frames[0].origin.y, mesh_data.frames[0].origin.z))
                object.rotation_mode = 'QUATERNION'
                #object.rotation_quaternion = [short2float(def_trans.rotate.x), short2float(def_trans.rotate.y), short2float(def_trans.rotate.z), short2float(def_trans.rotate.w)]
                # Create the mesh of the object
                mesh.from_pydata(array_verts_all, [], array_faces)

                animate_meshes(mesh_data, obj, names, keyframes, shape_data.sequences, subsequences, bpy.data.scenes['Scene'])

                object.scale = (mesh_data.frames[0].scale.x, mesh_data.frames[0].scale.y, mesh_data.frames[0].scale.z)
                # Select object by name
                ob = bpy.context.scene.objects[actual_object_name]  # Get the object
                bpy.ops.object.select_all(action='DESELECT')  # Deselect all objects
                bpy.context.view_layer.objects.active = ob  # Make the desired object the active object
                ob.select_set(True)  # Select the object
                # Create the face maps
                for tex in textures:
                    bpy.ops.object.face_map_add()
                    mat = bpy.data.materials.get(tex)
                    object.data.materials.append(mat)

                # Switch object modes, not sure why we have to go into edit mode and than back to object mode
                ob = bpy.context.active_object
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_mode(type="FACE")
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='OBJECT')
                # Loop through all faces and assign to face map and assign material
                x = 0
                for k in ob.data.polygons:
                    ob.data.polygons[x].select = True
                    bpy.ops.object.mode_set(mode='EDIT')
                    ob.face_maps.active_index = int(array_faces_material[x])
                    bpy.ops.object.face_map_assign()
                    # Assign material
                    bpy.context.object.active_material_index = int(array_faces_material[x])
                    bpy.ops.object.material_slot_assign()
                    # Deselect faces so their mapping doesn't change
                    bpy.ops.object.face_map_deselect()
                    bpy.ops.object.mode_set(mode='OBJECT')
                    x += 1

                # Create the UV map
                new_uv = ob.data.uv_layers.new(name='UV Map')
                for loop in ob.data.loops:
                    new_uv.data[loop.index].uv = array_uvs[loop.index]

                obj_id += 1

            # Blender - Create Objects for all nodes, with dummy meshes, find parents
            array_parents = []   
            for node in nodes:
                obj = bpy.context.scene.objects.get(names[node.name])
                if not obj:
                    object = bpy.data.objects.new(names[node.name], None)
                    object.rotation_mode = 'QUATERNION'
                    bpy.data.collections[filename].objects.link(object)
                if node.parent != -1:
                    array_val = [names[node.name], names[nodes[node.parent].name]]
                    array_parents.append(array_val)
                    
            # Blender - Find parents for all objects
            pprint.pp(obj_dts_to_blender_map)
            for obj_id in range(len(objects)):
                obj = objects[obj_id]
                # Some objects don't get created in Blender (e.g. bounds)
                if obj_id not in obj_dts_to_blender_map:
                    continue

                array_val = [obj_dts_to_blender_map[obj_id], names[nodes[obj.node_index].name]]
                array_parents.append(array_val)
                print(obj_id, obj_dts_to_blender_map[obj_id], obj.node_index, names[nodes[obj.node_index].name])
                        
            # Blender - Parent all the objects
            x = 0
            for obj in array_parents:
                #print(str(array_parents[x][0]), '->', str(array_parents[x][1]))
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = bpy.context.scene.objects[array_parents[x][1]] # Parent
                bpy.context.scene.objects[array_parents[x][1]].select_set(True) # Parent
                bpy.context.scene.objects[array_parents[x][0]].select_set(True) # First child
                bpy.ops.object.parent_set(type='OBJECT')
                x += 1
                    
            # Blender - Move the nodes
            for node in nodes:
                def_trans = transforms[nodes[node.id].default_transform]
                object = bpy.context.scene.objects[names[nodes[node.id].name]]
                object.location = [def_trans.translate.x, def_trans.translate.y, def_trans.translate.z]
                #object.rotation_quaternion = [short2float(def_trans.rotate.x), short2float(def_trans.rotate.y), short2float(def_trans.rotate.z), short2float(def_trans.rotate.w)]
                object.rotation_quaternion = [short2float(def_trans.rotate.w) * -1, short2float(def_trans.rotate.x), short2float(def_trans.rotate.y), short2float(def_trans.rotate.z)]
            
            shape_data: Dts.TsShape = d.shape.data.obj_data
            # Create a panel to hold sequences
            store("""
            const panel = new GUI( { width: 310 } );
            const folder_lod = panel.addFolder('Level of Detail');
            const folder_seq = panel.addFolder('Sequences');

            var _sequences = {};
            """)

            store("""
            controller_settings = {{
                lod: {defLOD}
            }};
            """.format(defLOD=int(shape_data.details[0].size)))
            store('folder_lod.add( controller_settings, "lod", [ {} ] ).name( "Level" ).onChange( updateLod );'.format(
                ', '.join(str(int(x.size)) for x in shape_data.details)
            ))
            store('folder_lod.open();')

            for sequence in shape_data.sequences:
                # store(str(names[sequence.name]))
                seq_name_ascii = names[sequence.name]
                store('_sequences["{}"] = true;'.format(seq_name_ascii))
                store('folder_seq.add(_sequences, "{}");'.format(seq_name_ascii))

            store('folder_seq.open();')



            # Create the sequences
            scene = bpy.data.scenes['Scene']

            # Iterate through all sequences and generate key frames for each object participating in that sequence
            for seq_id in range(len(shape_data.sequences)):
                sequence: Dts.VectorSequence = shape_data.sequences[seq_id]
                seq_name = names[sequence.name]
                print(seq_name)
                scene.timeline_markers.new(seq_name, frame=frame_id)

                if sequence.num_ifl_subsequences > 0:
                    # IFL sequence
                    print("IFL sequence")

                    # A sequence may have multiple IFL subsequences, for different materials
                    for subseq_count in range(sequence.num_ifl_subsequences):
                        subseq = subsequences[sequence.first_ifl_subsequence + subseq_count]
                        print('num key frames:', subseq.num_keyframes)

                        first_keyframe = subseq.first_keyframe
                        ifl_mat = bpy.data.materials.get('ifl_{}_{}'.format(seq_name, subseq_count))
                        value_node = ifl_mat.node_tree.nodes.get("IFL Input Value")

                        val = 0
                        for key in range(first_keyframe, first_keyframe + subseq.num_keyframes):
                            value_node.outputs["Value"].default_value = val
                            value_node.outputs["Value"].keyframe_insert(data_path="default_value", index=-1)
                            scene.frame_set(frame_id)
                            val += 1
                            frame_id += 1

                else:
                    # Node sequence
                    # Find the node with a sequence that corresponds to it
                    node_id = 0
                    last_subseq_len = 0
                    for node in nodes:
                        if node.num_subsequences:  # TODO: LODs

                            # A node may have multiple subsequences, go through all of them
                            for subseq_count in range(node.num_subsequences):
                                subseq = subsequences[node.first_subsequence + subseq_count]
                                if subseq.sequence_index == seq_id:
                                    print('num key frames:', subseq.num_keyframes)
                                    first_keyframe = subseq.first_keyframe

                                    #Blender
                                    blender_frame = frame_id
                                    object = bpy.context.scene.objects[str(names[nodes[node_id].name])]
                                    # Actions will be created for each object animated. Bones will need to be created to be used with armors.
                                    #object.animation_data_create() #
                                    #object.animation_data.action = bpy.data.actions.new(name=seq_name) #
                                    for key in range(first_keyframe, first_keyframe + subseq.num_keyframes):
                                        trans = transforms[keyframes[key].key_value]
                                        scene.frame_set(blender_frame) #Blender
                                        object.location = [trans.translate.x, trans.translate.y, trans.translate.z]
                                        object.rotation_quaternion = [short2float(trans.rotate.w) * -1, short2float(trans.rotate.x), short2float(trans.rotate.y), short2float(trans.rotate.z)] #Blender
                                        object.keyframe_insert(data_path="rotation_quaternion", index=-1)
                                        object.keyframe_insert(data_path="location", index=-1)
                                        blender_frame += 1 #Blender
                                    last_subseq_len = subseq.num_keyframes

                        node_id += 1
                    frame_id += last_subseq_len
                    
        return {'FINISHED'}