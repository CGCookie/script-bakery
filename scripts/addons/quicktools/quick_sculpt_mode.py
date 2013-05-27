import bpy

### ------------ New Menus ------------ ###        
        
# creates a menu for Sculpt mode tools
class QuickSculptTools(bpy.types.Menu):
    
    bl_label = "Quick Sculpt Tools"
    bl_idname = "sculpt.tools_menu"

    def draw(self, context):
        layout = self.layout
        dyntopo = bpy.context.sculpt_object.use_dynamic_topology_sculpting
        shortEdges = bpy.context.scene.tool_settings.sculpt.use_edge_collapse

        if dyntopo:
            layout.operator("sculpt.dynamic_topology_toggle", 'Disable Dynamic Topology',)
        else:
            layout.operator("sculpt.dynamic_topology_toggle", 'Enable Dynamic Topology')

        if shortEdges:
            layout.operator("sculpt.collapse_short_edges", 'Disable Collapse Short Edges',)
        else:
            layout.operator("sculpt.collapse_short_edges", 'Enable Collpase Short Edges')
        layout.separator()
        
        layout.operator("object.add_subsurf", 'Add Subsurf', icon='MOD_SUBSURF')
        layout.operator("object.apply_subsurf", 'Apply Subsurf')
        
        layout.separator()
        
        layout.operator("object.smooth_remesh", 'Remesh Modifier', icon='MOD_REMESH')
        layout.operator("object.apply_remesh", 'Apply Remesh')
        
        layout.separator()
        
        layout.operator("object.apply_modifiers", 'Apply All Modifiers')
        
        layout.separator()
        
        symmetry_x = bpy.context.tool_settings.sculpt.use_symmetry_x
        if symmetry_x:
            layout.operator("sculpt.symmetry_x", 'Disable X Symmetry', icon='MOD_MIRROR')
        else:
            layout.operator("sculpt.symmetry_x", 'Enable X Symmetry', icon='MOD_MIRROR')

        
        symmetry_y = bpy.context.tool_settings.sculpt.use_symmetry_y
        if symmetry_y:
            layout.operator("sculpt.symmetry_y", 'Disable Y Symmetry')
        else:
            layout.operator("sculpt.symmetry_y", 'Enable Y Symmetry')

        symmetry_z = bpy.context.tool_settings.sculpt.use_symmetry_z
        if symmetry_z:
            layout.operator("sculpt.symmetry_z", 'Disable Z Symmetry')
        else:
            layout.operator("sculpt.symmetry_z", 'Enable Z Symmetry')   

        layout.separator()
        
        lock_x = bpy.context.tool_settings.sculpt.lock_x
        if lock_x:
            layout.operator("sculpt.axislock_x", 'Disable X Lock', icon='MANIPUL')
        else:
            layout.operator("sculpt.axislock_x", 'Enable X Lock', icon='MANIPUL')

        lock_y = bpy.context.tool_settings.sculpt.lock_y
        if lock_y:
            layout.operator("sculpt.axislock_y", 'Disable Y Lock')
        else:
            layout.operator("sculpt.axislock_y", 'Enable Y Lock')

        lock_z = bpy.context.tool_settings.sculpt.lock_z
        if lock_z:
            layout.operator("sculpt.axislock_z", 'Disable Z Lock')
        else:
            layout.operator("sculpt.axislock_z", 'Enable Z Lock')

        layout.separator()       



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
    