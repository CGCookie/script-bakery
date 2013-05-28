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

        symmetry_x = bpy.context.tool_settings.sculpt.use_symmetry_x
        symmetry_y = bpy.context.tool_settings.sculpt.use_symmetry_y
        symmetry_z = bpy.context.tool_settings.sculpt.use_symmetry_z

        lock_x = bpy.context.tool_settings.sculpt.lock_x
        lock_y = bpy.context.tool_settings.sculpt.lock_y
        lock_z = bpy.context.tool_settings.sculpt.lock_z


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
        
        if symmetry_x:
            layout.operator("sculpt.symmetry", 'Disable X Symmetry').axis = -1
        else:
            layout.operator("sculpt.symmetry", 'Enable X Symmetry').axis = -1

        if symmetry_y:
            layout.operator("sculpt.symmetry", 'Disable Y Symmetry').axis = 0
        else:
            layout.operator("sculpt.symmetry", 'Enable Y Symmetry').axis = 0

        if symmetry_z:
            layout.operator("sculpt.symmetry", 'Disable Z Symmetry').axis = 1
        else:
            layout.operator("sculpt.symmetry", 'Enable Z Symmetry').axis = 1

        layout.separator()
        
        if lock_x:
            layout.operator("sculpt.axislock_x", 'Disable X Lock', icon='MANIPUL')
        else:
            layout.operator("sculpt.axislock_x", 'Enable X Lock', icon='MANIPUL')

        if lock_y:
            layout.operator("sculpt.axislock_y", 'Disable Y Lock')
        else:
            layout.operator("sculpt.axislock_y", 'Enable Y Lock')

        if lock_z:
            layout.operator("sculpt.axislock_z", 'Disable Z Lock')
        else:
            layout.operator("sculpt.axislock_z", 'Enable Z Lock')




### ------------ New Hotkeys and registration ------------ ###   

addon_keymaps = []

def register():
    bpy.utils.register_class(QuickSculptTools)
    
    wm = bpy.context.window_manager   
    # create the Sculpt hotkeys
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Sculpt']
    
    kmi = km.keymap_items.new('sculpt.symmetry', 'X', 'PRESS', shift=True)
    kmi.properties.axis = -1
    kmi = km.keymap_items.new('sculpt.symmetry', 'Y', 'PRESS', shift=True)
    kmi.properties.axis = 0
    kmi = km.keymap_items.new('sculpt.symmetry', 'Z', 'PRESS', shift=True)
    kmi.properties.axis = 1

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
    