import bpy

class BrushSettings(bpy.types.Operator):
    """Toggle Setting For Active Brush"""
    bl_idname = "sculpt.brush_setting"
    bl_label = "Toggle Brush Setting"

    setting = bpy.props.StringProperty()

    def execute(self, context):

        setting = self.setting
        brush = context.tool_settings.sculpt.brush
       
        if setting == 'use_accumulate':
            value = brush.use_accumulate
            print(value)
            brush.use_accumulate = not value
        return {"FINISHED"}


class BrushSettingsMenu(bpy.types.Menu):
    bl_label = "Brush Settings"
    bl_idname = "sculpt.brush_settings_menu"

    def draw(self, context):
        layout = self.layout

        accumulate = layout.operator("sculpt.brush_setting", "Accumulate")
        accumulate.setting = 'use_accumulate'

def register():
    bpy.utils.register_class(BrushSettings)
    bpy.utils.register_class(BrushSettingsMenu)
    
def unregister():
    bpy.utils.unregister_class(BrushSettings)
    bpy.utils.unregister_class(BrushSettingsMenu)
   

if __name__ == "__main__":
    register()
    
    bpy.ops.wm.call_menu(name=BrushSettingsMenu.bl_idname)