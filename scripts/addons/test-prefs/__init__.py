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

from bl_ui.space_userpref_keymap import InputKeyMapPanel


class TestPreferences(AddonPreferences):
    bl_idname = __package__

    test_print_key = StringProperty(
        name="Print Test",
        description="Print a test to the console",
        default="Y"
        )

    _fake_panel = InputKeyMapPanel()
    
    def draw(self, context):
        layout = self.layout
        split = layout.split()
        
        col = split.column()
        col.label(text="Global")

        col = layout.column()
        kc = bpy.context.window_manager.keyconfigs.addon
        for km, kmi in addon_keymaps:
            km = km.active()
            col.context_pointer_set("keymap", km)
            self._fake_panel.draw_kmi([], kc, km, kmi, col, 0)


addon_prefs = context.user_preferences.addons[__package__].preferences

addon_keymaps = []

def register():

    bpy.utils.register_module(__name__)
    pref_test.register()

    kc = bpy.context.window_manager.keyconfigs.addon

    # create the object mode Quick Tools menu hotkey
    km = kc.keymaps.new(name='Object Mode')
    kmi = km.keymap_items.new('view3d.print_test', 'Y', 'PRESS')
    kmi.active = False

    addon_keymaps.append((km, kmi))

#addon_prefs['test_print_key']

def unregister():
    bpy.utils.unregister_module(__name__)
    pref_test.unregister()
        
    # remove keymaps when add-on is deactivated
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

if __name__ == "__main__":
    register() 