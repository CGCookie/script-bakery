#script by Alex Telford | CG Cookie | www.blendercookie.com
#Description:
#This script will apply all modifiers on selected objects and remove the subsurf and multiresolutions. This is great for exporting models with a lot of modifiers where you do not want the subsurf applied.
#Usage:
#Load into script editor, hit run script.

#import blender python module
import bpy
#load selected objects into a variable
sel = bpy.context.selected_objects
#make all objects their own data users, this is so we can apply modifiers
bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, texture=False, animation=False)
#loop through all objects
for obj in sel:
	#set the active object to the current object in the loop
    bpy.context.scene.objects.active = obj
	#loop through the modifiers
    for mod in obj.modifiers:
		#check if the modifier is a subsurf or multires
        if mod.type == "SUBSURF" or mod.type == "MULTIRES":
			#if so, set the viewport display to 0, this effectively disables the modifier
            mod.show_viewport = 0
    #apply all modifiers
	bpy.ops.object.convert(target='MESH', keep_original=False)