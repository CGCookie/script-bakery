import bpy
import os
from bpy import context


# adds an object mode menu 
class QuickObjectTools(bpy.types.Menu):
    bl_label = "Quick Object Tools"
    bl_idname = "object.tools_menu"
       
    def draw(self, context):
        layout = self.layout
        
        
        layout.operator("object.add_subsurf", 'Add Subsurf', icon='MOD_SUBSURF')
        layout.operator("object.apply_subsurf", 'Apply Subsurf')
        
        layout.operator("object.add_mirror", 'Add Mirror', icon='MOD_MIRROR')
        layout.operator("object.empty_add_unactive", "Add Target")
        
        layout.separator()
                
        layout.operator_menu_enum("object.modifier_add", "type",
                                      icon='MODIFIER') 
        layout.operator("object.apply_modifiers")
        
        layout.separator() 
                
        layout.operator_menu_enum("object.origin_set", "type")

        layout.separator()
        
        layout.operator("object.shade_smooth", icon='SOLID')
        layout.operator("object.shade_flat", icon='MESH_UVSPHERE')
   
# Create the Tool Bar section 
class QuickObjectToolbar(bpy.types.Panel):
    bl_label = "Quick Tools"
    bl_idname = "object.quick_object_toolbar"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = 'objectmode'
    
    def draw(self, context):
        layout = self.layout
        
        col = layout.column(align=True)
        
        col.label(text="Modifiers")
        
        row = col.row()
        row.operator("object.add_subsurf", "Subsurf", icon="MOD_SUBSURF")
        row.operator("object.add_mirror", "Mirror", icon="MOD_MIRROR")
        
        row = col.row()
        row.operator("object.apply_subsurf", "Apply Subsurf")
        row.operator("object.empty_add_unactive", "Add Target")
        
        row = col.row()
        row.operator("object.apply_modifiers", "Apply Modifiers")
        
        col.operator_menu_enum("object.modifier_add", "type")
        
        col = layout.column(align=True)
        col.label(text="Origin")
        
        row = col.row()
        row.operator_menu_enum("object.origin_set", "type", "Set Origin")
        
        col = layout.column(align=True)
        col.label(text="Shading")

        row = col.row()
        row.operator("object.shade_smooth", "Smooth", icon='SOLID')
        row.operator("object.shade_flat", "Flat", icon='MESH_UVSPHERE')        
        
        
  

### ------------ New hotkeys and registration ------------ ###

addon_keymaps = []

def register():
    #register the new menus
    bpy.utils.register_class(QuickObjectTools)
    bpy.utils.register_class(QuickObjectToolbar)
     
    
    wm = bpy.context.window_manager
    
    
    # create the object mode menu hotkey
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    kmi = km.keymap_items.new('wm.call_menu', 'Q', 'PRESS')
    kmi.properties.name = 'object.tools_menu' 


    addon_keymaps.append(km)

def unregister():
    #unregister the new menus
    bpy.utils.unregister_class(QuickObjectTools)
    bpy.utils.unregister_class(QuickObjectToolbar)
        
    
    # remove keymaps when add-on is deactivated
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    del addon_keymaps[:]


if __name__ == "__main__":
    register()
    
    
       