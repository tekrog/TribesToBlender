from .dts import Dts
import sys
import os
import os.path
import pprint

import bpy
import bmesh
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

        filename = self.filepath.split('/')[-1].split('.')[0]
        path = self.filepath
        
        # Collection created, but not used yet
        obj_collection = bpy.data.collections.new(filename)
        context.scene.collection.children.link(obj_collection)

        with open(path, 'r') as f:
            def store(str=''):
                print(str)
                with open(out_path, 'a') as f:
                    f.write(str + "\n")
                
            def short2float(short):
                if short == 0:
                    return 0
                return float(short) / float(0x7FFF)

            def create_nodes(node: Dts.Node, nodes, transforms, node_tree):
                store('var node_{} = new THREE.Group();'.format(node.id))

                def_trans = transforms[nodes[node.id].default_transform]
                if nodes[node.id].parent == -1:
#                    store('node_{}.position.set({}, {}, {});'.format(node.id, def_trans.translate.x, def_trans.translate.y, def_trans.translate.z))
#                    store('node_{}.applyQuaternion(new THREE.Quaternion({}, {}, {}, {}));'.format(
#                        node.id, short2float(def_trans.rotate.x), short2float(def_trans.rotate.y), short2float(def_trans.rotate.z), short2float(def_trans.rotate.w)
 #                   ))
                    store('group.add(node_{});'.format(node.id))
                    # Create an object with the node's id
                    object = bpy.data.objects.new(str(node.id), None)
                    bpy.data.collections[filename].objects.link(object)
                    object.location = [def_trans.translate.x, def_trans.translate.y, def_trans.translate.z]
                    object.rotation_quaternion = [short2float(def_trans.rotate.x), short2float(def_trans.rotate.y), short2float(def_trans.rotate.z), short2float(def_trans.rotate.w)]
                    
                else:
                    #store('console.log(node_{}.quaternion);'.format(nodes[node.id].parent))
#                    store('node_{}.translateX({});'.format(node.id, def_trans.translate.x))
#                    store('node_{}.translateY({});'.format(node.id, def_trans.translate.y))
#                    store('node_{}.translateZ({});'.format(node.id, def_trans.translate.z))
#                    store('node_{}.applyQuaternion(node_{}.quaternion);'.format(node.id, nodes[node.id].parent))
#                    store('node_{}.applyQuaternion(new THREE.Quaternion({}, {}, {}, {}).invert());'.format(
#                        node.id, short2float(def_trans.rotate.x), short2float(def_trans.rotate.y), short2float(def_trans.rotate.z), short2float(def_trans.rotate.w)
#                    ))
#                    store('node_{}.add(node_{});'.format(nodes[node.id].parent, node.id))

## Fix translation
                    # Create an object with the node's id
                    object = bpy.data.objects.new(str(node.id), None)
                    bpy.data.collections[filename].objects.link(object)
                    object.location = [def_trans.translate.x, def_trans.translate.y, def_trans.translate.z]
                    object.rotation_quaternion = [short2float(def_trans.rotate.x), short2float(def_trans.rotate.y), short2float(def_trans.rotate.z), short2float(def_trans.rotate.w)]

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
                        texture = 'const texture_' + str(i) + " = textureLoader.load('textures/{}')".format(bitmap_name.decode('ascii'))

                    # Blender - Create a new material based on the model name and material id
                    mat = bpy.data.materials.new(filename.split('\\')[-1] + '.' + str(i))
                    mat.use_nodes = True
                    nodes = mat.node_tree.nodes
