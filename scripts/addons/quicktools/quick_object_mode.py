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
        
        layout.menu(SmartModifiers.bl_idname, "Add Smart Modifier", icon='MODIFIER')

        layout.operator_menu_enum("object.modifier_add", "type") 
        layout.operator("object.apply_modifiers")
        
        layout.separator() 
                
        layout.operator_menu_enum("object.origin_set", "type")

        layout.separator()

        layout.operator("object.mesh_halve", "Halve and Mirror")


class SmartModifiers(bpy.types.Menu):
    bl_idname = "object.smart_mod"
    bl_label = "Smart Modifiers"

    def draw (self, context):
        layout = self.layout
        layout.operator("object.add_mirror", "Mirror", icon='MOD_MIRROR')
        layout.operator("object.add_lattice", "Lattice", icon='MOD_LATTICE')

class QuickObjectOptions(bpy.types.Menu):
    bl_idname = "object.display_options"
    bl_label = "Quick Object Options"

    def draw(self, context):

        mode = bpy.context.object.mode

        layout = self.layout
        layout.operator("object.double_sided")
        layout.operator("object.all_edges_wire")

        layout.separator()

        # add "Outline Selected" here.

        if mode == 'OBJECT' or mode == 'SCULPT':
            layout.operator("object.shade_smooth", icon='SOLID')
            layout.operator("object.shade_flat", icon='MESH_UVSPHERE')
        elif mode == 'EDIT':
            layout.operator("mesh.faces_shade_smooth", icon='SOLID')
            layout.operator("mesh.faces_shade_flat", icon='MESH_UVSPHERE')
        
        

        
   
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
    bpy.utils.register_class(SmartModifiers)
    bpy.utils.register_class(QuickObjectOptions)
    bpy.utils.register_class(QuickObjectToolbar)
     
    
    wm = bpy.context.window_manager
    
    
    # create the object mode Quick Tools menu hotkey
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    kmi = km.keymap_items.new('wm.call_menu', 'Q', 'PRESS')
    kmi.properties.name = 'object.tools_menu' 

    # create the object mode Display and Scene Tools menu hotkey
    km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('wm.call_menu', 'Q', 'PRESS', shift=True)
    kmi.properties.name = 'object.display_options' 


    addon_keymaps.append(km)

def unregister():
    #unregister the new menus
    bpy.utils.unregister_class(QuickObjectTools)
    bpy.utils.unregister_class(SmartModifiers)
    bpy.utils.unregister_class(QuickObjectOptions)
    bpy.utils.unregister_class(QuickObjectToolbar)
        
    
    # remove keymaps when add-on is deactivated
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    del addon_keymaps[:]


if __name__ == "__main__":
    register()
    
    
       