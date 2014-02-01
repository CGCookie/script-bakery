import bpy
import os
import random
import math

#--------------------------------------------------------------------------
#-----------------------------MATERIAL OPERATORS --------------------------
#--------------------------------------------------------------------------

class OBJECT_OT_createColorMats(bpy.types.Operator):
    bl_idname = "material.create_color_mats"
    bl_label = "Create Colors"
    bl_description = "Create basic color materials"
    
    def execute (self, context):
        kt = bpy.context.window_manager.katietools
        mats = bpy.data.materials
            
        #red
        if ("KTc_RED" not in mats):
            red = bpy.data.materials.new('KTc_RED')
            red.diffuse_color = (1, .25, .25)
            red.specular_intensity = 0
            red.use_fake_user = True
        else:
            print ("RED exists")    
        
        #orange
        if ("KTc_ORANGE" not in mats):
            orange = bpy.data.materials.new('KTc_ORANGE')
            orange.diffuse_color = (1, .375, .155)
            orange.specular_intensity = 0
            orange.use_fake_user = True
        else:
            print ("ORANGE exists")    
        
        #yellow
        if ("KTc_YELLOW" not in mats):
            yellow = bpy.data.materials.new('KTc_YELLOW')
            yellow.diffuse_color = (1, 1, .25)
            yellow.specular_intensity = 0
            yellow.use_fake_user = True
        else:
            print ("YELLOW exists")     
        
        #green
        if ("KTc_GREEN" not in mats):
            green = bpy.data.materials.new('KTc_GREEN')
            green.diffuse_color = (0.25, 1, 0.25)
            green.specular_intensity = 0
            green.use_fake_user = True
        else:
            print ("GREEN exists")    
        
        #cyan
        if ("KTc_CYAN" not in mats):
            cyan = bpy.data.materials.new('KTc_CYAN')
            cyan.diffuse_color = (0.25, 1, 1)
            cyan.specular_intensity = 0
            cyan.use_fake_user = True
        else:
            print ("CYAN exists")
        
        #blue
        if ("KTc_BLUE" not in mats):
            blue = bpy.data.materials.new('KTc_BLUE')
            blue.diffuse_color = (0.25, .25, 1)
            blue.specular_intensity = 0
            blue.use_fake_user = True
        else:
            print ("BLUE exists")
        
        #purple
        if ("KTc_PURPLE" not in mats):
            purple = bpy.data.materials.new('KTc_PURPLE')
            purple.diffuse_color = (0.65, .25, 1)
            purple.specular_intensity = 0
            purple.use_fake_user = True
        else:
            print ("PURPLE exists")
        
        #brown
        if ("KTc_BROWN" not in mats):
            brown = bpy.data.materials.new('KTc_BROWN')
            brown.diffuse_color = (0.16, .1, .06)
            brown.specular_intensity = 0
            brown.use_fake_user = True
        else:
            print ("BROWN exists")
        
        #black
        if ("KTc_BLACK" not in mats):
            black = bpy.data.materials.new('KTc_BLACK')
            black.diffuse_color = (.05, .05, .05)
            black.specular_intensity = 0
            black.use_fake_user = True
        else:
            print ("BLACK exists")
        
        #white
        if ("KTc_WHITE" not in mats):
            white = bpy.data.materials.new('KTc_WHITE')
            white.diffuse_color = (.9, .9, .9)
            white.specular_intensity = 0
            white.use_fake_user = True
        else:
            print ("WHITE exists")
        
        #skin
        if ("KTc_SKIN" not in mats):
            skin = bpy.data.materials.new('KTc_SKIN')
            skin.diffuse_color = (1, .55, .435)
            skin.specular_intensity = 0
            skin.use_fake_user = True        
        else:
            print ("SKIN exists")
        
        #grey
        if ("KTc_GREY" not in mats):
            grey = bpy.data.materials.new('KTc_GREY')
            grey.diffuse_color = (.8, .8, .8)
            grey.specular_intensity = 0
            grey.use_fake_user = True
        else:
            print ("GREY exists")
        
        kt.mat_colors_exist = True
        
        return {'FINISHED'} 
  
    
