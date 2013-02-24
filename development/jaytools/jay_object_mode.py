import bpy
import os
from bpy import context


# adds an object mode menu 
class JWObjectTools(bpy.types.Menu):
    bl_label = "Jonathan's Object Tools"
    bl_idname = "object.tools_menu"
       
    def draw(self, context):
        layout = self.layout
        
        
        layout.operator("object.add_subsurf", 'Add Subsurf', icon='MOD_SUBSURF')
        layout.operator("object.apply_subsurf", 'Apply Subsurf')
        
        layout.operator("object.add_mirror", 'Add Mirror', icon='MOD_MIRROR')
        
        layout.separator()
                
        layout.operator_menu_enum("object.modifier_add", "type",
                                      icon='MODIFIER') 
        layout.operator("object.apply_modifiers")
        
        layout.separator() 
                
        layout.operator_menu_enum("object.origin_set", "type")
        
        layout.separator()
        
        layout.operator("object.shade_smooth", icon='SOLID')
        layout.operator("object.shade_flat", icon='MESH_UVSPHERE')
   



### ------------ New hotkeys and registration ------------ ###

addon_keymaps = []

def register():
    #register the new menus
    bpy.utils.register_class(JWObjectTools)
     
    
    wm = bpy.context.window_manager
    
    
    # create the object mode menu hotkey
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    kmi = km.keymap_items.new('wm.call_menu', 'Q', 'PRESS')
    kmi.properties.name = 'object.tools_menu' 


    addon_keymaps.append(km)

def unregister():
    #unregister the new menus
    bpy.utils.unregister_class(JWObjectTools)
        
    
    # remove keymaps when add-on is deactivated
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    del addon_keymaps[:]


if __name__ == "__main__":
    register()
    
    
       