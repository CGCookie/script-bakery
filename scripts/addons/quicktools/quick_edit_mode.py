import bpy
import os
from bpy import context
 

# creates a menu for edit mode tools         
class QuickMeshTools(bpy.types.Menu):
    bl_label = "Quick Mesh Tools"
    bl_idname = "mesh.tools_menu"
       
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        
        layout.operator("gpencil.surfsk_add_surface", 'Add BSurface', icon='OUTLINER_OB_SURFACE')
        layout.operator("mesh.bridge_edge_loops")
                
        layout.separator()
        
        layout.operator("mesh.bevel")
        layout.operator("mesh.inset").use_boundary=False
        layout.operator("mesh.subdivide")
        
        layout.separator()
        
        layout.operator("mesh.knife_tool", icon='SCULPTMODE_HLT')
        layout.operator("mesh.vert_connect")
        
        layout.separator()
        
        layout.operator("mesh.vertices_smooth")    
        
        layout.separator()

        layout.operator("mesh.set_object_origin", "Origin to Selection")

        layout.operator("object.mesh_halve", "Halve mesh")

        layout.separator()
        
        layout.operator("object.add_mirror", icon='MOD_MIRROR')  
        layout.operator("object.add_subsurf", 'Add Subsurf', icon='MOD_SUBSURF')

        layout.separator()
        
        layout.operator("mesh.faces_shade_smooth", icon='SOLID')
        layout.operator("mesh.faces_shade_flat", icon='MESH_UVSPHERE')



### ------------ New hotkeys and registration ------------ ###

addon_keymaps = []

def register():
    #register the new menus
    bpy.utils.register_class(QuickMeshTools)
     
    
    wm = bpy.context.window_manager
    
    # creatue the edit mode menu hotkey
    km = wm.keyconfigs.addon.keymaps.new(name='Mesh', space_type='EMPTY')
    kmi = km.keymap_items.new('wm.call_menu', 'Q', 'PRESS')
    kmi.properties.name = 'mesh.tools_menu'

    addon_keymaps.append(km)

def unregister():
    #unregister the new menus
    bpy.utils.unregister_class(QuickMeshTools)
        
    
    # remove keymaps when add-on is deactivated
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    del addon_keymaps[:]


if __name__ == "__main__":
    register()
    
    
       