class OBJECT_OT_matAssigner(bpy.types.Operator):
    bl_idname = "material.assign_mat"
    bl_label = "Assign Color"
    bl_description = "Assign color material to selected objects"

    def execute(self, context):
        kt = bpy.context.window_manager.katietools
        scn = bpy.context.scene
        selOb = bpy.context.selected_objects
        
        for ob in selOb:
            if kt.mat_color != 'RANDOM':
                ob.active_material_index = 0
                ob.active_material = bpy.data.materials['KTc_' + kt.mat_color]
            elif kt.mat_color == 'RANDOM':
                ran = random.randint(0, 10)
                colors = ['KTc_RED',
                          'KTc_ORANGE',
                          'KTc_YELLOW',
                          'KTc_GREEN',
                          'KTc_CYAN',
                          'KTc_BLUE',
                          'KTc_PURPLE',
                          'KTc_BROWN',
                          'KTc_BLACK',
                          'KTc_WHITE',
                          'KTc_SKIN']
       
                ranColor = colors[ran]
                ob.active_material = bpy.data.materials[ranColor] 
            
        scn.render.engine = 'BLENDER_RENDER'
        scn.game_settings.material_mode = 'MULTITEXTURE'
        
        areas = bpy.context.screen.areas
        for area in areas:
            if area.type == 'VIEW_3D':
                if area.spaces.active.viewport_shade != 'SOLID':
                    area.spaces.active.viewport_shade='SOLID'
                        
           
        return {'FINISHED'} 
    
                      
class OBJECT_OT_matSpecToggle(bpy.types.Operator):
    bl_idname = "object.mat_spec_toggle"
    bl_label = "Specular"
    bl_description = "Toggle specular value for basic color materials"
    
    def execute(self, context):
        materials = bpy.data.materials
        if ('KTc_RED' in materials):
            if materials['KTc_RED'].specular_intensity == 0:
                sToggle = 0
            else:
                sToggle = 1
                    
            if sToggle == 0:
                materials['KTc_RED'].specular_intensity = 0.5
                materials['KTc_ORANGE'].specular_intensity = 0.5
                materials['KTc_YELLOW'].specular_intensity = 0.5
                materials['KTc_GREEN'].specular_intensity = 0.5
                materials['KTc_CYAN'].specular_intensity = 0.5
                materials['KTc_BLUE'].specular_intensity = 0.5
                materials['KTc_PURPLE'].specular_intensity = 0.5
                materials['KTc_BROWN'].specular_intensity = 0.5
                materials['KTc_BLACK'].specular_intensity = 0.5
                materials['KTc_WHITE'].specular_intensity = 0.5
                materials['KTc_GREY'].specular_intensity = 0.5
                materials['KTc_SKIN'].specular_intensity = 0.5
                
            elif sToggle == 1:
                materials['KTc_RED'].specular_intensity = 0
                materials['KTc_ORANGE'].specular_intensity = 0
                materials['KTc_YELLOW'].specular_intensity = 0
                materials['KTc_GREEN'].specular_intensity = 0
                materials['KTc_CYAN'].specular_intensity = 0
                materials['KTc_BLUE'].specular_intensity = 0
                materials['KTc_PURPLE'].specular_intensity = 0
                materials['KTc_BROWN'].specular_intensity = 0
                materials['KTc_BLACK'].specular_intensity = 0
                materials['KTc_WHITE'].specular_intensity = 0
                materials['KTc_GREY'].specular_intensity = 0
                materials['KTc_SKIN'].specular_intensity = 0 
        else:
            self.report({'INFO'}, "Color materials have not been created yet")           
        
        return {'FINISHED'}
    

    
