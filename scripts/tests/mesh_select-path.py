bl_info = {
    "name": "Addon name",
    "location": "View3D > Edit Mode",
    "description": "Add-on description goes here",
    "author": "Jonathan Williamson",
    "version": (0,0),
    "blender": (2, 6, 7),
    "category": "Mesh",
    }
    
import bpy

mesh = bpy.ops.mesh

class SelectPath(bpy.types.Operator):
    """Select a vertex path"""
    bl_idname = "mesh.select_path"
    bl_label = "Select a Path"
    bl_options = {'REGISTER', 'UNDO'}    
    
    '''##############
    
        Add support for Edge loops and face loops by detecting current selection.    
    
    ##############'''
    
    def execute(self, context):
        if bpy.context.mode == 'EDIT_MESH':
            bpy.ops.view3d.select
            mesh.select_vertex_path(type='TOPOLOGICAL')
            return {'FINISHED'}
        
                
addon_keymaps = []
    
def register():
    bpy.utils.register_class(SelectPath)

    wm = bpy.context.window_manager

    km = wm.keyconfigs.addon.keymaps.new(name='Mesh', space_type='EMPTY')
    kmi = km.keymap_items.new('mesh.select_path', 'SELECTMOUSE', 'PRESS', ctrl=True)
    
    addon_keymaps.append(km)
    


def unregister():
    bpy.utils.register_class(SelectPath)
    
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    del addon_keymaps[:]
    
if __name__ == "__main__":
    register()
    