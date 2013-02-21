import bpy
import os
import random
import math

#--------------------------------------------------------------------------
#-----------------------------CLEANUP OPERATORS ---------------------------
#--------------------------------------------------------------------------

 
 
#APPLY MIRROR MODIFIERS
class OBJECT_OT_modApplyMirror(bpy.types.Operator):
    bl_idname = "object.apply_mirror_mods"
    bl_label = "Appy Mirrors"
    bl_description = "Apply existing Mirror modifiers for either selected or all mesh objects"
    
    def execute(self, context):
        scn = bpy.context.scene
        selOb = bpy.context.selected_objects
        
        if selOb:
            targetOb = selOb
            msg = "Mirror modifiers applied for selected mesh objects"
        else:
            targetOb = scn.objects
            msg = "Mirror modifiers applied for all mesh objects"       
            
        for ob in targetOb:
            if ob.type == "MESH":
                context.scene.objects.active = ob
                for mod in ob.modifiers:
                    if mod.type == "MIRROR":
                        #bpy.ops.object.modifier_move_up(modifier=mod.name)
                        bpy.ops.object.modifier_apply(apply_as='DATA',modifier=mod.name)
                    
        self.report({'INFO'}, msg)           
                                       
        return {'FINISHED'}
    

class OBJECT_OT_modSelectMirror(bpy.types.Operator):
    bl_idname = "object.select_mirror_mods"
    bl_label = "Select Mirrors"
    bl_description = "Select objects with MIRROR modifiers"
    
    def execute(self, context):
        scn = bpy.context.scene
        
        mirrorOb = []
        
        for ob in scn.objects:
            if ob.type == "MESH":
                context.scene.objects.active = ob
                for mod in ob.modifiers:
                    if mod.type == "MIRROR":
                        mirrorOb.append(ob)
                        
        if len(mirrorOb) >= 1:
            for ob in scn.objects:
                if ob in mirrorOb:
                    ob.select = True
                else:
                    ob.select = False    
            scn.objects.active = mirrorOb[0]
            self.report({'INFO'}, str(len(mirrorOb)) + " objects have a MIRROR modifier")
        else:
            self.report({'INFO'}, 'No objects have a MIRROR modifier')                                
                             
        return {'FINISHED'}
    
    
    
#APPLY SOLIDIFY MODIFIERS
class OBJECT_OT_modApplySolidified(bpy.types.Operator):
    bl_idname = "object.apply_solidify_mods"
    bl_label = "Appy Solidified"
    bl_description = "Apply existing Solidify modifiers for either selected or all mesh objects"
    
    def execute(self, context):
        scn = bpy.context.scene
        selOb = bpy.context.selected_objects
        
        if selOb:
            targetOb = selOb
            msg = "Solidify modifiers applied for selected mesh objects"
        else:
            targetOb = scn.objects
            msg = "Solidify modifiers applied for all mesh objects"       
            
        for ob in targetOb:
            context.scene.objects.active = ob
            for mod in ob.modifiers:
                if mod.type == "SOLIDIFY":
                    #bpy.ops.object.modifier_move_up(modifier=mod.name)
                    bpy.ops.object.modifier_apply(apply_as='DATA',modifier=mod.name)
                    
        self.report({'INFO'}, msg)            
                                       
        return {'FINISHED'}
    
class OBJECT_OT_modSelectSolidify(bpy.types.Operator):
    bl_idname = "object.select_solidify_mods"
    bl_label = "Select Solidified"
    bl_description = "Select objects with SOLIDIFY modifiers"
    
    def execute(self, context):
        scn = bpy.context.scene
        
        solidifyOb = []
        
        for ob in scn.objects:
            if ob.type == "MESH":
                context.scene.objects.active = ob
                for mod in ob.modifiers:
                    if mod.type == "SOLIDIFY":
                        solidifyOb.append(ob)
                        
        if len(solidifyOb) >= 1:
            for ob in scn.objects:
                if ob in solidifyOb:
                    ob.select = True
                else:
                    ob.select = False    
            scn.objects.active = solidifyOb[0]
            self.report({'INFO'}, str(len(solidifyOb)) + " objects have a SOLIDIFY modifier")
        else:
            self.report({'INFO'}, 'No objects have a SOLIDIFY modifier')                                
                             
        return {'FINISHED'}
        

