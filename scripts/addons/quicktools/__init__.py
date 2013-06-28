bl_info = {
    "name": "Quick Tools",
    "description": "A series of tools and menus to enhance and speed up workflow",
    "author": "Jonathan Williamson",
    "version": (0, 8),
    "blender": (2, 6, 7),
    "location": "View3D - 'Q' key gives a menu in Object, Edit, and Sculpt modes.",
    "warning": '',  # used for warning icon and text in addons panel
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/3D_interaction/quicktools",
    "tracker_url": "https://github.com/CGCookie/script-bakery/issues",
    "category": "3D View"}

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'quicktools'))
    
    
if "bpy" in locals():
    import imp
    imp.reload(quick_operators)
    imp.reload(quick_object_mode)
    imp.reload(quick_edit_mode)
    imp.reload(quick_sculpt_mode)
    imp.reload(quick_mode_switch)
    imp.reload(quick_scene)
    print("Reloaded multifiles")
	
else:
    from . import quick_operators, quick_object_mode, quick_edit_mode, quick_sculpt_mode, quick_mode_switch, quick_scene
    
    print("Imported multifiles")

import quick_operators
import quick_object_mode
import quick_edit_mode
import quick_sculpt_mode
import quick_mode_switch
import quick_scene

import bpy
from bpy.props import StringProperty
from bpy.types import AddonPreferences

class QuickToolsPreferences(AddonPreferences):
    bl_idname = __package__

    scene_settings_key = StringProperty(
        name="Scene Settings Key",
        description="Set hotkey for Scene Settings menu",
        default="`"
        )
    scene_settings_modifier_key = StringProperty(
        name="Scene Settings Key",
        description="Set modifier hotkey for Scene Settings menu",
        default="SHIFT"
        )

    object_settings_key = StringProperty(
        name="Object Settings Key",
        description="Set hotkey for Object Settings menu",
        default="`"
        )
    object_settings_modifier_key = StringProperty(
        name="Object Settings Modifier Key",
        description="Set modifier hotkey for Object Settings menu",
        default="SHIFT"
        )

    object_mode_key = StringProperty(
        name="Object Mode Key",
        description="Set hotkey for Object Mode menu",
        default="Q"
        )
    edit_mode_key = StringProperty(
        name="Edit Mode Key",
        description="Set hotkey for Edit Mode menu",
        default="Q"
        )
    sculpt_mode_key = StringProperty(
        name="Sculpt Mode Key",
        description="Set hotkey for Sculpt Mode menu",
        default="Q"
        )


    def draw(self, context):
        layout = self.layout
        split = layout.split()
        
        col = split.column()
        col.label(text="Global")

        col.prop(self, "scene_settings_key")
        col.prop(self, "object_settings_key")
        col.prop(self, "scene_settings_modifier_key")
        col.prop(self, "object_settings_modifier_key")
        
        col = split.column(align=True)
        col.label(text="Object Mode")
        col.prop(self, "object_mode_key")
        
        col.label(text="Edit Mode")
        col.prop(self, "edit_mode_key")

        col.label(text="Sculpt Mode")
        col.prop(self, "sculpt_mode_key")

def register():
   bpy.utils.register_class(QuickToolsPreferences)

   quick_operators.register()
   quick_object_mode.register()
   quick_edit_mode.register()
   quick_sculpt_mode.register()
   quick_mode_switch.register()
   quick_scene.register()
   
   
  # bpy.utils.register_module(__name__)
  
 
def unregister():
    bpy.utils.unregister_class(QuickToolsPreferences)

    quick_operators.unregister()
    quick_object_mode.unregister()
    quick_edit_mode.unregister()
    quick_sculpt_mode.unregister()
    quick_mode_switch.unregister()
    quick_scene.unregister()
    

    #bpy.utils.unregister_module(__name__)
    
if __name__ == "__main__":
    register()