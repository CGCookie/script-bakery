bl_info = {
    "name": "Add Skin Object",
    "location": "View3D > Add > Mesh > Add Skin Object",
    "description": "Adds a single edge object with a Skin modifier",
    "author": "Jonathan Williamson",
    "version": (0,1),
    "blender": (2, 6, 6),
    "category": "Add Mesh",
    }

import bpy

class addSkin(bpy.types.Operator):
    """Add a Skin Object"""
    bl_idname = "object.skin_add"
    bl_label = "Add Skin Object"
    bl_options = {'REGISTER', 'UNDO'}    
    
    def execute(self, context):
    
        scene = bpy.context.scene
        
        verts = [(0, 0, 0), (0, 0, 2)]
        edges = [(0, 1)]
        
        # create the skin mesh data and object
        skin_mesh = bpy.data.meshes.new("skin")
        skin_object = bpy.data.objects.new("Skin Object", skin_mesh)
        
        # place the skin object at the 3D Cursor
        skin_object.location = bpy.context.scene.cursor_location
        bpy.context.scene.objects.link(skin_object)
        
        skin_mesh.from_pydata(verts, edges, [])
        
        skin_object.select = True
        scene.objects.active = skin_object

######## Old Hack ############
        
#        bpy.ops.transform.resize(value=(0   , 1, 1))
#        bpy.ops.object.transform_apply(scale=True)
#        
#        bpy.ops.object.editmode_toggle()
#        bpy.ops.mesh.remove_doubles(threshold=0.0001, use_unselected=True)
#        bpy.ops.object.editmode_toggle()

##############################
        
        # add a mirror modifier
        bpy.ops.object.modifier_add(type='MIRROR')
        #bpy.context.active_object.modifiers["Mirror"].use_clip = True
        
        # add a skin modifier
        bpy.ops.object.modifier_add(type='SKIN')
        
        # add a subsurf modifier
        bpy.ops.object.modifier_add(type='SUBSURF')
        
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(addSkin.bl_idname, icon='MOD_SKIN')
            
def register():
    bpy.utils.register_class(addSkin)
    bpy.types.INFO_MT_mesh_add.append(menu_func)
    
def unregister():
    bpy.utils.unregister_class(addSkin)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)
    
if __name__ == "__main__":
    register()