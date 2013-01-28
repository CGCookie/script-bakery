#script by Alex Telford | CG Cookie | www.blendercookie.com
#Description:
#This script is my personal hotkey box that works with the hotkey Shift+Z, it contains whatever I happen to be using at the time and changes on a weekly basis.
#Usage:
#Load into script editor, hit run script.
#Editing:
#You can edit the file by changing the commands for each hotkey, any complex functions you see I just set to another function here.
#import blender python module
import bpy;
#define operations
#hotKeyNumber is the function that is run
#hotKeyNumberLbl is the text that we see in the box
hotKeyOne = "bpy.ops.mesh.merge(type='LAST', uvs=False)";
hotKeyOneLbl = 'Merge Last';
hotKeyTwo = "bpy.ops.mesh.remove_doubles(mergedist=0.025)";
hotKeyTwoLbl = 'Remove Doubles';
hotKeyThree = "bpy.ops.mesh.merge(uvs=False)";
hotKeyThreeLbl = 'Merge Center';
hotKeyFour = "bpy.ops.mesh.flip_normals()";
hotKeyFourLbl = 'Flip Normals';
hotKeyFive = "bpy.ops.mesh.subdivide()";
hotKeyFiveLbl = 'Subdivide';
hotKeySix = "bpy.ops.sculpt.sculptmode_toggle()";
hotKeySixLbl = 'Sculpt Mode';
hotKeySevenLbl = 'Create Lightmap UVs';
hotKeyEightLbl = 'Hide Linked';
hotKeyNineLbl = 'Disable Double Sided';
hotKeyTenLbl = 'Enable Double Sided';
hotKeyEleven = "bpy.ops.mesh.loop_to_region(select_bigger=False)";
hotKeyElevenLbl = 'Select Loop Inner Region';
hotKeyTwelve = "bpy.ops.mesh.loop_to_region(select_bigger=True)";
hotKeyTwelveLbl = 'Select Loop Outer Region';
hotKeyThirteenLbl = 'Reset UV';

#    hotkey Panel
class hotkeyPanel(bpy.types.Panel):
    bl_label = "HotKey Box"
    bl_idname = "OBJECT_MT_hotKeyBox"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
 
    def draw(self , context):
        layout = self.layout
		#make sure you specify the hotkey here to make it appear in the box
        layout.operator("hotkeybox.one", text=hotKeyOneLbl)
        layout.operator("hotkeybox.two", text=hotKeyTwoLbl)
        layout.operator("hotkeybox.three", text=hotKeyThreeLbl)
        layout.operator("hotkeybox.four", text=hotKeyFourLbl)
        layout.operator("hotkeybox.five", text=hotKeyFiveLbl)
        layout.operator("hotkeybox.six", text=hotKeySixLbl)
        layout.operator("hotkeybox.seven", text=hotKeySevenLbl)
        layout.operator("hotkeybox.eight", text=hotKeyEightLbl)
        layout.operator("hotkeybox.nine", text=hotKeyNineLbl)
        layout.operator("hotkeybox.ten", text=hotKeyTenLbl)
        layout.operator("hotkeybox.eleven", text=hotKeyElevenLbl)
        layout.operator("hotkeybox.twelve", text=hotKeyTwelveLbl)
        layout.operator("hotkeybox.thirteen", text=hotKeyThirteenLbl)
        layout.separator()
#all hotkeys need a class 
class OBJECT_OT_ButtonOne(bpy.types.Operator):
	#the name of the class to use in the panel
    bl_idname = "hotkeybox.one"
	#label is irrelevant but necessary
    bl_label = "Hotkey One"
	#execution function
    def execute(self, context):
		#exec function will execute text as code.
        exec(hotKeyOne);
        return{'FINISHED'}
class OBJECT_OT_ButtonTwo(bpy.types.Operator):
    bl_idname = "hotkeybox.two"
    bl_label = "Hotkey Two"
    def execute(self, context):
        exec(hotKeyTwo);
        return{'FINISHED'}
class OBJECT_OT_ButtonThree(bpy.types.Operator):
    bl_idname = "hotkeybox.three"
    bl_label = "Hotkey Three"
    def execute(self, context):
        exec(hotKeyThree);
        return{'FINISHED'}
class OBJECT_OT_ButtonFour(bpy.types.Operator):
    bl_idname = "hotkeybox.four"
    bl_label = "Hotkey Four"
    def execute(self, context):
        exec(hotKeyFour);
        return{'FINISHED'}
class OBJECT_OT_ButtonFive(bpy.types.Operator):
    bl_idname = "hotkeybox.five"
    bl_label = "Hotkey Five"
    def execute(self, context):
        exec(hotKeyFive);
        return{'FINISHED'}
class OBJECT_OT_ButtonSix(bpy.types.Operator):
    bl_idname = "hotkeybox.six"
    bl_label = "Hotkey Six"
    def execute(self, context):
        exec(hotKeySix);
        return{'FINISHED'}
#some functions require more code
#uv lightmap for unity
class OBJECT_OT_ButtonSeven(bpy.types.Operator):
    bl_idname = "hotkeybox.seven"
    bl_label = "Hotkey Seven"
    def execute(self, context):
		#set edit mode
        bpy.ops.object.mode_set(mode='EDIT')
		#select nGons
        bpy.ops.mesh.select_by_number_vertices(number=4, type='GREATER')
		#convert nGons to tris
        bpy.ops.mesh.quads_convert_to_tris(use_beauty=True)
		#add uv map
        bpy.ops.mesh.uv_texture_add()
		#lightmap pack with predefined settings best for unity
        bpy.ops.uv.lightmap_pack(PREF_CONTEXT='ALL_FACES', PREF_PACK_IN_ONE=True, PREF_NEW_UVLAYER=False, PREF_APPLY_IMAGE=False, PREF_IMG_PX_SIZE=1024, PREF_BOX_DIV=48, PREF_MARGIN_DIV=0.1)
		#go back to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        return{'FINISHED'}