#DELETE UNUSED MATERIALS   
class OBJECT_OT_matDeleteUnused(bpy.types.Operator):
    bl_idname = "mat.delete_unused"
    bl_label = "Delete Unused"
    bl_description = "Delete Materials not linked to any object"
    
    def execute(self, context):
        scn = bpy.context.scene
        kt = bpy.context.window_manager.katietools
        unused = []
        
        for mat in bpy.data.materials:
            if mat.users == 0:
                unused.append(mat)
                bpy.data.materials.remove(mat)
                
        kt.mat_matcaps_exist = False
        self.report({'INFO'}, str(len(unused)) + " unused materials deleted")       
        
        return {'FINISHED'}
       

#NUKE UV MAPS    
class OBJECT_OT_uvNuke(bpy.types.Operator):
    bl_idname = "data.uv_nuke"
    bl_label = "Nuke UV Maps"
    bl_description = "Remove UV maps for all or selected objects"
    
    def execute(self, context):
                
        scn = bpy.context.scene
        selOb = bpy.context.selected_objects
        
        if selOb:
            targetOb = selOb
            msg = "UV maps deleted from selected mesh objects"
        else:
            targetOb = scn.objects
            msg = "UV maps deleted from all mesh objects"       
            
        for ob in targetOb:
            if ob.type == "MESH":
                scn.objects.active = ob
            
                uv = list(ob.data.uv_textures)
                
                for i in range(len(uv)):
                        ob.data.uv_textures.active_index = i - 1
                        bpy.ops.mesh.uv_texture_remove()
                        
        self.report({'INFO'}, msg)                
        
        return {'FINISHED'}
    
    
class OBJECT_OT_dataUvSelect(bpy.types.Operator):
    bl_idname = "object.select_uv"
    bl_label = "Select UVs"
    bl_description = "Select objects with UV MAPS"
    
    def execute(self, context):
        scn = bpy.context.scene
        
        uvOb = []
        
        for ob in scn.objects:
            if ob.type == "MESH":
                uv = list(ob.data.uv_textures)
                if len(uv) >= 1:
                    uvOb.append(ob)
                        
        if len(uvOb) >= 1:
            for ob in scn.objects:
                if ob in uvOb:
                    ob.select = True
                else:
                    ob.select = False    
            scn.objects.active = uvOb[0]
            self.report({'INFO'}, str(len(uvOb)) + " objects have UV MAPS")
        else:
            self.report({'INFO'}, 'No objects have UV MAPS assigned')                                
                             
        return {'FINISHED'}    
    

#NUKE VERTEX GROUPS    
class OBJECT_OT_vgNuke(bpy.types.Operator):
    bl_idname = "data.vg_nuke"
    bl_label = "Nuke Vertex Groups"
    bl_description = "Delete Materials not linked to any object"
    
    def execute(self, context):    
        scn = bpy.context.scene
        selOb = bpy.context.selected_objects
        
        if selOb:
            targetOb = selOb
            msg = "Vertex Groups deleted from selected mesh objects"
        else:
            targetOb = scn.objects
            msg = "Vertex Groups deleted from all mesh objects"
            
        for ob in targetOb:
            if ob.type == "MESH":
                scn.objects.active = ob
                bpy.ops.object.vertex_group_remove(all=True)
        self.report({'INFO'}, msg)
        
        return {'FINISHED'}
    
