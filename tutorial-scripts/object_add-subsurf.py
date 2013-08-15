import bpy

scene = bpy.context.scene
selected = bpy.context.selected_objects
object = bpy.ops.object

for obj in selected:
    scene.objects.active = obj
    
    object.modifier_add(type="SUBSURF")
    
    for mod in obj.modifiers:
        if mod.type == "SUBSURF":
            bpy.context.object.modifiers[mod.name].levels = 2
            object.modifier_apply(apply_as="DATA", modifier=mod.name)