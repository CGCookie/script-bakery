import bpy

### ------------ New Menus ------------ ###        
        
# creates a menu for Sculpt mode tools
class QuickSculptTools(bpy.types.Menu):
    
    bl_label = "Quick Sculpt Tools"
    bl_idname = "sculpt.tools_menu"

    def draw(self, context):
        layout = self.layout
        
        layout.operator("sculpt.dynamic_topology_toggle", 'Dynamic Topology',)
        layout.operator("sculpt.collapse_short_edges", 'Collapse Short Edges',)
        
        layout.separator()
        
        layout.operator("object.modifier_add", 'Add Subsurf', icon='MOD_SUBSURF').type='SUBSURF'
        layout.operator("object.apply_subsurf", 'Apply Subsurf')
        
        layout.separator()
        
        layout.operator("object.smooth_remesh", 'Remesh Modifier', icon='MOD_REMESH')
        layout.operator("object.apply_remesh", 'Apply Remesh')
        
        layout.separator()
        
        layout.operator("object.apply_modifiers", 'Apply All Modifiers')
        
        layout.separator()
        
        layout.operator("sculpt.symmetry_x", icon='MOD_MIRROR')
        layout.operator("sculpt.symmetry_y")
        layout.operator("sculpt.symmetry_z")     

        layout.separator()
        
        layout.operator("sculpt.axislock_x", icon='MANIPUL')
        layout.operator("sculpt.axislock_y")
        layout.operator("sculpt.axislock_z")

        layout.separator()
        
<<<<<<< HEAD
=======

        layout.menu(SculptDisplayOptions.bl_idname)
>>>>>>> ff6c9251c1a2023f5ad50e0c086d1e48dba87453

        



### ------------ New Hotkeys and registration ------------ ###   

addon_keymaps = []

def register():
    bpy.utils.register_class(QuickSculptTools)
    
    wm = bpy.context.window_manager   
    # create the Sculpt hotkeys
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Sculpt']
    km.keymap_items.new('sculpt.symmetry_x', 'X', 'PRESS', shift=True)
    km.keymap_items.new('sculpt.symmetry_y', 'Y', 'PRESS', shift=True)
    km.keymap_items.new('sculpt.symmetry_z', 'Z', 'PRESS', shift=True)
    
    # create sculpt menu hotkey
    kmi = km.keymap_items.new('wm.call_menu', 'Q', 'PRESS')
    kmi.properties.name = 'sculpt.tools_menu' 
    addon_keymaps.append(km)

    
def unregister():

    #unregister the new operators 
    bpy.utils.unregister_class(QuickSculptTools)
    
    # remove keymaps when add-on is deactivated
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    del addon_keymaps[:]
    

if __name__ == "__main__":
    register()
    