# check alpha paramater, may need to flip 0 to 1, and 1 to 0
                    nodes["Principled BSDF"].inputs[0].default_value = (param.rgb.red, param.rgb.green, param.rgb.blue, param.alpha)
                    
                    if len(bitmap_name):
                        store('map: {},'.format('texture_' + str(i)))
                        store('transparent: true,')
                        
                        # Blender - Create the image texture node
                        shader_node = nodes.new("ShaderNodeTexImage")
                        shader_node.location = -400,200
                        shader_node.select = True
                        # Create the path to the image based on the model path
                        image_path = filename.rsplit('\\', 1)[0] + '\\' + bitmap_name.decode('ascii')
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
                # Create an object with the root node's name
                object = bpy.data.objects.new('node_0', None)
                bpy.data.collections[filename].objects.link(object)
                object.location = [transforms[nodes[0].default_transform].translate.x, transforms[nodes[0].default_transform].translate.y, transforms[nodes[0].default_transform].translate.z]
                object.rotation_quaternion = [short2float(transforms[nodes[0].default_transform].rotate.x), short2float(transforms[nodes[0].default_transform].rotate.y), short2float(transforms[nodes[0].default_transform].rotate.z), short2float(transforms[nodes[0].default_transform].rotate.w)]

                # Set up the node hierarchy
                for child in node_tree[0]:
                    create_nodes(nodes[child], nodes, transforms, node_tree)

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
            obj_id = 0
            mesh_data: Dts.TsAnimmesh
            for mesh_data in d.meshes:
                is_debris = False
                is_lod_shape = False
                is_hulk = False
                lod = 0
                obj_name = names[objects[obj_id].name]
                parent_node = objects[obj_id].node_index
                array_verts_all = [] # Blender
                array_faces = [] # Blender
                array_faces_material = [] # Blender

                if b'debris' in obj_name:
                    is_debris = True
                elif b' ' in obj_name:
                    is_lod_shape = True
                    lod_parts = obj_name.split(b' ')
                    lod = int(lod_parts[len(lod_parts) - 1])

                if b'hulk' in obj_name:
                    is_hulk = True

                obj_id += 1
                # if not is_lod_shape and not is_debris:
                #    continue

                # TEMP TODO: Toggle LODs and hulks
                # if is_hulk or lod != 15:#128:#15:
                #    continue

                if is_hulk or is_debris:
                    continue

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
                    store('new THREE.Vector2({}, {}),'.format(
                        vert.x, vert.y
                    ))
                store('];')

                # Set up UVs
                store('geometry.faceVertexUvs = [[')
                for face in mesh_data.faces:
                    store(' [ textureVerts[{}], textureVerts[{}], textureVerts[{}] ],'.format(
                        face.vip[0].texture_index, face.vip[1].texture_index, face.vip[2].texture_index
                    ))
                store(']];')

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
                # Put the object in a collection
                bpy.data.collections[filename].objects.link(object)
                # Set the location and rotation of the object
                object.location = [mesh_data.frames[0].origin.x, mesh_data.frames[0].origin.y, mesh_data.frames[0].origin.z]
                #object.rotation_quaternion = [short2float(def_trans.rotate.x), short2float(def_trans.rotate.y), short2float(def_trans.rotate.z), short2float(def_trans.rotate.w)]
                # Create the mesh of the object
                mesh.from_pydata(array_verts_all,[],array_faces)
                object.scale = (mesh_data.frames[0].scale.x, mesh_data.frames[0].scale.y, mesh_data.frames[0].scale.z)
                # Select object by name
                ob = bpy.context.scene.objects[str(obj_name)]       # Get the object
                bpy.ops.object.select_all(action='DESELECT') # Deselect all objects
                bpy.context.view_layer.objects.active = ob   # Make the desired object the active object 
                ob.select_set(True)                          # Select the object                
                # Create the face maps
                x = 0
                while (x < material_count):
                    bpy.ops.object.face_map_add()
                    mat = bpy.data.materials.get(filename.split('\\')[-1] + '.' + str(x))
                    object.data.materials.append(mat)
                    x += 1
                # Switch object modes, not sure why we have to go into edit mode and than back to object mode
                ob = bpy.context.active_object
                bpy.ops.object.mode_set(mode = 'EDIT') 
                bpy.ops.mesh.select_mode(type="FACE")
                bpy.ops.mesh.select_all(action = 'DESELECT')
                bpy.ops.object.mode_set(mode = 'OBJECT')
                # Loop through all faces and assign to face map
                x = 0
                for k in ob.data.polygons:
                    ob.data.polygons[x].select = True
                    bpy.ops.object.mode_set(mode = 'EDIT')
                    ob.face_maps.active_index = int(array_faces_material[x])
                    bpy.ops.object.face_map_assign()
                    # Deselect faces so their mapping doesn't change
                    bpy.ops.object.face_map_deselect()
                    bpy.ops.object.mode_set(mode = 'OBJECT')
                    x += 1

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

            node_id = 0
            for node in nodes:
                if node.num_subsequences: # TODO: LODs
                    subseq = subsequences[node.first_subsequence]
                    store("""
            const animationGroup_node{} = new THREE.AnimationObjectGroup();
            animationGroup_node{}.add( node_{} );
                    """.format(node_id, node_id, node_id))
                    first_keyframe = subseq.first_keyframe

                    store("""
            const quaternionKF_node{} = new THREE.QuaternionKeyframeTrack( 
            '.quaternion', 
                        """.format(node_id))
                    store('[')
                    for key in range(first_keyframe, first_keyframe + subseq.num_keyframes):
                        store('{}, '.format(keyframes[key].position * shape_data.sequences[subseq.sequence_index].duration))
                    store(']')

                    store(', [')
                    for key in range(first_keyframe, first_keyframe + subseq.num_keyframes):
                        trans = transforms[keyframes[key].key_value]
                        store('{}, {}, {}, {}, '.format(
                            short2float(trans.rotate.x), short2float(trans.rotate.y), short2float(trans.rotate.z), short2float(trans.rotate.w)
                        ))
                    store(']);')

                    store("""
            const clip_node{n_id} = new THREE.AnimationClip( '{seq_name}', {duration}, [ quaternionKF_node{n_id} ] );

            let mixer_node{n_id} = new THREE.AnimationMixer( animationGroup_node{n_id} );
            const clipAction_node{n_id} = mixer_node{n_id}.clipAction( clip_node{n_id} );
            //clipAction_node{n_id}.play();
            mixers.push(mixer_node{n_id});
                    """.format(n_id=node_id, seq_name=names[shape_data.sequences[subseq.sequence_index].name].decode('ascii'), duration=shape_data.sequences[subseq.sequence_index].duration))
                node_id += 1

            # Create the power sequence
            if b'power' in names:
                # Find the sequence ID for the power sequence
                seq_id = 0
                for sequence in shape_data.sequences:
                    if names[sequence.name] == b'power':
                        break
                    seq_id += 1

                # TODO: HANDLE IFL SEQUENCES

                subsequences = None
                if hasattr(shape_data, 'subsequences'):
                    subsequences = shape_data.subsequences
                elif hasattr(shape_data, 'subsequences_v7'):
                    subsequences = shape_data.subsequences_v7

                # Find the node with a sequence that corresponds to it
                node_id = 0
                for node in nodes:
                    lod = 0
                    if b' ' in names[node.name]:
                        is_lod_shape = True
                        lod_parts = names[node.name].split(b' ')
                        lod = int(lod_parts[len(lod_parts) - 1])

                    if node.num_subsequences and lod == 15: # TODO: LODs
                        subseq = subsequences[node.first_subsequence]
                        if subseq.sequence_index == seq_id:
                            store("""
            const animationGroup_node{} = new THREE.AnimationObjectGroup();
            animationGroup_node{}.add( node_{} );
                            """.format(node_id, node_id, node_id))
                            first_keyframe = subseq.first_keyframe

                            store("""
            const quaternionKF_node{} = new THREE.QuaternionKeyframeTrack( 
            '.quaternion', 
                                """.format(node_id))
                            store('[')
                            for key in range(first_keyframe, first_keyframe + subseq.num_keyframes):
                                store('{}, '.format(shape_data.keyframes[key].position * shape_data.sequences[seq_id].duration))
                            store(']')

                            store(', [')
                            for key in range(first_keyframe, first_keyframe + subseq.num_keyframes):
                                trans = transforms[shape_data.keyframes[key].key_value]
                                store('{}, {}, {}, {}, '.format(
                                    short2float(trans.rotate.x), short2float(trans.rotate.y), short2float(trans.rotate.z), short2float(trans.rotate.w)
                                ))
                            store(']);')

                            store("""
            const clip_node{n_id} = new THREE.AnimationClip( '{seq_name}', {duration}, [ quaternionKF_node{n_id} ] );

            let mixer_node{n_id} = new THREE.AnimationMixer( animationGroup_node{n_id} );
            const clipAction_node{n_id} = mixer_node{n_id}.clipAction( clip_node{n_id} );
            clipAction_node{n_id}.play();
            mixers.push(mixer_node{n_id});
                            """.format(n_id=node_id, seq_name=names[shape_data.sequences[seq_id].name].decode('ascii'), duration=shape_data.sequences[seq_id].duration))
                    node_id += 1
                    
        return {'FINISHED'}