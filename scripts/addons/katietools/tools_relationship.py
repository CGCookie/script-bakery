import bpy
import os
import random
import math

#--------------------------------------------------------------------------
#----------------------------- RELATIONSHIP OPERATORS ---------------------
#--------------------------------------------------------------------------

class OBJECT_OT_createKtGroup(bpy.types.Operator):
    bl_idname = "object.create_ktgroup"
    bl_label = "Create ktGroup"
    bl_description = "Parent selected objects to a newly created ktGroup at the cursor's location"

    def execute(self, context):
        scn = bpy.context.scene
        selOb = bpy.context.selected_objects
        cursorLoc = scn.cursor_location
        
        if selOb:
            if bpy.context.active_object == None:
                bpy.context.scene.objects.active = selOb[0]
                
            actOb = bpy.context.active_object
            father = actOb.parent
            
            bpy.ops.object.add(type='EMPTY', location=cursorLoc) 
            newActOb = bpy.context.active_object
            newActOb.name = "ktGroup.000"
            newActOb.ktgroup = True
            
            for ob in selOb:
                ob.select = True
                
            bpy.ops.object.parent_set()
            
            for ob in selOb:
                ob.select = False

            if actOb.parent != None:
                newActOb.parent = father
                   
            newActOb.select = True            
        else:
            self.report({'INFO'}, "No objects selected")                            
                        
        return {'FINISHED'} # operator worked

    

class OBJECT_OT_ungroupKtGroup(bpy.types.Operator):
    bl_idname = "object.ungroup_ktgroup"
    bl_label = "Ungroup ktGroup"
    bl_description = "Clear parent for children and removes ktGroup"
        
    
    def execute(self, context):
        allOb = bpy.context.scene.objects
        selOb = bpy.context.selected_objects
        actOb = bpy.context.active_object
        
        if selOb:
            if actOb.ktgroup == True and len(actOb.children) > 0:
                father = actOb.parent
                chillin = actOb.children
                
                for ob in allOb: ob.select = False #CLEAR SELECTION
                
                for child in chillin:
                    child.select = True
                    
                bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
                
                if actOb.parent != None:
                    for child in chillin:
                        child.parent = father
                    
                for ob in allOb: ob.select = False #CLEAR SELECTION   

                actOb.select = True
                bpy.ops.object.delete()
                
                for child in chillin:
                    child.select = True
                
                allOb.active = chillin[0]
            else:
                self.report({'INFO'}, "Active Object is not a ktGroup with children")                           
                        
        return {'FINISHED'} # operator worked
    

'''class OBJECT_OT_centerToChildren(bpy.types.Operator):
    bl_idname = "object.center_to_children"
    bl_label = "Center to Children"
    bl_description = "Center parent empty to the center of it's children"

    def execute(self, context):
        allOb = bpy.context.scene.objects
        selOb = bpy.context.selected_objects
        actOb = bpy.context.active_object
        
        if selOb:
            if actOb.ktgroup == True and len(actOb.children) > 0:
                name = actOb.name
                bpy.ops.object.select_grouped()
                children = bpy.context.selected_objects
                bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
                bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY")
                bpy.ops.view3D.snap_cursor_to_selected()
                actOb = bpy.context.scene.objects[name]
                for ob in allOb:
                    ob.select = False
                    actOb.select = True
                bpy.ops.view3D.snap_selected_to_cursor()
                for ob in children:
                    ob.select = True
                actOb.select = True    
                bpy.ops.object.parent_set()
                for ob in allOb:
                    ob.select = False
                    actOb.select = True
                    
            else:
                self.report({'INFO'}, "Active Object is not a ktGroup with Children")                              
                        
        return {'FINISHED'} # operator worked'''  
 
    
