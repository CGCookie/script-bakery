import bpy
class sculptSymmetry(bpy.types.Operator):
    """Toggle Symmetry For Sculpting"""
    bl_idname = "sculpt.symmetry"
    bl_label = "Toggle Sculpt Symmetry"

    
    axis = bpy.props.IntProperty(name = "Axis",
                    description = "switch between symmetry axis'",
                    default = -1)

    # def execute(self, context):

    #     symmetry = self.axis
    #     self.axis = not symmetry

    def execute(self, context):
        if self.axis == -1:
            symmetry_x = context.tool_settings.sculpt.use_symmetry_x
            context.tool_settings.sculpt.use_symmetry_x = not symmetry_x
        if self.axis == 0:
            symmetry_y = context.tool_settings.sculpt.use_symmetry_y
            context.tool_settings.sculpt.use_symmetry_x = not symmetry_y
        if self.axis == 1:
            symmetry_z = context.tool_settings.sculpt.use_symmetry_z
            context.tool_settings.sculpt.use_symmetry_z = not symmetry_z
        return {"FINISHED"}

def menu_func(self, context):
    self.layout.operator("sculpt.symmetry", "Test X Symmetry").axis = -1
    self.layout.operator("sculpt.symmetry", "Test Y Symmetry").axis = 0
    self.layout.operator("sculpt.symmetry", "Test Z Symmetry").axis = 1


def register():
    bpy.utils.register_module(__name__)
    bpy.types.sculpt_tools_menu.append(menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.sculpt_tools_menu.remove(menu_func)
        
if __name__ == "__main__":
    register()