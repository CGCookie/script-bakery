bl_info = {
    "name": "Add SubD Cube",
    "location": "View3D > Add > Mesh > Add SubD Cube",
    "description": "Adds ability to add a cube with a subdivision surface modifier already added",
    "author": "Jonathan Williamson",
    "version": (0,1),
    "blender": (2, 6, 5),
    "category": "Add Mesh",
    }

import bpy

class addSubDCube(bpy.types.Operator):
    """Add a simple box mesh"""
    bl_idname = "mesh.cube_subd_add"
    bl_label = "Add SubD Cube"
    bl_options = {'REGISTER', 'UNDO'}    
    
    def execute(self, context):
        obj = context.active_object
        
        addCube = bpy.ops.mesh.primitive_cube_add(view_align=False)
        addSubD = bpy.ops.object.modifier_add(type='SUBSURF')
        bpy.context.object.modifiers["Subsurf"].levels = 2
        
      
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(addSubDCube.bl_idname, icon='MOD_SUBSURF')
            
def register():
    bpy.utils.register_class(addSubDCube)
    bpy.types.INFO_MT_mesh_add.append(menu_func)
    
def unregister():
    bpy.utils.unregister_class(addSubDCube)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)
    
if __name__ == "__main__":
    register()