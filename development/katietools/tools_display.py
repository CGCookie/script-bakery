import bpy
import os
import random
import math

#--------------------------------------------------------------------------
#----------------------------- DISPLAY OPERATORS -------------------------
#--------------------------------------------------------------------------


#OPENGL LIGHT PRESETS  

class OBJECT_OT_oglAddPreset(bpy.types.Operator):
    bl_idname = "system.ogl_add_preset"
    bl_label = "Add OpenGL Preset"
    bl_description = "Add OpenGL preset according to current settings"
           
    def execute(self, context):
        kt = bpy.context.window_manager.katietools
        system = bpy.context.user_preferences.system
        presets = bpy.context.user_preferences.ogl_presets
        preName = kt.ogl_name
        oglNames = []
        
        lampA = system.solid_lights[0]
        lampB = system.solid_lights[1]
        lampC = system.solid_lights[2]
        
        a_use = lampA.use
        a_dc = list(lampA.diffuse_color) # bizarrely CRUCIAL to list values (?!)
        a_sc = list(lampA.specular_color)
        a_dir = list(lampA.direction)
        b_use = lampB.use
        b_dc = list(lampB.diffuse_color)
        b_sc = list(lampB.specular_color)
        b_dir = list(lampB.direction)
        c_use = lampC.use
        c_dc = list(lampC.diffuse_color)
        c_sc = list(lampC.specular_color)
        c_dir = list(lampC.direction)
        
        presets[preName] = {"a_use":a_use, "a_dc":a_dc, "a_sc":a_sc, "a_dir":a_dir,
                            "b_use":b_use, "b_dc":b_dc, "b_sc":b_sc, "b_dir":b_dir,
                            "c_use":c_use, "c_dc":c_dc, "c_sc":c_sc, "c_dir":c_dir}
                            
        for p in presets:
            oglNames.append((p,p,'OpenGl preset'))
            
        kt.ogl_toggle = False    
            
        def register():  
            bpy.types.KatieToolsProps.ogl_preset_enum = bpy.props.EnumProperty(name='OpenGL Presets',default='Head Light',items=sorted(oglNames, key=lambda p: str(p[0]).lower(), reverse=True))
        register()    
                        
        return {'FINISHED'}
    
    
class OBJECT_OT_oglDeletePreset(bpy.types.Operator):
    bl_idname = "system.ogl_delete_preset"
    bl_label = "Delete OpenGL Preset"
    bl_description = "Delete selected OpenGL preset"
           
    def execute(self, context):
        kt = bpy.context.window_manager.katietools
        presets = bpy.context.user_preferences.ogl_presets
        oglNames = []
        
        del presets[kt.ogl_preset_enum] #delete from presets
                            
        for p in presets: #delete from enumerator
            oglNames.append((p,p,'OpenGl preset'))
            
        def register():  
            bpy.types.KatieToolsProps.ogl_preset_enum = bpy.props.EnumProperty(name='OpenGL Presets',default='Blender Default',items=sorted(oglNames, key=lambda p: str(p[0]).lower(), reverse=True))
        register()    
                        
        return {'FINISHED'}    

    
class OBJECT_OT_oglApplyPreset(bpy.types.Operator):
    bl_idname = "system.ogl_apply_preset"
    bl_label = "Apply OpenGL Preset"
    bl_description = "Apply selected OpenGL Preset"
           
    def execute(self, context):
        kt = bpy.context.window_manager.katietools
        system = bpy.context.user_preferences.system
        presets = bpy.context.user_preferences.ogl_presets
        preName = kt.ogl_preset_enum
        
        if kt.ogl_preset_enum  in presets:
            a_use = presets[kt.ogl_preset_enum]['a_use']
            a_dc = presets[kt.ogl_preset_enum]['a_dc']
            a_sc = presets[kt.ogl_preset_enum]['a_sc']
            a_dir = presets[kt.ogl_preset_enum]['a_dir']
            b_use = presets[kt.ogl_preset_enum]['b_use']
            b_dc = presets[kt.ogl_preset_enum]['b_dc']
            b_sc = presets[kt.ogl_preset_enum]['b_sc']
            b_dir = presets[kt.ogl_preset_enum]['b_dir']
            c_use = presets[kt.ogl_preset_enum]['c_use']
            c_dc = presets[kt.ogl_preset_enum]['c_dc']
            c_sc = presets[kt.ogl_preset_enum]['c_sc']
            c_dir = presets[kt.ogl_preset_enum]['c_dir']
            
            
        lampA = system.solid_lights[0]
        lampB = system.solid_lights[1]
        lampC = system.solid_lights[2]
        
        lampA.use = a_use
        lampA.diffuse_color = a_dc
        lampA.specular_color = a_sc
        lampA.direction = a_dir
        
        lampB.use = b_use
        lampB.diffuse_color = b_dc
        lampB.specular_color = b_sc
        lampB.direction = b_dir
        
        lampC.use = c_use
        lampC.diffuse_color = c_dc
        lampC.specular_color = c_sc
        lampC.direction = c_dir
                                     
        return {'FINISHED'} 


