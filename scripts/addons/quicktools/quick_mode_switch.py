import bpy 
from bpy import context


# Create the operator that sets the mode
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
    
    @classmethod
    def poll(cls, context):
        if len(context.selected_objects) > 0:
            return True
        return False

    def draw(self, context):
        layout = self.layout  

        mode = bpy.context.object.mode
        
        # check the current mode and only display the relavent modes, e.g. don't show current mode              
        if mode == 'EDIT' or mode == 'SCULPT' or mode == 'TEXTURE_PAINT' or mode == 'VERTEX_PAINT' or mode == 'WEIGHT_PAINT':
            objectMode = layout.operator("object.working_mode", "Object Mode", icon="OBJECT_DATAMODE")
            objectMode.setMode = 'OBJECT'  
        
        if mode == 'OBJECT' or mode == 'SCULPT' or mode == 'TEXTURE_PAINT' or mode == 'VERTEX_PAINT' or mode == 'WEIGHT_PAINT':
            editMode = layout.operator("object.working_mode", "Edit Mode", icon="EDITMODE_HLT")
            editMode.setMode = 'EDIT'
        
        if mode == 'EDIT' or mode == 'OBJECT' or mode == 'TEXTURE_PAINT' or mode == 'VERTEX_PAINT' or mode == 'WEIGHT_PAINT':
            sculptMode = layout.operator("object.working_mode", "Sculpt Mode", icon="SCULPTMODE_HLT"    )
            sculptMode.setMode = 'SCULPT'
        
        if mode == 'EDIT' or mode == 'OBJECT' or mode == 'SCULPT' or mode == 'TEXTURE_PAINT' or mode == 'WEIGHT_PAINT':
            sculptMode = layout.operator("object.working_mode", "Vertex Paint", icon="VPAINT_HLT"    )
            sculptMode.setMode = 'VERTEX_PAINT'

        if mode == 'EDIT' or mode == 'OBJECT' or mode == 'SCULPT' or mode == 'TEXTURE_PAINT' or mode == 'VERTEX_PAINT':
            sculptMode = layout.operator("object.working_mode", "Weight Paint", icon="WPAINT_HLT"    )
            sculptMode.setMode = 'WEIGHT_PAINT'

        if mode == 'EDIT' or mode == 'OBJECT' or mode == 'SCULPT' or mode == 'VERTEX_PAINT' or mode == 'WEIGHT_PAINT':
            sculptMode = layout.operator("object.working_mode", "Texture Paint", icon="TPAINT_HLT"    )
            sculptMode.setMode = 'TEXTURE_PAINT'


def register():
    bpy.utils.register_class(ModeSwitch)
    bpy.utils.register_class(SetMode)

    
def unregister():
    bpy.utils.unregister_class(ModeSwitch)
    bpy.utils.unregister_class(SetMode)

    
if __name__ == "__main__":
    register()