class OBJECT_OT_vgSelect(bpy.types.Operator):
    bl_idname = "object.select_vg"
    bl_label = "Select V Group"
    bl_description = "Select objects with VERTEX GROUPS"
    
    def execute(self, context):
        scn = bpy.context.scene
        
        vgOb = []
        
        for ob in scn.objects:
            if ob.type == "MESH":
                if len(ob.vertex_groups) >= 1:
                    vgOb.append(ob)
                        
        if len(vgOb) >= 1:
            for ob in scn.objects:
                if ob in vgOb:
                    ob.select = True
                else:
                    ob.select = False    
            scn.objects.active = vgOb[0]
            self.report({'INFO'}, str(len(vgOb)) + " objects have VERTEX GROUPS")
        else:
            self.report({'INFO'}, 'No objects have VERTEX GROUPS')                                
                             
        return {'FINISHED'}
    

#NUKE VERTEX COLORS    
class OBJECT_OT_vcNuke(bpy.types.Operator):
    bl_idname = "data.vc_nuke"
    bl_label = "Nuke Vertex Colors"
    bl_description = "Remove Vertex Color Layers for all or selected objects"
    
    def execute(self, context):
        scn = bpy.context.scene
        selOb = bpy.context.selected_objects
        
        if selOb:
            targetOb = selOb
            msg = "Vertex Colors deleted from selected mesh objects"
        else:
            targetOb = scn.objects
            msg = "Vertex Colors deleted from all mesh objects"
            
        for ob in targetOb:
            if ob.type == "MESH":
                scn.objects.active = ob
            
                vc = list(ob.data.vertex_colors)
                
                for i in range(len(vc)):
                        ob.data.vertex_colors.active_index = i - 1
                        bpy.ops.mesh.vertex_color_remove()
                        
        self.report({'INFO'}, msg)               
        
        return {'FINISHED'}

    
class OBJECT_OT_vcSelect(bpy.types.Operator):
    bl_idname = "object.vc_select"
    bl_label = "Select V Color"
    bl_description = "Select objects with VERTEX COLORS"
    
    def execute(self, context):
        scn = bpy.context.scene
        
        vcOb = []
        
        for ob in scn.objects:
            if ob.type == "MESH":
                vc = list(ob.data.vertex_colors)
                if len(vc) >= 1:
                    vcOb.append(ob)
                        
        if len(vcOb) >= 1:
            for ob in scn.objects:
                if ob in vcOb:
                    ob.select = True
                else:
                    ob.select = False    
            scn.objects.active = vcOb[0]
            self.report({'INFO'}, str(len(vcOb)) + " objects have VERTEX COLORS")
        else:
            self.report({'INFO'}, 'No objects have VERTEX COLORS')                                
                             
        return {'FINISHED'}


def destroyData(key):
    xObjects = []
    xMeshes = []
    xMats = []
    
    
    for ob in bpy.data.objects:
        if key in ob.name and ob.users == 0:
            xObjects.append(ob)
            bpy.data.objects.remove(ob)
            
    for m in bpy.data.meshes:
        if key in m.name and m.users == 0:
            xMeshes.append(m)
            bpy.data.meshes.remove(m)
            
    for mat in bpy.data.materials:
        if key in mat.name and mat.users == 0:
            xMats.append(mat)
            bpy.data.materials.remove(mat)
            
    return ("--------------------------------------" + '\n' +
            str(len(xObjects)) + " Objects destroyed" + '\n' +
            str(len(xMeshes)) + " Meshes decimated" + '\n' + 
            str(len(xMats)) + " Materials extinguished" + '\n' +
            "--------------------------------------")     
                    
                    
    
class OBJECT_OT_cleanData(bpy.types.Operator):
    bl_idname = "data.clean_data"
    bl_label = "Clean Data"
    bl_description = "Destroy all unused data blocks globally or based on key string"
    
    key = bpy.props.StringProperty()
    
    def execute(self, context):
        if self.key == "**KEY**":
            self.report({'INFO'}, "No Key set. 'all' can be used to delete all unused data blocks")
        else:    
            destroy = destroyData(self.key)
            print (destroy)                               
                             
        return {'FINISHED'}
