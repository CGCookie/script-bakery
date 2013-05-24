import bpy



class mirrorMesh(bpy.types.Operator):    
    """Delete one half of a mesh and add a mirror modifier"""
    bl_idname = "object.mesh_mirror"
    bl_label = "Halve and mirror mesh"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        obj = bpy.context.active_object.data
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        
        for verts in obj.vertices:
            if verts.co.x < -0.001:    
                verts.select = True
                
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.delete(type='VERT')
        
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.modifier_add(type='MIRROR')

        return {'FINISHED'}
    
def register():
    bpy.utils.register_class(mirrorMesh)
    
def unregister():
    bpy.utils.unregister_class(mirrorMesh)
    
if __name__ == "__main__":
    register()