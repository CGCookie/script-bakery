import bpy
import os
import random
import math

#--------------------------------------------------------------------------
#----------------------------- NAMING OPERATORS ---------------------------
#--------------------------------------------------------------------------



class OBJECT_OT_renameBase(bpy.types.Operator):
    bl_idname = "object.renamer_base"
    bl_label = "Rename"
    bl_description = "Rename selected objects from input Base String"
    
    def execute (self, context):
        
        kt = bpy.context.window_manager.katietools
        selOb = bpy.context.selected_editable_objects
        for ob in selOb:
            ob.name = kt.rename_base + '.000'    
        return {'FINISHED'}    
    
        
class OBJECT_OT_selectByBase(bpy.types.Operator):
    bl_idname = "object.select_by_base"
    bl_label = "Select"
    bl_description = "Select objects with name from input Base String"
    
    def execute (self, context):
        kt = bpy.context.window_manager.katietools
        baseString = kt.rename_base
        
        for ob in context.scene.objects:
            bpy.ops.object.select_pattern(pattern=baseString,case_sensitive=False,extend=False)
              
        return {'FINISHED'}
    
    
class OBJECT_OT_addPrefix(bpy.types.Operator):
    bl_idname = "object.add_prefix"
    bl_label = "Add Prefix"
    bl_description = "Add prefix to selected objects' names"
    
    def execute (self, context):
        kt = bpy.context.window_manager.katietools
        selOb = bpy.context.selected_objects
        
        for ob in selOb:
            ob.name = kt.rename_prefix + ob.name
              
        return {'FINISHED'}
    
    
class OBJECT_OT_addSuffix(bpy.types.Operator):
    bl_idname = "object.add_suffix"
    bl_label = "Add Suffix"
    bl_description = "Add suffix to selected objects' names"
    
    def execute (self, context):
        kt = bpy.context.window_manager.katietools
        selOb = bpy.context.selected_objects
        
        for ob in selOb:
            ob.name = ob.name + kt.rename_suffix
              
        return {'FINISHED'}    
 
    
class OBJECT_OT_copyDataNames(bpy.types.Operator):
    bl_idname = "object.copy_data_names"
    bl_label = "Copy to ObData"
    bl_description = "Copy object name as data name for all or selected mesh objects"
    
    def execute (self, context):
            
        myOb = list(bpy.context.selected_objects)
        allOb = bpy.data.objects
        
        for ob in allOb:
            ob.select = True
            
        selOb = bpy.context.selected_editable_objects  
                    
        for mesh in selOb:
            if mesh.data != None:
                mesh.data.name = mesh.name #+ '_DATA'
                
        for ob in bpy.data.objects:
            ob.select = False
        
        for ob in myOb:
            ob.select = True          
              
        return {'FINISHED'}