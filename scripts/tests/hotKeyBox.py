import bpy;
#define operations
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
hotKeyFourteenLbl = 'Show Wires';
hotKeyFifteenLbl = 'Hide Wires';

#    hotkey Panel
class hotkeyPanel(bpy.types.Panel):
    bl_label = "HotKey Box"
    bl_idname = "OBJECT_MT_hotKeyBox"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
 
    def draw(self , context):
        layout = self.layout
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
        layout.operator("hotkeybox.fourteen", text=hotKeyFourteenLbl)
        layout.operator("hotkeybox.fifteen", text=hotKeyFifteenLbl)
        layout.separator()
 
class OBJECT_OT_ButtonOne(bpy.types.Operator):
    bl_idname = "hotkeybox.one"
    bl_label = "Hotkey One"
    def execute(self, context):
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

class OBJECT_OT_ButtonSeven(bpy.types.Operator):
    bl_idname = "hotkeybox.seven"
    bl_label = "Hotkey Seven"
    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_by_number_vertices(number=4, type='GREATER')
        bpy.ops.mesh.quads_convert_to_tris(use_beauty=True)
        bpy.ops.mesh.uv_texture_add()
        bpy.ops.uv.lightmap_pack(PREF_CONTEXT='ALL_FACES', PREF_PACK_IN_ONE=True, PREF_NEW_UVLAYER=False, PREF_APPLY_IMAGE=False, PREF_IMG_PX_SIZE=1024, PREF_BOX_DIV=48, PREF_MARGIN_DIV=0.1)
        bpy.ops.object.mode_set(mode='OBJECT')
        return{'FINISHED'}
class OBJECT_OT_ButtonEight(bpy.types.Operator):
    bl_idname = "hotkeybox.eight"
    bl_label = "Hotkey eight"
    def execute(self, context):
        bpy.ops.object.select_linked(extend=False, type='OBDATA')
        bpy.ops.object.hide_view_set(unselected=False)
        return{'FINISHED'}
class OBJECT_OT_ButtonNine(bpy.types.Operator):
    bl_idname = "hotkeybox.nine"
    bl_label = "Hotkey nine"
    def execute(self, context):
        for ob in bpy.context.selected_objects:
            if ob.type == 'MESH' :
                ob.data.show_double_sided = 0
        return{'FINISHED'}
class OBJECT_OT_ButtonTen(bpy.types.Operator):
    bl_idname = "hotkeybox.ten"
    bl_label = "Hotkey ten"
    def execute(self, context):
        for ob in bpy.context.selected_objects:
            if ob.type == 'MESH' :
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
class OBJECT_OT_ButtonThirteen(bpy.types.Operator):
    bl_idname = "hotkeybox.thirteen"
    bl_label = "Hotkey thirteen"
    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.uv.reset()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.reset()
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_linked(extend=False, type='OBDATA')
        bpy.ops.object.hide_view_set(unselected=False)
        return{'FINISHED'}
class OBJECT_OT_ButtonFourteen(bpy.types.Operator):
    bl_idname = "hotkeybox.fourteen"
    bl_label = "Hotkey fourteen"
    def execute(self, context):
        for ob in bpy.context.selected_objects:
            if ob.type == 'MESH' :
                ob.show_all_edges = True
                ob.show_wire = True
        return{'FINISHED'}
class OBJECT_OT_ButtonFifteen(bpy.types.Operator):
    bl_idname = "hotkeybox.fifteen"
    bl_label = "Hotkey fifteen"
    def execute(self, context):
        for ob in bpy.context.selected_objects:
            if ob.type == 'MESH' :
                ob.show_all_edges = False
                ob.show_wire = False
        return{'FINISHED'}


class hotkeyMenu(bpy.types.Menu):
    bl_label = "HotKey Menu"
    bl_idname = "OBJECT_MT_hotKeyMenu"
    def draw(self , context):
        layout = self.layout
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

keymap = bpy.context.window_manager.keyconfigs.default.keymaps['3D View']

for keymapi in keymap.keymap_items:
    if keymapi.idname == "wm.call_menu" and keymapi.properties.name == "OBJECT_MT_hotKeyMenu":
        keymap.keymap_items.remove(keymapi)


keymapi = keymap.keymap_items.new('wm.call_menu', 'Z', 'PRESS', shift=True)
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
bpy.utils.register_class(OBJECT_OT_ButtonFourteen)
bpy.utils.register_class(OBJECT_OT_ButtonFifteen)
bpy.utils.register_class(hotkeyMenu)
bpy.utils.register_class(hotkeyPanel)