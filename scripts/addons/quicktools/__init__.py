bl_info = {
    "name": "Quick Tools",
    "description": "A series of tools and menus to enhance and speed up workflow",
    "author": "Jonathan Williamson",
    "version": (0, 7),
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
    print("Reloaded multifiles")
	
else:
    from . import quick_operators, quick_object_mode, quick_edit_mode, quick_sculpt_mode
    
    print("Imported multifiles")

import quick_operators
import quick_object_mode
import quick_edit_mode
import quick_sculpt_mode

import bpy



def register():
   quick_operators.register()
   quick_object_mode.register()
   quick_edit_mode.register()
   quick_sculpt_mode.register()
   
   bpy.utils.register_module(__name__)
   
   
   
 
def unregister():
    quick_operators.unregister()
    quick_object_mode.unregister()
    quick_edit_mode.unregister()
    quick_sculpt_mode.unregister()
    
    bpy.utils.unregister_module(__name__)
    
if __name__ == "__main__":
    register()