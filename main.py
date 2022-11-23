from .dts import Dts
import sys
import os
import os.path
import pprint

import bpy
import bmesh
import mathutils
from bpy import ops
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, FloatProperty


class ImportDTS(bpy.types.Operator, ImportHelper):
    bl_idname = "dynamix.dts"
    bl_label = "Import Starsiege: Tribes .dts"
    bl_description = 'Imports Starsiege: Tribes .dts file.'

    filter_glob : StringProperty(default="*.dts", options={'HIDDEN'})
    filename_ext = ".dts"
    
    def execute(self, context):
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

            #file_path = "./shapes/indoorgun.DTS"

            out_path = filename + ".html"

            if os.path.exists(out_path):
                os.truncate(out_path, 0)

#            with open('header.html', 'r') as f:
#                with open(out_path, 'w') as g:
#                    g.write(f.read())
            
            d = Dts.from_file(path)

            MAX_VAL = float(0x7FFF)
            names = []
            nodes = []
            objects = []
            textures = []
            transforms = []
            node_tree = {}

            store('var geometry = null;')
            store('var mesh = null;')
            store('var texture = null;')
            store('var material = null;')
            store('var textureVerts = null;')

            # Load textures
            if d.has_materials and d.materials:
                material_count = 0
                i = 0
                for param in d.materials.params:
                    bitmap_name: bytes = param.map_file[:param.map_file.find(b'\0')]
                    texture = None
                    if len(bitmap_name):
                        bitmap_name = bitmap_name.replace(b'.bmp', b'.png')
                        bitmap_name = bitmap_name.replace(b'.BMP', b'.png')
                        texture = 'const texture_' + str(i) + " = textureLoader.load('textures/{}')".format(
                            bitmap_name.decode('ascii'))

                    # Blender - Create a new material based on the model name and material id
                    mat = bpy.data.materials.new(filename.split(os.path.sep)[-1] + '.' + str(i))
                    mat.use_nodes = True
                    nodes = mat.node_tree.nodes
                    # check alpha paramater, may need to flip 0 to 1, and 1 to 0
                    nodes["Principled BSDF"].inputs[0].default_value = (
                    param.rgb.red, param.rgb.green, param.rgb.blue, param.alpha)

                    if len(bitmap_name):
                        store('map: {},'.format('texture_' + str(i)))
                        store('transparent: true,')

                        # Blender - Create the image texture node
                        shader_node = nodes.new("ShaderNodeTexImage")
                        shader_node.location = -400, 200
                        shader_node.select = True
                        # Create the path to the image based on the model path
                        image_path = os.path.dirname(self.filepath) + os.path.sep + bitmap_name.decode('ascii')
                        print(image_path)
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
                        link = links.new(shader_node.outputs["Color"], nodes["Principled BSDF"].inputs[0])

                    textures.append('material_' + str(i))
                    # Blender - count materials, used for face maps
                    material_count += 1

                    i += 1

            # Make nodes
            if b'TS::Shape' in d.shape.data.classname:
                shape_data: Dts.TsShape = d.shape.data.obj_data

                for name in shape_data.names:
                    names.append(name[:name.find(b'\0')])

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
            else:
                print("Shape was not of TS::Shape")
                sys.exit(1)

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
                is_debris = False
                is_lod_shape = False
                is_hulk = False
                lod = 0
                obj_name = names[objects[obj_id].name]
                print(str(obj_name))
                parent_node = objects[obj_id].node_index
                array_verts_all = []  # Blender
                array_faces = []  # Blender
                array_faces_material = []  # Blender
                array_texvert = []  # Blender
                array_uvs = []  # Blender

                if b'debris' in obj_name:
                    is_debris = True
                elif b' ' in obj_name:
                    lod_parts = obj_name.split(b' ')
                    second_name = lod_parts[len(lod_parts) - 1]

                    if second_name.decode('ascii').isnumeric():
                        is_lod_shape = True
                        lod = int(second_name)

                if b'hulk' in obj_name:
                    is_hulk = True

                obj_id += 1
                # if not is_lod_shape and not is_debris:
                #    continue

                # TEMP TODO: Toggle LODs and hulks
                # if is_hulk or lod != 15:#128:#15:
                #    continue

#                if is_hulk or is_debris:
#                    continue

                if len(mesh_data.faces) == 0:
                    continue

                store()
                store('//{}'.format(obj_name))
                store('geometry = new THREE.Geometry();')

                # Vertices
                for vert in mesh_data.vertices:
                    store('geometry.vertices.push( new THREE.Vector3( {}, {}, {} ) );'.format(
                        vert.x, vert.y, vert.z
                    ))
                    # Blender - Put all the vertices in an array of [x, y, z]