def importMatcapImages(context):
    
    ext_list = ['jpg','bmp','iris','png','jpeg','targa','tga']
        
    kt = bpy.context.window_manager.katietools
    path = bpy.utils.script_paths('addons/katietools/matcap_img')
    pathStr = ''.join(path) #convert list object to string
    files = list(os.listdir(pathStr))
    
    imported = []
    
    for file in files:
        
        if file.split('.')[-1].lower() in ext_list:
            
            #import image files in dir as blender images
            texName = 'KTmc_' + file.split('.')[0]
            imgPath = pathStr + "\\" + file
            base = file.split('.')[0]
            enumItems = (base, base,'MatCap name')
            
            if (texName not in bpy.data.materials):
                                           
                newTex = bpy.data.textures.new(texName, 'IMAGE')
                
                image = bpy.data.images.load(imgPath)
                image.source = "FILE"
                image.filepath = imgPath
                bpy.data.textures[newTex.name].image = image
                
                #create matcaps
                matName = texName       
                mat = bpy.data.materials.new(matName)
                mat.use_nodes = True
                mat.use_fake_user = True
                
                tree = bpy.data.materials[matName].node_tree
                links = tree.links
                
                geo = tree.nodes.new('ShaderNodeGeometry')
                geo.name = 'KTmc_Geometry'
                geo.location = -200,0
                
                map = tree.nodes.new('ShaderNodeMapping')
                map.name = 'KTmc_Mapping'
                map.scale = (1.0,-1.0,1.0)
                links.new(geo.outputs[5],map.inputs[0])
                
                tex = tree.nodes.new('ShaderNodeTexture')
                tex.name = 'KTmc_Texture'
                tex.location = 300,0
                tex.texture = bpy.data.textures[texName]
                links.new(map.outputs[0],tex.inputs[0])
                
                '''curve = tree.nodes.new('ShaderNodeRGBCurve') #RGB Curve node for texture color space 'correction'
                curve.name = 'KTmc_CurveRGB'
                curve.location = 500,0
                cCurve = curve.mapping.curves[3] #the 'C' curve is first in the UI but last in the code
                cCurve.points.new(position=1, value=0.5) #what are the 'position' and 'value' parameters?!
                cCurve.points.new(position=2, value=0.5)
                cCurve.points[1].location = [0.2, 0.06]
                cCurve.points[2].location = [0.8, 0.9]
                cCurve.points[3].location = [1, 1]
                links.new(tex.outputs[1],curve.inputs[1])'''
                
                out = tree.nodes['Output'] #note this node already exists; different syntax
                out.name = 'KTmc_Output'
                out.location = 800,0
                links.new(tex.outputs[1],out.inputs[0])
                
                matNode = tree.nodes['Material']
                tree.nodes.remove(matNode)
                
                kt.mat_matcaps_exist = True
                
            else:
                kt.mat_matcaps_exist = True
                print ('MatCap ' + texName + ' already created')
                
            imported.append(enumItems)               

    def register():
        bpy.types.KatieToolsProps.mat_matcap = bpy.props.EnumProperty(name='Matcap',items=imported)
    
    register()
    
    
class OBJECT_OT_createMatCaps(bpy.types.Operator):
    bl_idname = "object.create_matcaps"
    bl_label = "Create MatCaps"
    bl_description = "Creates MatCap materials based on preset images" 
       
    def execute(self, context):
        scn = bpy.context.scene
        engine = scn.render.engine
        
        if engine !="BLENDER_RENDER":
            bpy.context.scene.render.engine = "BLENDER_RENDER"
          
        importMatcapImages(context)
        
        scn.render.engine = engine     
        
        return {'FINISHED'}
    
class OBJECT_OT_refreshMatCap(bpy.types.Operator):
    bl_idname = "object.refresh_matcap"
    bl_label = "Refresh Matcaps"
    bl_description = "Refresh Matcap list"
    
    def execute(self, context): 
          
        importMatcapImages(context)        
        
        return {'FINISHED'}   
    
    
class OBJECT_OT_matCapAssigner(bpy.types.Operator):
    bl_idname = "object.assign_matcap"
    bl_label = "Assign Matcap"
    bl_description = "Assign MatCap material to selected objects"
    
    def execute(self, context):
        selOb = bpy.context.selected_objects
        scn = bpy.context.scene
        kt = bpy.context.window_manager.katietools
        game = bpy.types.SceneGameData
        view = bpy.types.SpaceView3D
        selMatCap = kt.mat_matcap
        
        for ob in selOb:
            ob.active_material_index = 0
            ob.active_material = bpy.data.materials['KTmc_' + selMatCap]
            
        scn.render.engine = 'BLENDER_RENDER'
        scn.game_settings.material_mode = 'GLSL'
        
        areas = bpy.context.screen.areas
        for area in areas:
            if area.type == 'VIEW_3D':
                if area.spaces.active.viewport_shade != 'TEXTURED':
                    area.spaces.active.viewport_shade='TEXTURED'
        
        return {'FINISHED'}
    

    
