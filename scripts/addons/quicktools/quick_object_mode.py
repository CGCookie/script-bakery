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
        
        #layout.operator("object.add_mirror", 'Add Mirror', icon='MOD_MIRROR')
        #layout.operator("object.empty_add_unactive", "Add Target")
        
        layout.separator()
        
        layout.menu(SmartModifiers.bl_idname, "Add Smart Modifier", icon='MODIFIER')

        layout.operator_menu_enum("object.modifier_add", "type") 
        layout.operator("object.apply_modifiers")
        layout.operator("object.modifier_remove_all", "Remove All Modifiers")
        
        layout.separator()

        layout.operator("object.mesh_halve", "Halve and Mirror")

        layout.separator() 
                
        layout.operator_menu_enum("object.origin_set", "type")


class SmartModifiers(bpy.types.Menu):
    bl_idname = "object.smart_mod"
    bl_label = "Smart Modifiers"

    def draw (self, context):
        layout = self.layout
        layout.operator("object.empty_add_unactive", "Add Target", icon='CURSOR')

        layout.separator()

        layout.operator("object.add_array", "Array", icon='MOD_ARRAY')
        layout.operator("object.add_boolean", "Boolean", icon='MOD_BOOLEAN')
        layout.operator("object.add_mirror", "Mirror", icon='MOD_MIRROR')
        layout.operator("object.add_lattice", "Lattice", icon='MOD_LATTICE')
        layout.operator("object.add_screw", "Screw", icon='MOD_SCREW')


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


### ------------ New hotkeys and registration ------------ ###

addon_keymaps = []

user_prefs = context.user_preferences
addon_prefs = user_prefs.addons['quicktools'].preferences

def register():
    bpy.utils.register_module(__name__)  

    wm = bpy.context.window_manager    
    
    # create the object mode Quick Tools menu hotkey
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode')
    kmi = km.keymap_items.new('wm.call_menu', 'Q', 'PRESS')
    kmi.properties.name = 'object.tools_menu' 

    # create the object mode Display and Scene Tools menu hotkey
    km = wm.keyconfigs.addon.keymaps.new(name='3D View')
    kmi = km.keymap_items.new('wm.call_menu', 'Q', 'PRESS', shift=True)
    kmi.properties.name = 'object.display_options' 

    addon_keymaps.append(km)


def unregister():
    bpy.utils.unregister_module(__name__)
        
    # remove keymaps when add-on is deactivated
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    del addon_keymaps[:]


if __name__ == "__main__":
    register()   