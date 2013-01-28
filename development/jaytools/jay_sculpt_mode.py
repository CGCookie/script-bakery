import bpy

### ------------ New Menus ------------ ###        
        
# creates a menu for Sculpt mode tools
class SculptTools(bpy.types.Menu):
    
    bl_label = "Sculpt Tools"
    bl_idname = "sculpt.tools_menu"

    def draw(self, context):
        layout = self.layout
        
        layout.operator("object.modifier_add", 'Add Subsurf', icon='MOD_SUBSURF').type='SUBSURF'
        layout.operator("object.apply_subsurf", 'Apply Subsurf')
        
        layout.separator()
        
        layout.operator("object.modifier_add", 'Remesh Modifier', icon='MOD_REMESH').type='REMESH'
        layout.operator("object.apply_remesh", 'Apply Remesh')
        
        layout.separator()
        
        layout.operator("sculpt.symmetry_x", icon='MOD_MIRROR')
        layout.operator("sculpt.symmetry_y")
        layout.operator("sculpt.symmetry_z")     



### ------------ New Hotkeys and registration ------------ ###   

addon_keymaps = []

def register():
    print('1')
    bpy.utils.register_class(SculptTools)
    
    wm = bpy.context.window_manager
    print('2')    
    # create the Sculpt hotkeys
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Sculpt']
    km.keymap_items.new('sculpt.symmetry_x', 'X', 'PRESS', shift=True)
    print('3')
    #km = wm.keyconfigs.addon.keymaps.new(name='Sculpt', space_type='EMPTY')
    #kmi = km.keymap_items.new('sculpt.symmetry_x', 'X', 'PRESS', shift=True)
    #kmi = km.keymap_items.new('sculpt.symmetry_y', 'Y', 'PRESS', shift=True)
    #kmi = km.keymap_items.new('sculpt.symmetry_z', 'Z', 'PRESS', shift=True)
    
    # create sculpt menu hotkey
    kmi = km.keymap_items.new('wm.call_menu', 'T', 'PRESS', oskey=True)
    kmi.properties.name = 'sculpt.tools_menu' 
    print('4')
    addon_keymaps.append(km)
    print('5')

    
def unregister():

    #unregister the new operators 
    bpy.utils.unregister_class(SculptTools)
    
    # remove keymaps when add-on is deactivated
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    del addon_keymaps[:]
    

if __name__ == "__main__":
    register()
    