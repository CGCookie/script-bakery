bl_info = {
    "name": "Jay's Tools",
    "description": "A series of tools and menus to enhance and speed up workflow",
    "author": "Jonathan Williamson",
    "version": (0, 5),
    "blender": (2, 6, 6),
    "location": "View3D - 'Q' key gives a menu in Object, Edit, and Sculpt modes.",
    "warning": '',  # used for warning icon and text in addons panel
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/3D_interaction/jaytools",
    "tracker_url": "http://projects.blender.org/tracker/index.php?func=detail&aid=34482&group_id=153&atid=467",
    "category": "3D View"}

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'jaytools'))
    
    
if "bpy" in locals():
    import imp
    imp.reload(jay_operators)
    imp.reload(jay_object_mode)
    imp.reload(jay_sculpt_mode)
    imp.reload(jay_edit_mode)
    print("Reloaded multifiles")
	
else:
    from . import jay_operators, jay_object_mode, jay_sculpt_mode, jay_edit_mode
    
    print("Imported multifiles")

import jay_operators
import jay_sculpt_mode
import jay_object_mode
import jay_edit_mode

import bpy



def register():
   jay_operators.register()
   jay_object_mode.register()
   jay_edit_mode.register()
   jay_sculpt_mode.register()
   
   bpy.utils.register_module(__name__)
   
   
   
 
def unregister():
    bpy.utils.unregister_module(__name__)
    
if __name__ == "__main__":
    register()