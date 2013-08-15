import bpy

bpy.ops.object.mode_set(mode = 'EDIT')

bpy.ops.mesh.select_face_by_sides(number = 4, type = 'GREATER', extend = False)

bpy.ops.mesh.extrude_faces_move()

bpy.ops.mesh.edge_collapse()