#DOUBLE-SIDED TOGGLE      
class OBJECT_OT_doubleSidedToggle(bpy.types.Operator):
    #connecting this class to the button of the same name
    bl_idname = "object.double_sided_toggle"
    bl_label = "Double-Sided"
    bl_description = "Toggle double-sided lighting in the viewport globally"
           
    #function that's executed when button is pushed
    def execute(self, context):
        scn = bpy.context.scene
        selOb = bpy.context.selected_objects
        
        if selOb:
            targetOb = selOb
        else:
            targetOb = scn.objects

        newSel = []
        
        for ob in targetOb:
            if ob.type == "MESH":
                newSel.append(ob)
        if newSel[0].data.show_double_sided == True:
            for ob in newSel:
                mesh = ob.data
                mesh.show_double_sided = False
        elif newSel[0].data.show_double_sided == False:
            for ob in newSel:
                mesh = ob.data
                mesh.show_double_sided = True                
                        
        return {'FINISHED'} # operator worked 
        
#ALL EDGES TOGGLE             
class OBJECT_OT_allEdgesToggle(bpy.types.Operator):
    #connecting this class to the button of the same name
    bl_idname = "object.all_edges_toggle"
    bl_label = "All Edges"
    bl_description = "Toggle wireframe-on-shaded for all mesh objects in the viewport"
    
    #function that's executed when button is pushed
    def execute(self, context):
        scn = bpy.context.scene
        selOb = bpy.context.selected_objects
        
        if selOb:
            targetOb = selOb
        else:
            targetOb = scn.objects     
            
        for ob in targetOb:
            if ob.type == "MESH":
                ob.select = 1
            else:
                ob.select = 0
                
        newSel = list(bpy.context.selected_objects)
            
        if newSel:        
            if newSel[0].show_wire == True:
                toggle = 1
            else:
                toggle = 0
                     
            for ob in newSel:
                if ob.type == "MESH":
                    mesh = ob.data
                    if toggle == 1:
                        ob.show_all_edges = False
                        ob.show_wire = False
                    if toggle == 0:
                        ob.show_all_edges = True
                        ob.show_wire = True
                        scn.objects.active = ob
                        #if bpy.ops.object.mode_set.poll():
                            #bpy.ops.object.mode_set(mode="EDIT")
                            #bpy.ops.object.mode_set(mode="OBJECT")
                            
        if targetOb == scn.objects:
            for ob in scn.objects:
                ob.select = False                    
                
        bpy.context.scene.frame_current = bpy.context.scene.frame_current     
        return {'FINISHED'} # operator worked           


#WIRE ONLY TOGGLE             
class OBJECT_OT_wireOnly(bpy.types.Operator):
    #connecting this class to the button of the same name
    bl_idname = "object.wire_only"
    bl_label = "Wire Only"
    bl_description = "Toggle object draw type to Wire"
           
    #function that's executed when button is pushed
    def execute(self, context):
        allOb = bpy.context.scene.objects
        selOb = bpy.context.selected_objects
        meshes = list(bpy.data.meshes)
        
        if selOb:
            selMeshes = []
            for ob in selOb:
                if ob.type == "MESH":
                    selMeshes.append(ob)
                            
            if selMeshes[0].draw_type == "WIRE":
                toggle = 1
            else:
                toggle = 0
                     
            for ob in selMeshes:
                if toggle == 1:
                    ob.draw_type = "TEXTURED"
                if toggle == 0:
                    ob.draw_type = "WIRE"
                    
        return {'FINISHED'} # operator worked  
    