#hide all objects with linked data
class OBJECT_OT_ButtonEight(bpy.types.Operator):
    bl_idname = "hotkeybox.eight"
    bl_label = "Hotkey eight"
    def execute(self, context):
		#select linked
        bpy.ops.object.select_linked(extend=False, type='OBDATA')
		#hide
        bpy.ops.object.hide_view_set(unselected=False)
        return{'FINISHED'}
#Disable double sided
class OBJECT_OT_ButtonNine(bpy.types.Operator):
    bl_idname = "hotkeybox.nine"
    bl_label = "Hotkey nine"
    def execute(self, context):
		#loop through objects in selection
        for ob in bpy.context.selected_objects:
			#check if it is a mesh
            if ob.type == 'MESH' :
				#disable double sided
                ob.data.show_double_sided = 0
        return{'FINISHED'}
#enable double sided
class OBJECT_OT_ButtonTen(bpy.types.Operator):
    bl_idname = "hotkeybox.ten"
    bl_label = "Hotkey ten"
    def execute(self, context):
        for ob in bpy.context.selected_objects:
            if ob.type == 'MESH' :
				#enable double sided
                ob.data.show_double_sided = 1
        return{'FINISHED'}
class OBJECT_OT_ButtonEleven(bpy.types.Operator):
    bl_idname = "hotkeybox.eleven"
    bl_label = "Hotkey Eleven"
    def execute(self, context):
        exec(hotKeyEleven);
        return{'FINISHED'}

class OBJECT_OT_ButtonTwelve(bpy.types.Operator):
    bl_idname = "hotkeybox.twelve"
    bl_label = "Hotkey Twelve"
    def execute(self, context):
        exec(hotKeyTwelve);
        return{'FINISHED'}
#reset uvs - this was for a specific set of objects I was working with so not very useful outside of that project.
class OBJECT_OT_ButtonThirteen(bpy.types.Operator):
    bl_idname = "hotkeybox.thirteen"
    bl_label = "Hotkey thirteen"
    def execute(self, context):
		#edit mode
        bpy.ops.object.mode_set(mode='EDIT')
		#reset uv's - why I needed this I cannot remember but it served some purpose ;)
        bpy.ops.uv.reset()
		#select all
        bpy.ops.mesh.select_all(action='SELECT')
		#reset uv's again
        bpy.ops.uv.reset()
		#object mode
        bpy.ops.object.mode_set(mode='OBJECT')
		#select linked
        bpy.ops.object.select_linked(extend=False, type='OBDATA')
		#hide
        bpy.ops.object.hide_view_set(unselected=False)
        return{'FINISHED'}

#initiate menu
class hotkeyMenu(bpy.types.Menu):
    bl_label = "HotKey Menu"
    bl_idname = "OBJECT_MT_hotKeyMenu"
    def draw(self , context):
        layout = self.layout
		#remember to add your hotkeys here
        layout.operator("hotkeybox.one", text=hotKeyOneLbl)
        layout.operator("hotkeybox.two", text=hotKeyTwoLbl)
        layout.operator("hotkeybox.three", text=hotKeyThreeLbl)
        layout.operator("hotkeybox.four", text=hotKeyFourLbl)
        layout.operator("hotkeybox.five", text=hotKeyFiveLbl)
        layout.operator("hotkeybox.six", text=hotKeySixLbl)
        layout.operator("hotkeybox.seven", text=hotKeySevenLbl)
        layout.operator("hotkeybox.eight", text=hotKeyEightLbl)
        layout.operator("hotkeybox.eleven", text=hotKeyElevenLbl)
        layout.operator("hotkeybox.twelve", text=hotKeyTwelveLbl)
        layout.operator("hotkeybox.thirteen", text=hotKeyThirteenLbl)
        layout.separator()
#load keymap
keymap = bpy.context.window_manager.keyconfigs.default.keymaps['3D View']
#loop through keys
for keymapi in keymap.keymap_items:
	#if exists already
    if keymapi.idname == "wm.call_menu" and keymapi.properties.name == "OBJECT_MT_hotKeyMenu":
		#remove
        keymap.keymap_items.remove(keymapi)

#set hotkey to shoft+Z
keymapi = keymap.keymap_items.new('wm.call_menu', 'Z', 'PRESS', shift=True)
#set name
keymapi.properties.name = "OBJECT_MT_hotKeyMenu"

# registering and menu integration
bpy.utils.register_class(OBJECT_OT_ButtonOne)
bpy.utils.register_class(OBJECT_OT_ButtonTwo)
bpy.utils.register_class(OBJECT_OT_ButtonThree)
bpy.utils.register_class(OBJECT_OT_ButtonFour)
bpy.utils.register_class(OBJECT_OT_ButtonFive)
bpy.utils.register_class(OBJECT_OT_ButtonSix)
bpy.utils.register_class(OBJECT_OT_ButtonSeven)
bpy.utils.register_class(OBJECT_OT_ButtonEight)
bpy.utils.register_class(OBJECT_OT_ButtonNine)
bpy.utils.register_class(OBJECT_OT_ButtonTen)
bpy.utils.register_class(OBJECT_OT_ButtonEleven)
bpy.utils.register_class(OBJECT_OT_ButtonTwelve)
bpy.utils.register_class(OBJECT_OT_ButtonThirteen)
bpy.utils.register_class(hotkeyMenu)
bpy.utils.register_class(hotkeyPanel)