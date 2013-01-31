import bpy
import os
from bpy import context
 
    

### ------------ Creating the Menus for each mode ------------ ###

# adds a Mode switch menu
class ModeSwitch(bpy.types.Menu):
    bl_label = "Quick Mode Switch Menu"
    bl_idname = "mode.switch_menu"
    
    def draw(self, context):
        layout = self.layout
   
        layout.operator("object.editmode_toggle", 'Edit Mode', icon='EDITMODE_HLT')
        layout.operator("object.editmode_toggle", 'Object Mode', icon='OBJECT_DATAMODE')
        layout.operator("sculpt.sculptmode_toggle", 'Sculpt Mode', icon='SCULPTMODE_HLT')

# adds an object mode menu 
class JWObjectTools(bpy.types.Menu):
    bl_label = "Jonathan's Object Tools"
    bl_idname = "object.tools_menu"
       
    def draw(self, context):
        layout = self.layout
        
        
        layout.operator("object.modifier_add", 'Add Subsurf', icon='MOD_SUBSURF').type='SUBSURF'
        layout.operator("object.apply_subsurf", 'Apply Subsurf')
        
        layout.operator("object.add_mirror", 'Add Mirror', icon='MOD_MIRROR')
        
        layout.separator()
                
        layout.operator_menu_enum("object.modifier_add", "type",
                                      icon='MODIFIER') 
        
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
    bpy.utils.register_class(ModeSwitch)
     
    
    wm = bpy.context.window_manager
    
    # create the mode switcher menu hotkey
    km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('wm.call_menu', 'TAB', 'PRESS', alt=True)
    kmi.properties.name = 'mode.switch_menu'
    
    # create the object mode menu hotkey
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    kmi = km.keymap_items.new('wm.call_menu', 'Q', 'PRESS')
    kmi.properties.name = 'object.tools_menu' 


    addon_keymaps.append(km)

def unregister():
    #unregister the new menus
    bpy.utils.unregister_class(JWObjectTools)
    bpy.utils.unregister_class(ModeSwitch)
        
    
    # remove keymaps when add-on is deactivated
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    del addon_keymaps[:]


if __name__ == "__main__":
    register()
    
    
       