#ALL NAMES TOGGLE             
class OBJECT_OT_allNamesToggle(bpy.types.Operator):
    #connecting this class to the button of the same name
    bl_idname = "object.all_names_toggle"
    bl_label = "Object Names"
    bl_description = "Toggle object names for all objects in the viewport"
           
    #function that's executed when button is pushed
    def execute(self, context):
        listOb = list(bpy.data.objects)
        if listOb:        
            if listOb[0].show_name == True:
                toggle = 1
            else:
                toggle = 0
                     
            for ob in context.scene.objects:
                if toggle == 1:
                    ob.show_name = False
                if toggle == 0:
                    ob.show_name = True                    
                        
        return {'FINISHED'} # operator worked           
   
#ALL AXIS TOGGLE             
class OBJECT_OT_allAxisToggle(bpy.types.Operator):
    #connecting this class to the button of the same name
    bl_idname = "object.all_axis_toggle"
    bl_label = "Object Axis"
    bl_description = "Toggle local axises for all objects in the viewport"
           
    #function that's executed when button is pushed
    def execute(self, context):
        listOb = list(bpy.data.objects)
        if listOb:        
            if listOb[0].show_axis == True:
                toggle = 1
            else:
                toggle = 0
                     
            for ob in context.scene.objects:
                if toggle == 1:
                    ob.show_axis = False
                if toggle == 0:
                    ob.show_axis = True                    
                        
        return {'FINISHED'} # operator worked 
    
#ALL TRANSPARENCY TOGGLE             
class OBJECT_OT_allTransparencyToggle(bpy.types.Operator):
    #connecting this class to the button of the same name
    bl_idname = "object.all_transparent_toggle"
    bl_label = "Transparency"
    bl_description = "Toggle material transparency in viewport for all objects"
           
    #function that's executed when button is pushed
    def execute(self, context):
        listOb = list(bpy.data.objects)
        if listOb:        
            if listOb[0].show_transparent == True:
                toggle = 1
            else:
                toggle = 0
                     
            for ob in context.scene.objects:
                if toggle == 1:
                    ob.show_transparent = False
                if toggle == 0:
                    ob.show_transparent = True                    
                        
        return {'FINISHED'} # operator worked
    
    
#----------- LIMIT VISIBLE OPERATROS --------------

class OBJECT_OT_fvShowNone(bpy.types.Operator):
    bl_idname = "object.fv_show_none"
    bl_label = "None"
    bl_description = "Uncheck all Types"

    def execute(self, context):
        kt = bpy.context.window_manager.katietools
        
        kt.ob_fvMesh = False
        kt.ob_fvCurve = False
        kt.ob_fvSurf = False
        kt.ob_fvMeta = False
        kt.ob_fvFont = False
        kt.ob_fvArm = False
        kt.ob_fvLat = False
        kt.ob_fvEmpty = False
        kt.ob_fvCam = False
        kt.ob_fvLamp = False
        kt.ob_fvSpeak = False
                        
        return {'FINISHED'} # operator worked
    
    
class OBJECT_OT_fvShowAll(bpy.types.Operator):
    bl_idname = "object.fv_show_all"
    bl_label = "All"
    bl_description = "Check all Types"

    def execute(self, context):
        kt = bpy.context.window_manager.katietools
        
        kt.ob_fvMesh = True
        kt.ob_fvCurve = True
        kt.ob_fvSurf = True
        kt.ob_fvMeta = True
        kt.ob_fvFont = True
        kt.ob_fvArm = True
        kt.ob_fvLat = True
        kt.ob_fvEmpty = True
        kt.ob_fvCam = True
        kt.ob_fvLamp = True
        kt.ob_fvSpeak = True
                        
        return {'FINISHED'} # operator worked

class OBJECT_OT_fvStore(bpy.types.Operator):
    bl_idname = "object.fv_store"
    bl_label = "Store"
    bl_description = "Store currently visible objects"        

    def execute(self, context):
        kt = bpy.context.window_manager.katietools
        allOb = bpy.context.scene.objects
        visOb = []
        
        if len(kt.ob_fvStore) > 0:
            bpy.types.KatieToolsProps.ob_fvStore = []
        else:    
            for ob in allOb:
                if ob.hide == False:
                    visOb.append(ob)
    
            bpy.types.KatieToolsProps.ob_fvStore = visOb
        
        print (kt.ob_fvStore) 
    
        return {'FINISHED'} # operator worked 
                  
