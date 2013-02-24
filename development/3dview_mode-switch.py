bl_info = {
    "name": "Quick Mode Switch Menu",
    "location": "View3D > ALT+TAB",
    "description": "Adds a context-senstive menu for switching modes",
    "author": "Jonathan Williamson",
    "version": (0,1),
    "blender": (2, 6, 6),
    "category": "3D View",
    }

import bpy


### ------------ Creating the Menus for each mode ------------ ###

class SetMode(bpy.types.Operator):
    bl_label = "Set Mode"
    bl_idname = "object.working_mode"
    
    setMode = bpy.props.StringProperty()

    
    def execute(self, context):
        bpy.ops.object.mode_set(mode=self.setMode)

        return {"FINISHED"}



# adds a Mode switch menu
class ModeSwitch(bpy.types.Menu):
    bl_label = "Quick Mode Switch Menu"
    bl_idname = "mode.switch_menu"
    
    #modes = ["OBJECT", "EDIT", "SCULPT"]
    currentMode = bpy.context.mode
    
    
    def draw(self, context):
        layout = self.layout                
                
        objectMode = layout.operator("object.working_mode", "Object Mode", icon="OBJECT_DATAMODE")
        objectMode.setMode = 'OBJECT'  
    
        editMode = layout.operator("object.working_mode", "Edit Mode", icon="EDITMODE_HLT")
        editMode.setMode = 'EDIT'
        
        sculptMode = layout.operator("object.working_mode", "Sculpt Mode", icon="SCULPTMODE_HLT"    )
        sculptMode.setMode = 'SCULPT'
    
        

        return {"FINISHED"}


addon_keymaps = []

def register():
    bpy.utils.register_class(ModeSwitch)
    bpy.utils.register_class(SetMode)
    
    wm = bpy.context.window_manager
    
    # create the mode switcher menu hotkey
    km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('wm.call_menu', 'TAB', 'PRESS', alt=True)
    kmi.properties.name = 'mode.switch_menu'
    
    addon_keymaps.append(km)
    
def unregister():
    bpy.utils.unregister_class(ModeSwitch)
    bpy.utils.unregister_class(SetMode)

    # remove keymaps when add-on is deactivated
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    del addon_keymaps[:]
    
if __name__ == "__main__":
    register()