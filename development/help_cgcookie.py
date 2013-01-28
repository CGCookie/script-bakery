bl_info = {
    "name": "Add Blender Cookie to the Help menu",
    "location": "Help > Blender Cookie",
    "description": "Adds a link to Blender Cookie Tutorials in the Help menu",
    "author": "Jonathan Williamson",
    "version": (0,1),
    "blender": (2, 6, 6),
    "category": "Help",
    }

import bpy

def menu_func(self, context):
    self.layout.operator("wm.url_open", text="Blender Cookie", icon='HELP').url = "http://cgcookie.com/blender"
            
def register():
    bpy.types.INFO_MT_help.append(menu_func)
    
def unregister():
    bpy.types.INFO_MT_help.remove(menu_func)
    
if __name__ == "__main__":
    register()