class OBJECT_OT_centerToCursor(bpy.types.Operator):
    bl_idname = "object.center_ktgroup"
    bl_label = "Center ktGroup to Cursor"
    bl_description = "Set ktGroup origin at the cursor's location"
    
    def execute(self, context):
        scn = bpy.context.scene
        selOb = bpy.context.selected_objects
        actOb = bpy.context.active_object
        name = actOb.name
        
        if selOb:
            if actOb.ktgroup == True:
                if actOb.parent !=None:
                    self.report({'INFO'}, "Active Object is a child")
                else:     
                    bpy.ops.object.select_grouped(type="CHILDREN")
                    children = bpy.context.selected_objects
                    bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
                    
                    bpy.ops.object.create_ktgroup() #create new ktgroup with empty at cursor
                    
                    for ob in scn.objects:
                        if ob.name == name:
                            ob.select = True
                        else:
                            ob.select = False
                            
                    bpy.ops.object.delete() #delete original empty
                    scn.objects.active.name = name #rename newly created ktGroup with original name
                    
                    for ob in scn.objects:
                        if ob.name == name:
                            ob.select = True
                        else:
                            ob.select = False
                            
                    scn.objects.active = scn.objects[name]        

            else:
                self.report({'INFO'}, "Active Object is not a ktGroup")                          
                        
        return {'FINISHED'} # operator worked
        

class OBJECT_OT_duplicateKtGroup(bpy.types.Operator):
    bl_idname = "object.duplicate_ktgroup"
    bl_label = "Duplicate ktGroup"
    bl_description = "Duplicate ktGroup and children"
    
    def execute(self, context):
        allOb = bpy.context.scene.objects
        selOb = bpy.context.selected_objects
        actOb = bpy.context.active_object
        
        if selOb:
            if actOb.ktgroup == True and len(actOb.children) > 0:
                bpy.ops.object.select_grouped(extend=True,type="CHILDREN_RECURSIVE")
                newSel = bpy.context.selected_objects
                bpy.ops.object.duplicate(linked=False)
                
                actOb = bpy.context.active_object

                for ob in bpy.context.scene.objects:
                    if actOb.name != ob.name:
                        ob.select = False 
            else:
                self.report({'INFO'}, "Active Object is not a ktGroup with Children")                           
                        
        return {'FINISHED'} # operator worked


class OBJECT_OT_mergeKtGroup(bpy.types.Operator):
    bl_idname = "object.merge_ktgroup"
    bl_label = "Merge"
    bl_description = "Merge ktGroup's children into single object and remove ktGroup"
    
    def execute(self, context):
        allOb = bpy.context.scene.objects
        selOb = bpy.context.selected_objects
        actOb = bpy.context.active_object
        
        if selOb:
            if actOb.ktgroup == True and len(actOb.children) > 0:
                
                name = actOb.name
                invisOb = []
                for ob in allOb:
                    if ob.hide == True:
                        invisOb.append(ob) #add hidden objects to invisOb array
                    ob.hide = False #unhide all ohjects
                
                bpy.ops.object.select_grouped(extend=True,type="CHILDREN_RECURSIVE")
                selChildren = bpy.context.selected_objects
                
                bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
                
                meshes = []
                for child in selChildren:
                    if child.type != "MESH":
                        child.select = True
                    else:
                        child.select = False
                        meshes.append(child)
                        
                bpy.ops.object.delete()
                    
                for mesh in meshes:
                    mesh.select = True
                    
                bpy.context.scene.objects.active = meshes[0]
                bpy.ops.object.join()
                bpy.context.active_object.name = name
                bpy.context.active_object.hide = False  
                
                for ob in invisOb:
                    if ob.name != name:
                        ob.hide = True #re-hide objects previously hidden 
                  
            else:
                self.report({'INFO'}, "Active Object is not a ktGroup with Children")                           
                        
        return {'FINISHED'} # operator worked 

    
class OBJECT_OT_deleteKtGroup(bpy.types.Operator):
    bl_idname = "object.delete_ktgroup"
    bl_label = "Delete ktGroup"
    bl_description = "Delete ktGroup and its children"
    
    def execute(self, context):
        allOb = bpy.context.scene.objects
        selOb = bpy.context.selected_objects
        actOb = bpy.context.active_object
        
        if selOb:
            if actOb.ktgroup == True and len(actOb.children) > 0:
                invisOb = []
                for ob in allOb:
                    if ob.hide == True:
                        invisOb.append(ob) #add hidden objects to invisOb array
                    ob.hide = False #unhide all ohjects
                    
                bpy.ops.object.select_grouped(extend=True,type="CHILDREN_RECURSIVE")
                bpy.ops.object.delete()
                
                for ob in invisOb:
                    ob.hide = True #re-hide objects previously hidden   
            else:
                self.report({'INFO'}, "Active Object is not a ktGroup with Children")                           
                        
        return {'FINISHED'} # operator worked      