class OBJECT_OT_fvToggle(bpy.types.Operator):
    bl_idname = "object.fv_toggle"
    bl_label = "FV Toggle"
    bl_description = "Toggle for Limited Visibility"
    
    fvType = bpy.props.StringProperty()

    def execute(self, context):
        scn = bpy.context.scene
        kt = bpy.context.window_manager.katietools
        visOb = [] 
             
        if len(kt.ob_fvStore) > 0:
            visOb = kt.ob_fvStore
        else:
            visOb = bpy.context.scene.objects
                        
        if self.fvType == "MESH":
            if kt.fvMESH == True:
                kt.fvMESH = False
            else:
                kt.fvMESH = True
            for ob in visOb:
                if ob.type == self.fvType:
                    if kt.fvMESH == True:
                        ob.hide = False
                    else:
                        ob.hide = True            
  
        if self.fvType == "CURVE":
            if kt.fvCURVE == True:
                kt.fvCURVE = False
            else:
                kt.fvCURVE = True
            for ob in visOb:
                if ob.type == self.fvType:
                    if kt.fvCURVE == True:
                        ob.hide = False
                    else:
                        ob.hide = True
                        
        if self.fvType == "SURFACE":
            if kt.fvSURFACE == True:
                kt.fvSURFACE = False
            else:
                kt.fvSURFACE = True
            for ob in visOb:
                if ob.type == self.fvType:
                    if kt.fvSURFACE == True:
                        ob.hide = False
                    else:
                        ob.hide = True
                        
        if self.fvType == "META":
            if kt.fvMETA == True:
                kt.fvMETA = False
            else:
                kt.fvMETA = True
            for ob in visOb:
                if ob.type == self.fvType:
                    if kt.fvMETA == True:
                        ob.hide = False
                    else:
                        ob.hide = True
                        
        if self.fvType == "FONT":
            if kt.fvFONT == True:
                kt.fvFONT = False
            else:
                kt.fvFONT = True
            for ob in visOb:
                if ob.type == self.fvType:
                    if kt.fvFONT == True:
                        ob.hide = False
                    else:
                        ob.hide = True
                        
        if self.fvType == "ARMATURE":
            if kt.fvARMATURE == True:
                kt.fvARMATURE = False
            else:
                kt.fvARMATURE = True
            for ob in visOb:
                if ob.type == self.fvType:
                    if kt.fvARMATURE == True:
                        ob.hide = False
                    else:
                        ob.hide = True
                        
        if self.fvType == "LATTICE":
            if kt.fvLATTICE == True:
                kt.fvLATTICE = False
            else:
                kt.fvLATTICE = True
            for ob in visOb:
                if ob.type == self.fvType:
                    if kt.fvLATTICE == True:
                        ob.hide = False
                    else:
                        ob.hide = True
                        
        if self.fvType == "EMPTY":
            if kt.fvEMPTY == True:
                kt.fvEMPTY = False
            else:
                kt.fvEMPTY = True
            for ob in visOb:
                if ob.type == self.fvType:
                    if kt.fvEMPTY == True:
                        ob.hide = False
                    else:
                        ob.hide = True
                        
        if self.fvType == "CAMERA":
            if kt.fvCAMERA == True:
                kt.fvCAMERA = False
            else:
                kt.fvCAMERA = True
            for ob in visOb:
                if ob.type == self.fvType:
                    if kt.fvCAMERA == True:
                        ob.hide = False
                    else:
                        ob.hide = True
                        
        if self.fvType == "LAMP":
            if kt.fvLAMP == True:
                kt.fvLAMP = False
            else:
                kt.fvLAMP = True
            for ob in visOb:
                if ob.type == self.fvType:
                    if kt.fvLAMP == True:
                        ob.hide = False
                    else:
                        ob.hide = True
                        
        if self.fvType == "SPEAKER":
            if kt.fvSPEAKER == True:
                kt.fvSPEAKER = False
            else:
                kt.fvSPEAKER = True
            for ob in visOb:
                if ob.type == self.fvType:
                    if kt.fvSPEAKER == True:
                        ob.hide = False
                    else:
                        ob.hide = True
                
        return {'FINISHED'} # operator worked       
    

#----------- SMOOTHING OPERATORS --------------

