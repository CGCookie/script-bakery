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
from bpy.types import AddonPreferences

# import rna_keymap_ui

# class QuickToolsPreferences(AddonPreferences):
#     bl_idname = __package__

#     def draw(self, context):
#         layout = self.layout
#         split = layout.split()
        
#         col = split.column()
#         col.label(text="Keymaps")

#         col = layout.column()
#         kc = bpy.context.window_manager.keyconfigs.addon
#         for km, kmi in addon_keymaps:
#             #km = km.active()
#             col.context_pointer_set("keymap", km)
#             rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)

addon_keymaps = []        

def register():
   # bpy.utils.register_class(QuickToolsPreferences)

   quick_operators.register()
   quick_object_mode.register()
   quick_edit_mode.register()
   quick_sculpt_mode.register()
   quick_mode_switch.register()
   quick_scene.register()

   kc = bpy.context.window_manager.keyconfigs.addon
   
   # create the mode switch menu hotkey
   km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
   kmi = km.keymap_items.new('wm.call_menu', 'Q', 'PRESS', alt=True)
   kmi.properties.name = 'mode.switch_menu' 
   kmi.active = True
   addon_keymaps.append((km, kmi))

   # create the secene options menu hotkey
   km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
   kmi = km.keymap_items.new('wm.call_menu', 'ACCENT_GRAVE', 'PRESS', shift=True)
   kmi.properties.name = 'scene.quick_options' 
   kmi.active = True
   addon_keymaps.append((km, kmi))

   # create the object mode tools menu hotkey
   km = kc.keymaps.new(name='Object Mode')
   kmi = km.keymap_items.new('wm.call_menu', 'Q', 'PRESS')
   kmi.properties.name = 'object.tools_menu' 
   kmi.active = True
   addon_keymaps.append((km, kmi))

   # create the object mode Display menu hotkey
   km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
   kmi = km.keymap_items.new('wm.call_menu', 'Q', 'PRESS', shift=True)
   kmi.properties.name = 'object.display_options'
   kmi.active = True
   addon_keymaps.append((km, kmi))

   kmi = km.keymap_items.new('wm.call_menu', 'W', 'PRESS', alt=True)
   kmi.properties.name = 'object.quick_pet_menu'
   kmi.active = True
   addon_keymaps.append((km, kmi))

   # create the edit mode tools menu hotkey
   km = kc.keymaps.new(name='Mesh')
   kmi = km.keymap_items.new('wm.call_menu', 'Q', 'PRESS')
   kmi.properties.name = 'mesh.tools_menu'
   kmi.active = True
   addon_keymaps.append((km, kmi))

   # create the sculpt mode tools menu hotkey
   km = kc.keymaps.new(name='Sculpt')
   kmi = km.keymap_items.new('wm.call_menu', 'Q', 'PRESS')
   kmi.properties.name = 'sculpt.tools_menu'
   kmi.active = True

   kmi = km.keymap_items.new('wm.call_menu', 'W', 'PRESS')
   kmi.properties.name = 'sculpt.brush_settings_menu'
   kmi.active = True

   kmi = km.keymap_items.new('sculpt.symmetry', 'X', 'PRESS', shift=True)
   kmi.properties.axis = -1
   kmi = km.keymap_items.new('sculpt.symmetry', 'Y', 'PRESS', shift=True)
   kmi.properties.axis = 0
   kmi = km.keymap_items.new('sculpt.symmetry', 'Z', 'PRESS', shift=True)
   kmi.properties.axis = 1
  
   addon_keymaps.append((km, kmi))
 
def unregister():
    # bpy.utils.unregister_class(QuickToolsPreferences)

    quick_operators.unregister()
    quick_object_mode.unregister()
    quick_edit_mode.unregister()
    quick_sculpt_mode.unregister()
    quick_mode_switch.unregister()
    quick_scene.unregister()
    
    # remove the add-on keymaps
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    
if __name__ == "__main__":
    register()