#                    array_val = [vert.x * mesh_data.frames[0].scale.x, vert.y * mesh_data.frames[0].scale.y, vert.z * mesh_data.frames[0].scale.z]
                    array_val = [vert.x, vert.y, vert.z]
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
                store('mesh = new THREE.Mesh( geometry, [{}] );'.format(', '.join(textures)))

                # Position the mesh
                store('mesh.position.set({}, {}, {});'.format(
                    mesh_data.frames[0].origin.x,
                    mesh_data.frames[0].origin.y,  # + (lod if is_lod_shape else 0),
                    mesh_data.frames[0].origin.z  # - (15 if (is_debris or is_hulk) else 0)
                ))

                # Add the mesh to the node's group
                store('node_{}.add(mesh);'.format(parent_node))

                # Blender - Create an object with the node's id
                mesh = bpy.data.meshes.new(str(obj_name))
                object = bpy.data.objects.new(str(obj_name), mesh)
                bpy.data.collections[filename].objects.link(object)
                object = bpy.context.scene.objects[str(obj_name)]
                object.data = mesh
                # Move Blender 3d cursor to object's pivot point, then set object pivot to 3d cursor
                bpy.context.scene.cursor.location = (transforms[nodes[0].default_transform].translate.x, transforms[nodes[0].default_transform].translate.y, transforms[nodes[0].default_transform].translate.z)
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
                
                # Set the location and rotation of the object
                object.location = object.location + mathutils.Vector((mesh_data.frames[0].origin.x, mesh_data.frames[0].origin.y, mesh_data.frames[0].origin.z))
                object.rotation_mode = 'QUATERNION'
                #object.rotation_quaternion = [short2float(def_trans.rotate.x), short2float(def_trans.rotate.y), short2float(def_trans.rotate.z), short2float(def_trans.rotate.w)]
                # Create the mesh of the object
                mesh.from_pydata(array_verts_all, [], array_faces)
                object.scale = (mesh_data.frames[0].scale.x, mesh_data.frames[0].scale.y, mesh_data.frames[0].scale.z)
                # Select object by name
                ob = bpy.context.scene.objects[str(obj_name)]  # Get the object
                bpy.ops.object.select_all(action='DESELECT')  # Deselect all objects
                bpy.context.view_layer.objects.active = ob  # Make the desired object the active object
                ob.select_set(True)  # Select the object
                # Create the face maps
                x = 0
                while (x < material_count):
                    bpy.ops.object.face_map_add()
                    mat = bpy.data.materials.get(filename.split('\\')[-1] + '.' + str(x))
                    object.data.materials.append(mat)
                    x += 1
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

            # Blender - Create Objects for all nodes, with dummy meshes, find parents
            array_parents = []   
            for node in nodes:
                obj = bpy.context.scene.objects.get(str(names[node.name]))
                if not obj:
                    object = bpy.data.objects.new(str(names[node.name]), None)
                    bpy.data.collections[filename].objects.link(object)
                if node.parent != -1:
                    array_val = [str(names[node.name]), str(names[nodes[node.parent].name])]
                    array_parents.append(array_val)
                    
            # Blender - Find parents for all objects
            for obj in objects:
                array_val = [str(names[obj.name]), str(names[nodes[obj.node_index].name])]
                array_parents.append(array_val)
                        
            # Blender - Parent all the objects
            x = 0
            for obj in array_parents:
                #print(str(array_parents[x][0]), '->', str(array_parents[x][1]))
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = bpy.context.scene.objects[str(array_parents[x][1])] 
                bpy.context.scene.objects[str(array_parents[x][1])].select_set(True)
                bpy.context.scene.objects[str(array_parents[x][0])].select_set(True)
                bpy.ops.object.parent_set(type='OBJECT')
                x += 1
                    
            # Blender - Move the nodes
            for node in nodes:
                def_trans = transforms[nodes[node.id].default_transform]
                object = bpy.context.scene.objects[str(names[nodes[node.id].name])]
                object.location = [def_trans.translate.x, def_trans.translate.y, def_trans.translate.z]
                #object.rotation_quaternion = [short2float(def_trans.rotate.x), short2float(def_trans.rotate.y), short2float(def_trans.rotate.z), short2float(def_trans.rotate.w)]
                object.rotation_quaternion = [short2float(def_trans.rotate.w), short2float(def_trans.rotate.x), short2float(def_trans.rotate.y), short2float(def_trans.rotate.z)]
            
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
                seq_name_ascii = names[sequence.name].decode('ascii')
                store('_sequences["{}"] = true;'.format(seq_name_ascii))
                store('folder_seq.add(_sequences, "{}");'.format(seq_name_ascii))

            store('folder_seq.open();')



            # Create the sequences

            # TODO: HANDLE IFL SEQUENCES
            scene = bpy.data.scenes['Scene']
            subsequences = None
            keyframes = None
            if hasattr(shape_data, 'subsequences'):
                subsequences = shape_data.subsequences
            elif hasattr(shape_data, 'subsequences_v7'):
                subsequences = shape_data.subsequences_v7

            if hasattr(shape_data, 'keyframes'):
                keyframes = shape_data.keyframes
            elif hasattr(shape_data, 'keyframes_v7'):
                keyframes = shape_data.keyframes_v7


            # Iterate through all sequences and generate key frames for each object participating in that sequence
            frame_id = 0
            for seq_id in range(len(shape_data.sequences)):
                seq_name = names[shape_data.sequences[seq_id].name].decode('ascii')
                scene.timeline_markers.new(seq_name, frame=frame_id)

                # Find the node with a sequence that corresponds to it
                node_id = 0
                last_subseq_len = 0
                for node in nodes:
                    if node.num_subsequences:  # TODO: LODs
                        subseq = subsequences[node.first_subsequence]
                        if subseq.sequence_index == seq_id:
                            first_keyframe = subseq.first_keyframe

                            #Blender
                            blender_frame = frame_id
                            object = bpy.context.scene.objects[str(names[nodes[node_id].name])]
                            for key in range(first_keyframe, first_keyframe + subseq.num_keyframes):
                                trans = transforms[keyframes[key].key_value]
                                scene.frame_set(blender_frame) #Blender
                                object.rotation_quaternion = [short2float(trans.rotate.w), short2float(trans.rotate.x), short2float(trans.rotate.y), short2float(trans.rotate.z)] #Blender
                                object.keyframe_insert(data_path="rotation_quaternion", index=-1)
                                blender_frame += 1 #Blender
                            last_subseq_len = subseq.num_keyframes

                    node_id += 1
                frame_id += last_subseq_len
                    
        return {'FINISHED'}