#ADD SUBSURF    
class OBJECT_OT_modAddSubsurf(bpy.types.Operator):
    bl_idname = "object.mod_add_subsurf"
    bl_label = "ON"
    bl_description = "Add a subsurf modifier named 'MySubsurf' to all mesh objects"
    
    def execute(self, context):
        scn = bpy.context.scene
        selOb = bpy.context.selected_objects
        myModName = "MySubsurf"
        l = len(myModName)
        kt = bpy.context.window_manager.katietools
        hiPoly = []
        unsmoothOb = []
        for ob in scn.objects:
            if ob.unsmoothable == True:
                unsmoothOb.append(ob)
        
        if selOb:
            targetOb = selOb
        else:
            targetOb = scn.objects     
            
        for ob in targetOb:
            if ob.type == "MESH":
                if len(ob.data.polygons) < kt.subD_limit: #CHECK THE POLYCOUNT
                    if ob not in unsmoothOb: #CHECK TO MAKE SURE IT's NOT TAGGED UNSMOOTHABLE
                        if (myModName not in ob.modifiers):
                            m = ob.modifiers.new(myModName,'SUBSURF')
                            m.levels = kt.subD_val
                            m.render_levels = kt.subD_val_ren
                            m.show_on_cage = True
                            m.show_only_control_edges = True
                else:
                    hiPoly.append(ob.name)
        
        if len(hiPoly) != 0 and len(unsmoothOb) != 0:
            self.report({'INFO'}, "Some hi-poly and usnmoothable objects were not smoothed")
        elif len(unsmoothOb) != 0:
            self.report({'INFO'}, "Some usnmoothable objects were not smoothed")
        elif len(hiPoly) != 0:
            self.report({'INFO'}, "Some hi-poly bjects were not smoothed")    
            
            print ("OBJECTS NOT SMOOTHED:  " + str(hiPoly))
                    
        # Silly way to force all windows to refresh
        bpy.context.scene.frame_current = bpy.context.scene.frame_current

        return {'FINISHED'}

#REMOVE SUBSURF
class OBJECT_OT_modRemoveSubsurf(bpy.types.Operator):
    bl_idname = "object.mod_remove_subsurf"
    bl_label = "OFF"
    bl_description = "Remove the 'MySubsurf' from all mesh objects"
    
    def execute(self, context):
        scn = bpy.context.scene
        selOb = bpy.context.selected_objects
        myModName = "MySubsurf"
        l = len (myModName)
        
        if selOb:
            targetOb = selOb
        else:
            targetOb = scn.objects     
            
        for ob in targetOb:
            if ob.type == "MESH":
                for mod in ob.modifiers:
                    if myModName == mod.name[:l]:
                        ob.modifiers.remove(mod)

        bpy.context.scene.frame_current = bpy.context.scene.frame_current
        
        return {'FINISHED'}


#TAG UNSMOOTHABLE
class OBJECT_OT_tagUnsmoothable(bpy.types.Operator):
    bl_idname = "object.tag_unsmooth"
    bl_label = "Tag Unsmoothable"
    bl_description = "Tag selected objects as not smoothable"
    
    #NOTE: Currently the 'unsmoothable' tag is remembered in window manager.
    #Might be smart to add this to 'scene' instead
    
    def execute(self, context):
        selOb = bpy.context.selected_objects
        
        if selOb:
            for ob in selOb:
                ob.unsmoothable = True  
        
        return {'FINISHED'}
    
class OBJECT_OT_selectUnsmoothable(bpy.types.Operator):
    bl_idname = "object.select_unsmooth"
    bl_label = "Select Unsmoothable"
    bl_description = "Select objects tagged as not smoothable"
    
    def execute(self, context):
        scn = bpy.context.scene
        unsmoothOb = []
        
        for ob in scn.objects:
            if ob.unsmoothable == True:
                unsmoothOb.append(ob)
                
        if len(unsmoothOb) == 0:
            self.report({'INFO'}, "No objects tagged as non smoothable")
        else:
            for ob in scn.objects:
                if ob in unsmoothOb:
                    ob.select = True
                else:
                    ob.select = False
                    
            scn.objects.active = unsmoothOb[0]              
            
        
        return {'FINISHED'}
    
class OBJECT_OT_clearUnsmoothable(bpy.types.Operator):
    bl_idname = "object.clear_unsmooth"
    bl_label = "Clear Unsmoothable"
    bl_description = "Clear unsmoothable tag from all or selected objects"
    
    def execute(self, context):
        scn = bpy.context.scene
        selOb = bpy.context.selected_objects
        unsmoothOb = []
        
        for ob in scn.objects:
            if ob.unsmoothable == True:
                unsmoothOb.append(ob)
        
        if selOb:
            for ob in selOb:
                if ob in unsmoothOb:
                    ob.unsmoothable = False
        else:
            for ob in scn.objects:
                if ob in unsmoothOb:
                    ob.unsmoothable = False
        
        return {'FINISHED'}