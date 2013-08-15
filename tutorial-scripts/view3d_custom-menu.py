bl_info = {
        "name": "My Custom Menu",
        "category": "3D View",
        "author": "Jonathan Williamson"
        }        

import bpy

class customMenu(bpy.types.Menu):
    bl_label = "Custom Menu"
    bl_idname = "view3D.custom_menu"
    
    def draw(self, context):
        layout = self.layout
        
        layout.operator("mesh.primitive_cube_add")
        layout.operator("object.duplicate_move")
    
def register():
    bpy.utils.register_class(customMenu)
#    bpy.ops.wm.call_menu(name=customMenu.bl_idname)
    
def unregister():
    bpy.utils.unregister_class(customMenu)
    
if __name__ == "__main__":
    register()