#---------- BUDDY MESHES ------- # 
       
class OBJECT_OT_combineMeshes(bpy.types.Operator):
    bl_idname = "object.combine_meshes"
    bl_label = "Combine"
    bl_description = "Joins selected mesh objects and stores originally selected meshes as vertex groups"
      
        
    def execute(self, context):
        selOb = bpy.context.selected_objects
        scn = bpy.context.scene
        
        if selOb:
            if len(selOb) > 1:
                bmOb = []
                for ob in selOb:
                    if ("-BM_" in ob.name):
                        bmOb.append(ob)
                if len(bmOb) > 0:
                    self.report({'INFO'}, "Can't combine with other Buddy Meshes")
                else:        
                    for ob in selOb:
                        if ob.type != "MESH":
                            ob.select = False
                        
                    newSelOb = bpy.context.selected_objects
                    
                    if bpy.context.active_object not in newSelOb:
                        scene.objects.active = newSelOb[0]
                        
                    actOb = scn.objects.active
                    
                    for ob in newSelOb:  
                        scn.objects.active = ob
                        mesh = ob.data
                        vert_list = []
                        
                        for v in mesh.vertices:
                            vert_list.append(v.index)   
                        
                        newVGroup = ob.vertex_groups.new(ob.name)
                        newVGroup.add(vert_list,1.0,'ADD')
                            
                    bpy.ops.object.join()
                    scn.objects.active.name = "-BM_" + actOb.name
                    
                    bmName = scn.objects.active.name
            else:
                self.report({'INFO'}, "Only 1 object selected")        
        else:
            self.report({'INFO'}, "No objects selected")
             
         
        return {'FINISHED'} # operator worked
    

class OBJECT_OT_splitPoseMesh(bpy.types.Operator):
    bl_idname = "object.split_posemesh"
    bl_label = "Split"
    bl_description = "Separates mesh based on its vertex groups"
    
    def execute(self, context):
        selOb = bpy.context.selected_objects
        scn = bpy.context.scene
        kt = bpy.context.window_manager.katietools
        
        if selOb:
            if len(selOb) > 1:
                self.report({'INFO'}, "Only works with one object selected")
            else:
                if ("-BM" in bpy.context.active_object.name):
                    bpy.context.active_object.name = "tempName"
                else:
                    self.report({'INFO'}, "No BM object selected")    
                    
                actOb = bpy.context.active_object    
        
                vgroups = actOb.vertex_groups
                
                for vg in vgroups:
                    if bpy.ops.object.mode_set.poll(): #jump to edit mode
                        bpy.ops.object.mode_set(mode="EDIT")
                        
                    bpy.ops.wm.context_set_value(data_path='tool_settings.mesh_select_mode',value='(True,False,False)')
                    bpy.ops.mesh.select_all(action='DESELECT') #deselect all
                    
                    bpy.ops.object.vertex_group_set_active(group=vg.name)
                    bpy.ops.object.vertex_group_select()
                    bpy.ops.mesh.separate(type="SELECTED")
                    
                if bpy.ops.object.mode_set.poll(): #jump to object mode
                    bpy.ops.object.mode_set(mode="OBJECT")
                
                # Delete blank object    
                for ob in scn.objects:
                    if actOb.name == ob.name:
                        ob.select = True
                    else:
                        ob.select = False
                    bpy.ops.object.delete()
                
                # Rename separated objects based on active vertex group; then remove vertex groups       
                for ob in scn.objects:    
                    if (actOb.name in ob.name):
                        ob.select = True
                    else:
                        ob.select = False      
                    
                    if ob.select == True:
                        scn.objects.active = ob
                        actVG = bpy.context.active_object.vertex_groups.active
                        ob.name = actVG.name
                        bpy.ops.object.vertex_group_remove(all=True)
        else:
            self.report({'INFO'}, "No object selected")
                        
        return {'FINISHED'} # operator worked   