import bpy

selected = [verts for verts in bpy.context.active_object.data.vertices if verts.selected]
print(len(selected))