class OBJECT_OT_selectByMat(bpy.types.Operator):
    bl_idname = "object.select_by_mat"
    bl_label = "Select By Mat"
    bl_description = "Select objects with the same active material as the as active object"
    
    def execute(self, context):
        actOb = bpy.context.active_object
        scnOb = bpy.context.scene.objects
        actMat = actOb.active_material
        
        for ob in scnOb:
            if ob.active_material == actMat:
                ob.select = True                         
                
        return {'FINISHED'}
        
    
    
class OBJECT_OT_matClear(bpy.types.Operator):
    bl_idname = "object.clear_mats"
    bl_label = "Clear Created"
    bl_description = "Clear materials created here"
    
    def clearMats(self):
        allOb = bpy.data.objects
        scn = bpy.context.scene
        game = bpy.types.SceneGameData
        view = bpy.types.SpaceView3D
        
        for ob in allOb:
            if ob.type == 'MESH':
                scn.objects.active = ob
                matSlots = list(ob.material_slots)
                msNames = []
                for ms in matSlots:
                    msNames.append(ms.name)
                mi = (i for i,x in enumerate(msNames) if ('KTc' in x) or ('KTmc' in x))
                for i in mi:
                    ob.active_material_index = i
                    bpy.ops.object.material_slot_remove()         
        
        #fix display settings    
        scn.render.engine = 'BLENDER_RENDER'
        scn.game_settings.material_mode = 'MULTITEXTURE'
        
        areas = bpy.context.screen.areas
        for area in areas:
            if area.type == 'VIEW_3D':
                if area.spaces.active.viewport_shade != 'SOLID':
                    area.spaces.active.viewport_shade='SOLID'                               
    
    def execute(self, context):
        mats = bpy.data.materials
        scn = bpy.context.scene
        kt = bpy.context.window_manager.katietools
        
        self.clearMats()
        
        for mat in mats:
            if ("KTmc_" in mat.name) or ("KTc_" in mat.name):
                mat.use_fake_user = False
                bpy.data.materials.remove(mat)
            
        self.report({'INFO'}, "Colors and MatCaps deleted")              
                          
        # Hack: Force update of material slot view
        scn.frame_set(scn.frame_current)
        kt.mat_matcaps_exist = False
        kt.mat_colors_exist = False        
        
        return {'FINISHED'}
    

class OBJECT_OT_matLinkSwitch(bpy.types.Operator):
    bl_idname = "object.mat_link_switch"
    bl_label = "Link Switch"
    bl_description = "Toggle all material slot links from OBJECT DATA to OBJECT, and vice versa"
    
    def execute(self, context):
        selOb = bpy.context.selected_objects
        actOb = bpy.context.active_object
        allOb = bpy.data.objects
        scn = bpy.context.scene
        
        obWithMat = []
        
        for ob in allOb:
            if ob.type == 'MESH' or ob.type == 'CURVE' or ob.type == 'SURFACE' or ob.type == 'META' or ob.type == 'FONT':
                if len(ob.material_slots) >= 1:
                    obWithMat.append(ob)
        
        if len(obWithMat) >= 1:                                 #if there is at least 1 object in array  
            firstObSlots = obWithMat[0].material_slots          #the first object's material slots
            for slot in firstObSlots:
                if slot == firstObSlots[0]:
                    if slot.link == 'DATA':
                        toggle = 0
                    elif slot.link == 'OBJECT':
                        toggle = 1
                        
            for ob in obWithMat:
                scn.objects.active = ob
        
                matSlots = list(ob.material_slots)
                matArray = []
                
                for slot in matSlots:
                    num = matSlots.index(slot)
                    matArray.append(slot.material)
                    
                    if toggle == 0:   
                        slot.link = "OBJECT"
                        self.report({'INFO'}, "All Links set to OBJECT")
                    elif toggle == 1:
                        slot.link = "DATA"
                        self.report({'INFO'}, "All Links set to DATA")
                    elif toggle == None:
                        self.report({'INFO'}, "No Toggle value")    
                            
                    slot.material = matArray[num]            
        else:
            self.report({'INFO'}, "No objects have material slots")
            
        scn.objects.active = actOb                   
        
        return {'FINISHED'}       
