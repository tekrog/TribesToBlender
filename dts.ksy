meta:
  id: dts
  file-extension: dts
  endian: le
seq:
  #- id: sections
  #  type: section
  #  repeat: eos
    #repeat: expr
    #repeat-expr: 1
  - id: shape
    type: section
  - id: meshes
    type: section
    repeat: expr
    repeat-expr: shape.data.as<pers_data>.obj_data.as<ts_shape>.num_meshes
  - id: has_materials
    type: s4
  - id: materials
    type: section
    if: has_materials == 1
  
types:
  dummy:
    seq:
      - id: no_value
        size: 0
        
  shape_data:
    seq:
      - id: data
        type: section
  
  point2f:
    seq:
      - id: x
        type: f4
      - id: y
        type: f4
  point3f:
    seq:
      - id: x
        type: f4
      - id: y
        type: f4
      - id: z
        type: f4
  box3f:
    seq:
      - id: min
        type: point3f
      - id: max
        type: point3f
  node:
    seq:
      - id: name
        type: u2
      - id: parent
        type: s2
      - id: num_subsequences
        type: u2
      - id: first_subsequence
        type: u2
      - id: default_transform
        type: u2
  nodev7:
    seq:
      - id: name
        type: u4
      - id: parent
        type: s4
      - id: num_subsequences
        type: u4
      - id: first_subsequence
        type: u4
      - id: default_transform
        type: u4
  vector_sequence:
    seq:
      - id: name
        type: u4
      - id: cyclic
        type: u4
      - id: duration
        type: f4
      - id: priority
        type: u4
      - id: first_frame_trigger
        type: u4
      - id: num_frame_triggers
        type: u4
      - id: num_ifl_subsequences
        type: u4
      - id: first_ifl_subsequence
        type: u4
  subsequence:
    seq:
      - id: sequence_index
        type: u2
      - id: num_keyframes
        type: u2
      - id: first_keyframe
        type: u2
  subsequencev7:
    seq:
      - id: sequence_index
        type: u4
      - id: num_keyframes
        type: u4
      - id: first_keyframe
        type: u4
  keyframe:
    seq:
      - id: position
        type: f4
      - id: key_value
        type: u2
      - id: mat_index
        type: u2
  keyframev7:
    seq:
      - id: position
        type: f4
      - id: key_value
        type: u4
      - id: mat_index
        type: u4
  quat16:
    seq:
      - id: x
        type: s2
      - id: y
        type: s2
      - id: z
        type: s2
      - id: w
        type: s2
  transform:
    seq:
      - id: rotate
        type: quat16
      - id: translate
        type: point3f
  transformv7:
    seq:
      - id: rotate
        type: quat16
      - id: translate
        type: point3f
      - id: scale
        type: point3f
  tmat3f:
    seq:
      - id: flags
        type: u4
      - id: m
        type: f4
        repeat: expr
        repeat-expr: 9
      - id: p
        type: point3f
  objectv8:
    seq:
      - id: name
        type: s2
      - id: flags
        type: u2
      - id: mesh_index
        type: s4
      - id: node_index
        type: s2
      - id: object_offset
        type: point3f
      - id: num_subsequences
        type: u2
      - id: first_subsequence
        type: u2
      - id: dummy
        type: u2
  objectv7:
    seq:
      - id: name
        type: u2
      - id: flags
        type: u2
      - id: mesh_index
        type: u4
      - id: node_index
        type: u4
      - id: object_offset
        type: tmat3f
      - id: num_subsequences
        type: u4
      - id: first_subsequence
        type: u4
  detail:
    seq:
      - id: root_node_index
        type: u4
      - id: size
        type: f4
  transition:
    seq:
      - id: start_sequence
        type: u4
      - id: end_sequence
        type: u4
      - id: start_position
        type: f4
      - id: end_position
        type: f4
      - id: duration
        type: f4
      - id: transform
        type: transform
  transitionv7:
    seq:
      - id: start_sequence
        type: u4
      - id: end_sequence
        type: u4
      - id: start_position
        type: f4
      - id: end_position
        type: f4
      - id: transform
        type: transformv7
  frame_trigger:
    seq:
      - id: position
        type: f4
      - id: value
        type: u4
  packed_vertex:
    seq:
      #- id: normal_table
      #  type: u4
      - id: x
        type: u1
      - id: y
        type: u1
      - id: z
        type: u1
      - id: normal
        type: u1
  vertex_index_pair:
    seq:
      - id: vertex_index
        type: u4
      - id: texture_index
        type: u4
  face:
    seq:
      - id: vip
        type: vertex_index_pair
        repeat: expr
        repeat-expr: 3
      - id: material
        type: u4
      #- id: dummy
      #  type: u2
  framev2:
    seq:
      - id: first_vert
        type: u4
  frame:
    seq:
      - id: first_vert
        type: s4
      - id: scale
        type: point3f
      - id: origin
        type: point3f
  rgb:
    seq:
      - id: red
        type: u1
      - id: green
        type: u1
      - id: blue
        type: u1
      - id: flags
        type: u1
  material_params:
    seq:
      - id: flags
        type: s4
      - id: alpha
        type: f4
      - id: index
        type: s4
      - id: rgb
        type: rgb
      - id: map_file_old
        type: str
        encoding: ASCII
        size: 16
        if: _parent._parent.version == 1
      - id: map_file
        type: str
        encoding: ASCII
        size: 32
        if: _parent._parent.version >= 2
      - id: type
        type: s4
        if: _parent._parent.version >= 3
      - id: elasticity
        type: f4
        if: _parent._parent.version >= 3
      - id: friction
        type: f4
        if: _parent._parent.version >= 3
      - id: use_default_props
        type: u4
        if: _parent._parent.version >= 4
        
  point2:
    seq:
      - id: x
        type: u1
      - id: y
        type: u1
  surface:
    seq:
      - id: type
        type: b1
      - id: texture_scale_shift
        type: b4
      - id: apply_ambient
        type: b1
      - id: visible_to_outside
        type: b1
      - id: plane_front
        type: b1
      - id: material
        type: u1
      - id: texture_size
        type: point2
      - id: texture_offset
        type: point2
      - id: plane_index
        type: u2
      - id: vertex_index
        type: u4
      - id: point_index
        type: u4
      - id: vertex_count
        type: u1
      - id: point_count
        type: u1
      - id: dummy
        type: u2
        
  bspnode:
    seq:
      - id: plane_index
        type: u2
      - id: front
        type: s2
      - id: back
        type: s2
      - id: fill
        type: s2
        
  bspsolidleaf:
    seq:
      - id: dummy
        type: u2
      - id: surface_index
        type: u2
      - id: dummy2
        type: u2
      - id: plane_index
        type: u2
      - id: surface_count
        type: u2
      - id: plane_count
        type: u2
        
  bspemptyleaf:
    seq:
      - id: flags
        type: b1
      - id: pvs_count
        type: b15
      - id: surface_count
        type: u2
      - id: pvs_index
        type: u4
      - id: surface_index
        type: u4
      - id: plane_index
        type: u4
      - id: box
        type: box3f
      - id: plane_count
        type: u2
      - id: dummy
        type: u2

  vertex:
    seq:
      - id: point_index
        type: u2
      - id: texture_index
        type: u2

  tplanef:
    seq:
      - id: point
        type: point3f
      #- id: distance_precision
      #  type: f4
      #- id: normal_precision
      #  type: f4
      - id: d
        type: f4
      #- id: dummy
      #  type: u2

  section:
    seq:
      - id: fourcc
        type: u4le
        enum: obj_enums
      - id: data
        type:
          switch-on: fourcc
          cases:
            'obj_enums::pers': pers_data
            _: dummy

    enums:
      obj_enums:
        0x53524550: pers

  pers_data:
    seq:
      - id: size
        type: u4
      - id: classname_len
        type: u2
      - id: classname
        type: str
        encoding: ASCII
        size: (classname_len + 1) & (~1)
      - id: version
        type: u4
      - id: obj_data
        type:
          switch-on: classname
          cases:
            '"TS::Shape\0"': ts_shape
            '"TS::CelAnimMesh\0"': ts_animmesh
            '"TS::MaterialList"': ts_mat_list
            '"ITRGeometry\0"' : itr_geometry

  itr_geometry:
    seq:
      - id: build_id
        type: s4
      - id: texture_scale
        type: f4
      - id: box
        type: box3f
      - id: surface_list_size
        type: s4
      - id: node_list_size
        type: s4
      - id: solid_leaf_list_size
        type: s4
      - id: empty_leaf_list_size
        type: s4
      - id: bit_list_size
        type: s4
      - id: vertex_list_size
        type: s4
      - id: point3_list_size
        type: s4
      - id: point2_list_size
        type: s4
      - id: plane_list_size
        type: s4
      - id: surface_list
        type: surface
        repeat: expr
        repeat-expr: surface_list_size
      - id: node_list
        type: bspnode
        repeat: expr
        repeat-expr: node_list_size
      - id: solid_leaf_list
        type: bspsolidleaf
        repeat: expr
        repeat-expr: solid_leaf_list_size
      - id: empty_leaf_list
        type: bspemptyleaf
        repeat: expr
        repeat-expr: empty_leaf_list_size
      - id: bitlist
        type: u1
        repeat: expr
        repeat-expr: bit_list_size
      - id: vertex_list
        type: vertex
        repeat: expr
        repeat-expr: vertex_list_size
      - id: point3_list
        type: point3f
        repeat: expr
        repeat-expr: point3_list_size
      - id: point2_list
        type: point2f
        repeat: expr
        repeat-expr: point2_list_size
      - id: plane_list
        type: tplanef
        repeat: expr
        repeat-expr: plane_list_size
      - id: highest_mip_level
        type: s4
      - id: flags
        type: u4
        
        
  ts_shape:
    seq:
      - id: num_nodes
        type: u4
      - id: num_seq
        type: u4
      - id: num_subseq
        type: u4
      - id: num_keyframes
        type: u4
      - id: num_transforms
        type: u4
      - id: num_names
        type: u4
      - id: num_objects
        type: u4
      - id: num_details
        type: u4
      - id: num_meshes
        type: u4
      - id: num_transitions
        type: u4
      - id: num_frametriggers
        type: u4
      - id: radius
        type: f4
      - id: center
        type: point3f
      - id: bounds
        type: box3f
        if: _parent.version >= 8

      - id: nodes_v7
        type: nodev7
        repeat: expr
        repeat-expr: num_nodes
        if: _parent.version == 7

      - id: nodes
        type: node
        repeat: expr
        repeat-expr: num_nodes
        if: _parent.version == 8

      - id: sequences
        type: vector_sequence
        repeat: expr
        repeat-expr: num_seq
        
      - id: subsequences
        type: subsequence
        repeat: expr
        repeat-expr: num_subseq
        if: _parent.version == 8
        
      - id: subsequences_v7
        type: subsequencev7
        repeat: expr
        repeat-expr: num_subseq
        if: _parent.version <= 7
        
      - id: keyframes
        type: keyframe
        repeat: expr
        repeat-expr: num_keyframes
        if: _parent.version == 8

      - id: keyframes_v7
        type: keyframev7
        repeat: expr
        repeat-expr: num_keyframes
        if: _parent.version <= 7

      - id: transforms
        type: transform
        repeat: expr
        repeat-expr: num_transforms
        if: _parent.version == 8

      - id: transforms_v7
        type: transformv7
        repeat: expr
        repeat-expr: num_transforms
        if: _parent.version == 7

      - id: names
        type: str
        size: 24
        encoding: ASCII
        repeat: expr
        repeat-expr: num_names

      - id: objects
        type: objectv8
        repeat: expr
        repeat-expr: num_objects
        if: _parent.version == 8

      - id: objects_v7
        type: objectv7
        repeat: expr
        repeat-expr: num_objects
        if: _parent.version <= 7

      - id: details
        type: detail
        repeat: expr
        repeat-expr: num_details

      - id: transitions
        type: transition
        repeat: expr
        repeat-expr: num_transitions
        if: _parent.version == 8
        
      - id: transitions_v7
        type: transitionv7
        repeat: expr
        repeat-expr: num_transitions
        if: _parent.version == 7

      - id: frame_triggers
        type: frame_trigger
        repeat: expr
        repeat-expr: num_frametriggers

      - id: default_material
        type: u4
        if: _parent.version >= 5
      - id: always_animate
        type: s4
        if: _parent.version >= 6

  ts_animmesh:
    seq:
      - id: num_vertices
        type: u4
      - id: num_vertices_per_frame
        type: u4
      - id: num_texture_vertices
        type: u4
      - id: num_faces
        type: u4
      - id: num_frames
        type: u4
      - id: num_texture_vertices_per_frame
        type: u4
        if: _parent.version >= 2
      - id: scale_v2
        type: point3f
        if: _parent.version < 3
      - id: origin_v2
        type: point3f
        if: _parent.version < 3
      - id: radius
        type: f4
      - id: vertices
        type: packed_vertex
        repeat: expr
        repeat-expr: num_vertices
      - id: texture_vertices
        type: point2f
        repeat: expr
        repeat-expr: num_texture_vertices
      - id: faces
        type: face
        repeat: expr
        repeat-expr: num_faces
      - id: frames_v2
        type: framev2
        repeat: expr
        repeat-expr: num_frames
        if: _parent.version < 3
      - id: frames
        type: frame
        repeat: expr
        repeat-expr: num_frames
        if: _parent.version >= 3

  ts_mat_list:
    seq:
      - id: num_details
        type: u4
      - id: num_materials
        type: u4
      - id: params
        type: material_params
        repeat: expr
        repeat-expr: num_materials

