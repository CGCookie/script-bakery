bl_info = {
    "name": "Sculpt Symmetry Hotkeys",
    "description": "Provides hotkeys for toggling x,y,z axis symmetry",
    "author": "Jonathan Williamson",
    "version": (0,1),
    "blender": (2, 6, 5),
    "category": "3D View",
}
  
import bpy

### Creating operators for toggling Sculpt Symmetry ###

class sculptSymmetryX(bpy.types.Operator):
    bl_label = "Toggle X-axis Symmetry"
    bl_idname = "sculpt.symmetry_x"
    
    def execute(self, context):
       
       # checks the current state of x-axis symmetry then toggles it. 
        symmetry_x = bpy.context.tool_settings.sculpt.use_symmetry_x
        if symmetry_x:
            context.tool_settings.sculpt.use_symmetry_x = False
        else:
            context.tool_settings.sculpt.use_symmetry_x = True
        
        return {"FINISHED"}

class sculptSymmetryY(bpy.types.Operator):
    bl_label = "Toggle Y-axis Symmetry"
    bl_idname = "sculpt.symmetry_y"
    
    def execute(self, context):
        
        symmetry_y = bpy.context.tool_settings.sculpt.use_symmetry_y
        if symmetry_y:
            context.tool_settings.sculpt.use_symmetry_y = False
        else:
            context.tool_settings.sculpt.use_symmetry_y = True
        
        return {"FINISHED"}   
    
class sculptSymmetryZ(bpy.types.Operator):
    bl_label = "Toggle Z-axis Symmetry"
    bl_idname = "sculpt.symmetry_z"
    
    def execute(self, context):
        
        symmetry_z = bpy.context.tool_settings.sculpt.use_symmetry_z
        if symmetry_z:
            context.tool_settings.sculpt.use_symmetry_z = False
        else:
            context.tool_settings.sculpt.use_symmetry_z = True
        
        return {"FINISHED"}       

### Appends symmetry options to the Quick Tools Addon sculpt menu ###
class JWSculptTools(bpy.types.Menu):
    bl_label = "Jonathan's Sculpt Tools"
    bl_idname = "sculpt.tools_menu"

    def draw(self, context):
        layout = self.layout
        
        layout.operator("sculpt.symmetry_x", icon='MOD_MIRROR')
        layout.operator("sculpt.symmetry_y")
        layout.operator("sculpt.symmetry_z")

### Creating the hotkeys ###

addon_keymaps = []

def register():
    bpy.utils.register_class(sculptSymmetryX)
    bpy.utils.register_class(sculptSymmetryY)
    bpy.utils.register_class(sculptSymmetryZ)
    
        
    # create the Sculpt symmetry hotkeys
    kmi = km.keymap_items.new('sculpt.symmetry_x', 'X', 'PRESS', shift=True)
    kmi = km.keymap_items.new('sculpt.symmetry_y', 'Y', 'PRESS', shift=True)
    kmi = km.keymap_items.new('sculpt.symmetry_z', 'Z', 'PRESS', shift=True)

    addon_keymaps.append(km)
    
def unregister():

    #unregister the new operators 
    bpy.utils.register_class(sculptSymmetryX)
    bpy.utils.register_class(sculptSymmetryY)
    bpy.utils.register_class(sculptSymmetryZ)
    
    # remove keymaps when add-on is deactivated
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    del addon_keymaps[:]
    
if __name__ == "__main__":
    register()
    