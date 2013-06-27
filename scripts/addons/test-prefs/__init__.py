bl_info = {
    "name": "Preferences Test",
    "description": "A series of tools and menus to enhance and speed up workflow",
    "author": "Jonathan Williamson",
    "version": (0, 8),
    "blender": (2, 6, 8),
    "location": "",
    "warning": '',  # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "3D View"}

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'test-prefs'))

if "bpy" in locals():
    import imp
    imp.reload(pref_test)

    print("Reloaded multifiles")
	
else:
    from . import pref_test
    print("Imported multifiles")

import pref_test

import bpy
from bpy.props import StringProperty
from bpy.types import AddonPreferences
from bpy import context


class TestPreferences(AddonPreferences):
    bl_idname = __package__

    test_print_key = StringProperty(
        name="Print Test",
        description="Print a test to the console",
        default="Y"
        )

    def draw(self, context):
        layout = self.layout
        split = layout.split()
        
        col = split.column()
        col.label(text="Global")

        col.prop(self, "test_print_key")

user_prefs = context.user_preferences
addon_prefs = user_prefs.addons[__package__].preferences

addon_keymaps = []

def register():
    bpy.utils.register_module(__name__)  
    pref_test.register()

    wm = bpy.context.window_manager    
    
    # create the object mode Quick Tools menu hotkey
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode')
    kmi = km.keymap_items.new('view3d.print_test', 'Y', 'PRESS')
    #kmi.properties.name = 'object.tools_menu' 

    addon_keymaps.append(km)


def unregister():
    bpy.utils.unregister_module(__name__)
    pref_test.unregister()
        
    # remove keymaps when add-on is deactivated
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    del addon_keymaps[:]


if __name__ == "__main__":
    register() 