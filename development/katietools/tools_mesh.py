import bpy
import os
import random
import math
import time
from operator import itemgetter

#--------------------------------------------------------------------------
#----------------------------- MESH OPERATORS -----------------------------
#--------------------------------------------------------------------------


class OBJECT_OT_calcTotalEdgeLength(bpy.types.Operator):
    bl_idname = "mesh.calc_total_edge_length"
    bl_label = "Calculate Total Edge Length"
    bl_description = "Calculates the total length of selected edges"
    
    def execute (self, context):
        actOb = bpy.context.active_object  
        edgeLength = 0
        edgeList = []
        
        for e in actOb.data.edges:
            if e.select == True:
                edgeList.append(e)
        
        for edge in edgeList:
            v1 = edge.vertices[0]
            v2 = edge.vertices[1]
            co1 = actOb.data.vertices[v1].co
            co2 = actOb.data.vertices[v2].co
            edgeLength += (co1-co2).length
            
        self.report({'INFO'}, "Total Edge Length:" + str("%.2f" % edgeLength))   
                  
              
        return {'FINISHED'}
    

#----------------------------- COPY VERTEX ORDER BY UVs by NUKEngine -----------------------------
    
#globals:
EPSILON = 0.000001
#EPSILON = 0.0001
#EPSILON = 0.001
isBMesh = False


#handle blender 2.62 and bmesh transparently
def faces(mesh):
    if isBMesh:
        return mesh.polygons
    else:
        return mesh.faces

def uvs(mesh, f, F):
    if isBMesh:
        uv_loops = mesh.uv_layers.active.data
        lstart = lend = F.loop_start
        lend += F.loop_total
        return [uv.uv for uv in uv_loops[lstart:lend]]
    else:
        return mesh.uv_textures.active.data[f].uv

def buildVertToFaceMap(mesh):
    VertexFaces = {}
    for fid, F in enumerate(faces(mesh)):
        for v in F.vertices:
            if not v in VertexFaces :
                VertexFaces[v] = []
            VertexFaces[v].append(fid)
    return VertexFaces

def buildDegreeOccuranceHeap(mesh, VertexFaces):
    degreeMap = {}
    for idx, f in VertexFaces.items():
        degree = len(f)
        if not degree in degreeMap:
            degreeMap[degree] = []
        degreeMap[degree].append(idx)
    occursHeap = []
    for degree, vList in degreeMap.items():
        occursHeap.append((len(vList), degree, vList))
    occursHeap = sorted(occursHeap, key=itemgetter(0,1))
    return occursHeap

    
    
def findMatchingVertsByUv(mesh1, v1, f1, mesh2, v2, f2, uvcache1, uvcache2):
    res = {}
    F1 = faces(mesh1)[f1]
    F2 = faces(mesh2)[f2]
    
    if len(F1.vertices) != len(F2.vertices):
        return {}
    
    if f1 in uvcache1:
        uvs1 = uvcache1[f1]
    else:
        uvs1 = uvs(mesh1, f1, F1)
        uvcache1[f1] = uvs1
        
    if f2 in uvcache2:
        uvs2 = uvcache2[f2]
    else:
        uvs2 = uvs(mesh2, f2, F2)
        uvcache2[f2] = uvs2
    
    if len(uvs1) != len(uvs2):
        return {}
    
    vidx1 = -1
    for idx1, vi1 in enumerate(F1.vertices):
        if v1 == vi1:
            vidx1 = idx1
            break
    vidx2 = -1
    for idx2, vi2 in enumerate(F2.vertices):
        if v2 == vi2:
            vidx2 = idx2
            break
    
    numVerts = len(F1.vertices)
    ok = True
    #print("DEBUG START************************** v: %i vs %i, f: %i vs %i" % (v1,v2, f1, f2))
    for i in range(numVerts):
        newIdx1 = (i + vidx1) % numVerts
        newIdx2 = (i + vidx2) % numVerts
        if abs(uvs1[newIdx1][0] - uvs2[newIdx2][0]) > EPSILON or abs(uvs1[newIdx1][1] - uvs2[newIdx2][1]) > EPSILON:
            ok = False
            #print("DEBUG: no match (newIdx1=%i, newIdx2=%i), conflict [%f, %f] vs. [%f, %f]" %(newIdx1, newIdx2, uvs1[newIdx1][0], uvs1[newIdx1][1], uvs2[newIdx2][0], uvs2[newIdx2][1]))
            # uvs = []
            # for x in mesh2.uv_textures.active.data[f2].uv:
                # uvs.append([x[0], x[1]])
            # print("DEBUG uvs of failed match %i: %s" % (f2, str(uvs)))
            break
        else:
            res[F1.vertices[newIdx1]] = F2.vertices[newIdx2]
            #print("DEBUG: match %i, %i with uvs %f, %f to %f, %f" % (F1.vertices[newIdx1], F2.vertices[newIdx2], uvs1[newIdx1][0], uvs1[newIdx1][1], uvs2[newIdx2][0], uvs2[newIdx2][1]))
    
    #print("DEBUG END  ************************** v1=%i v2=%i : %s" % (v1,v2, str(ok)))    
    if (ok):
        return res
    else:
        return {}
    
    
    
def mapByUv(mesh1, mesh2, vList1, vList2, VertexFaces1, VertexFaces2, uvcache1, uvcache2, mapping, invmapping, newMaps):
        refound = []
        for v1 in vList1:
                for f1 in VertexFaces1[v1]:
                    match = False
                    for v2 in vList2:
                        for f2 in VertexFaces2[v2]:
                            #if mesh1.vertics[v1]. not v1 in mapping
                            submatch = findMatchingVertsByUv(mesh1, v1, f1, mesh2, v2, f2, uvcache1, uvcache2)
                            if submatch:
                                #print("found submatch v1=%i v2=%i: map=%s" % (v1, v2, str(submatch)))
                                #mapping[v1] = v2
                                for v1x, v2x in submatch.items():
                                    if v1x in mapping:
                                        if mapping[v1x] != v2x:
                                            print("ERROR: found different mapping for vertex")
                                            print("original mapping %i,%i, new mapping %i,%i" % (v1x, mapping[v1x], v1x, v2x))
                                            raise Exception("ERROR: found different mapping for vertex")
                                        else:
                                            #print("DEBUG: refound mapping: v: %i,%i,  f: %i,%i" % (v1x, v2x, f1, f2))
                                            #FIXME: check: tricky bug if missing???
                                            #newMaps.append(v1x, v2x, f1, f2)
                                            refound.append((v1x, v2x, f1, f2))
                                    else:
                                        mapping[v1x] = v2x
                                        invmapping[v2x] = v1x
                                        newMaps.append((v1x, v2x, f1, f2))
                                        #print("DEBUG: found mapping: v: %i,%i,  f: %i,%i" % (v1x, v2x, f1, f2))
                                match = True
                    if not match:
                        print("ERROR: no match for face found:", f1)
                        uvsFail = []
                        for x in uvs(mesh1, f1, faces(mesh1)[f1]):
                            uvsFail.append([x[0], x[1]])
                        print("UVs mesh1 of face %i: %s" % (f1, str(uvsFail)))
                        for v2 in vList2:
                            for f2 in VertexFaces2[v2]:
                                uvsFail = []
                                for x in uvs(mesh2, f2, faces(mesh2)[f2]):
                                    uvsFail.append([x[0], x[1]])
                                print("UVs mesh2 of face %i: %s" % (f2, str(uvsFail)))
                        raise Exception("ERROR: no match for face found:", f1)
        #try to reduce data size
        #all faces found if here
        for vnew1, vnew2, f1, f2 in newMaps:
            #fixme: fix code that method is not called in this case
            if f1 in VertexFaces1[vnew1]:
                VertexFaces1[vnew1].remove(f1)
                VertexFaces2[vnew2].remove(f2)
                
        for vnew1, vnew2, f1, f2 in refound:
            #fixme: fix code that method is not called in this case
            if f1 in VertexFaces1[vnew1]:
                VertexFaces1[vnew1].remove(f1)
                VertexFaces2[vnew2].remove(f2)
                

#Algorithm:
#build min-heap of vertex lists by number of occurance of a certain vertex degree in the mesh (degree as number of faces containing a vertex)
#first step of the loop: map verts, candidate set is all unmapped verts with degree X [ aka map(pop(minheap)) ]
#second step of loop: loop: expand mappings found in step one: candidate set is all unmapped verts of all unmapped faces of a vertex that was mapped in step one or two.
def object_copy_indices (self, context):
    startTime = time.time()
    #create a copy of mesh1 (active), but with vertex order of mesh2 (selected)
    obj1 = bpy.context.active_object
    selected_objs = bpy.context.selected_objects[:]
    
    
    if not obj1 or len(selected_objs) != 2 or obj1.type != "MESH":
        raise Exception("Exactly two meshes must be selected. This Addon copies vertex order from mesh1 to copy of mesh2")
    
    selected_objs.remove(obj1)
    obj2 = selected_objs[0]
    
    if obj2.type != "MESH":
        raise Exception("Exactly two meshes must be selected. This Addon copies vertex order from mesh1 to copy of mesh2")
    
    
    mesh1 = obj1.data
    mesh2 = obj2.data
    
    #ugly block, but fast to implement
    global isBMesh
    try:
        face = mesh1.polygons
        print("is BMesh")
        isBMesh = True
    except:
        print("is not BMesh")
        face = mesh1.faces
        isBMesh = False
    if isBMesh:
        # be sure that both are bmesh, otherwise crash (should not be possible or I understand something wrong)
        face = mesh2.polygons
    
    if not mesh1.uv_textures or len(mesh1.uv_textures) == 0 or not mesh2.uv_textures or len(mesh2.uv_textures) == 0:
        raise Exception("Both meshes must have a uv mapping. This operator even assumes matching uv mapping!")
    if len(mesh1.vertices) != len(mesh2.vertices):
        raise Exception("Both meshes must have the same number of vertices. But it is %i:%i" % (len(mesh1.vertices), len(mesh2.vertices)))
    
    #FIXME: faces seem invalid later, or is there another bug? so we use face indices for now and look them up on use
    VertexFaces1 = buildVertToFaceMap(mesh1)
    VertexFaces2 = buildVertToFaceMap(mesh2)
    degreeHeap1 = buildDegreeOccuranceHeap(mesh1, VertexFaces1)
    degreeHeap2 = buildDegreeOccuranceHeap(mesh2, VertexFaces2)

    uvcache1 = {}
    uvcache2 = {}
    
    mapping = {}
    invmapping = {}
    passes = 0
    
    print("Trying to find initial mapping of all vertices with that degree (num faces) that occurs the fewest in the mesh")
    while len(mapping) < len(mesh1.vertices) and len(degreeHeap1) > 0:
        num1, degree1, vList1 = degreeHeap1.pop(0)
        num2, degree2, vList2 = degreeHeap2.pop(0)
        newMaps = []
        if num1 == num2 and degree1 == degree2 and len(vList1) == len(vList2):
            print("DEBUG: Looking at %i verts with degree %i" % (len(vList1), degree1))
            #remove all known from vlists (TODO: optimize)
            tmpList = []
            for vxx in vList1:
                if not vxx in mapping:
                    tmpList.append(vxx)
            vList1 = tmpList
            tmpList = []
            for vxx in vList2:
                if not vxx in invmapping:
                    tmpList.append(vxx)
            vList2 = tmpList
            
            print("DEBUG: relevant of those %i in mesh1 and %i in mesh2" % (len(vList1), len(vList2)))
            #first step of the loop: map verts, candidate set is all verts with degree X (degree as number of faces containing a vertex)
            mapByUv(mesh1, mesh2, vList1, vList2, VertexFaces1, VertexFaces2, uvcache1, uvcache2, mapping, invmapping, newMaps)
            passes += 1
            #expand over all neighbours of newly known vertex mappings
            #second step of loop: loop: expand mappings found in step one (or in this step)
            while len(newMaps) > 0:
                #print("DEBUG: handling newMaps: %s" % str(newMaps))
                newerMaps = []
                for vnew1, vnew2, f1, f2 in newMaps:
                    newFs1 = VertexFaces1[vnew1]
                    newFs2 = VertexFaces2[vnew2]
                    if newFs1 and newFs2:
                        vList1 = []
                        vList2 = []
                        for fx1 in newFs1:
                            for vx1 in faces(mesh1)[fx1].vertices:
                                if not vx1 in mapping:
                                    vList1.append(vx1)
                        for fx2 in newFs2:
                            for vx2 in faces(mesh2)[fx2].vertices:
                                if not vx2 in invmapping:
                                    vList2.append(vx2)
                        if vList1 and vList2:
                            tmpMap = []
                            #print("DEBUG: calling mapByUv to extend known mappings")
                            #candidate set is all verts of all faces (without already mapped faces) of a vertex that was mapped in step one or two
                            mapByUv(mesh1, mesh2, vList1, vList2, VertexFaces1, VertexFaces2, uvcache1, uvcache2, mapping, invmapping, tmpMap)
                            newerMaps = newerMaps + tmpMap
                            passes += 1
                            if passes % 500 == 0:
                                print("after %i extension runs of mapByUv (%s seconds) we have %i mappings." % (passes, str(time.time()-startTime),len(mapping)))
                                print("current newMaps size:", len(newMaps))
                newMaps = newerMaps
        else:
            print("ERROR: the meshes have a different topology.")
            raise Exception("ERROR: the meshes have a different topology.")
        print("DEBUG: ran %i executions of mapByUv to extend mapping" % passes)
        print("DEBUG: mappingsize=%i, verts=%i" % (len(mapping), len(mesh1.vertices)))
        if len(mapping) < 50:
            print("Mapping so far: %s" % (str(mapping)))

    if len(mapping) == len(mesh1.vertices):
        verts_pos=[]
        faces_indices=[]
        print("Found complete mapping")
        for v in mesh2.vertices:
            verts_pos.append(mesh1.vertices[invmapping[v.index]].co)
        
        for f in faces(mesh2):
            vs=[]
            for v in f.vertices:
                vs.append(v)
            faces_indices.append(vs)
        
        #create new mesh
        me=bpy.data.meshes.new("%s_v_order_%s" % (mesh1.name, mesh2.name))
        ob=bpy.data.objects.new("%s_v_order_%s" % (obj1.name, obj2.name) ,me)           
                 
        me.from_pydata(verts_pos, [], faces_indices)
        
        ob.matrix_world = obj1.matrix_world
        
        bpy.context.scene.objects.link(ob)
        me.update()
        print("New Object created. object=%s, mesh=%s in %s seconds" % (ob.name, me.name, str(time.time()-startTime)))
    else:
        print("ERROR: Process failed, did not find a mapping for all vertices")
        raise Exception("ERROR: Process failed, did not find a mapping for all vertices")    


class OBJECT_OT_copyVertIndices(bpy.types.Operator):
    bl_idname = "object.copy_vertex_order_by_uvs"
    bl_label = "Copy Vertex Order by UVs"
    bl_description = "Copy vertex order from mesh1 to a copy of mesh2.  CREDIT to NUKEngine"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        object_copy_indices(self, context)
 
        return {'FINISHED'}
    

#--------------------- APPLY SHAPEKEYS ----------------------------------

class OBJECT_OT_shapeKeyApply(bpy.types.Operator):
    bl_idname = "data.shapekey_apply"
    bl_label = "Apply Shapekeys"
    bl_description = "Applies current shape state and removes shapekeys for all or selected mesh objects"
    bl_options = {"UNDO"}
    
    def execute(self, context):
        scn = bpy.context.scene
        scnOb = scn.objects
        selOb = bpy.context.selected_objects
        actObName = bpy.context.active_object.name
        applicables = []
        
        if selOb:
            for ob in selOb:
                if ob.type == "MESH":
                    if ob.data.shape_keys != None:
                        applicables.append(ob.name)
                        scnOb.active = ob
                        name = ob.name
                        shapeKeys = ob.data.shape_keys.key_blocks
                                     
                        bpy.ops.object.select_all(action='DESELECT') # CRUCIAL TO WORKING
                        ob.select = True
                        bpy.ops.object.duplicate()
                        
                        actOb = bpy.context.active_object
                        actOb.name = "TEMP_" + name #duplicated TEMP object
                        actOb.select = True
                        ob.select = True
                        scn.objects.active = ob #original object duplicated and selection setup for join_shapes
                        
                        
                        for i in reversed(range(len(shapeKeys))):
                            ob.active_shape_key_index = i
                            bpy.ops.object.shape_key_remove() #shapekeys removed backwards to Basis on original object
                                        
                        bpy.ops.object.join_shapes()
                        
                        for i in range(len(shapeKeys)):
                            ob.active_shape_key_index = i
                            bpy.ops.object.shape_key_remove() #shapekeys forwards leaving the shape baked into the original object
                            ob.active_shape_key_index = i
                            bpy.ops.object.shape_key_remove() #HAD TO ADD THESE LINES TWICE FOR 2.64 (?!)
                            
                        ob.select = False
                        
                        bpy.ops.object.delete() #delete TEMP object
                    
            for ob in selOb:    
                ob.select = True
                
            scnOb.active = scnOb[actObName]
            
            count = str(len(applicables))
            self.report({'INFO'}, count + " objects with shapekeys have been applied")
        else:        
            self.report({'INFO'}, "No objects selected")      
        
        return {'FINISHED'}
    
    
class OBJECT_OT_skSelect(bpy.types.Operator):
    bl_idname = "object.sk_select"
    bl_label = "Select Shapekey"
    bl_description = "Select objects with SHAPEKEYS"
    bl_options = {"UNDO"}
    
    def execute(self, context):
        scn = bpy.context.scene
        
        skOb = []
        
        for ob in scn.objects:
            if ob.type == "MESH":
                if ob.data.shape_keys != None:
                    sk = list(ob.data.shape_keys.key_blocks)
                    if len(sk) >= 1:
                        skOb.append(ob)
                        
        if len(skOb) >= 1:
            for ob in scn.objects:
                if ob in skOb:
                    ob.select = True
                else:
                    ob.select = False    
            scn.objects.active = skOb[0]
            self.report({'INFO'}, str(len(skOb)) + " objects have SHAPEKEYS")
        else:
            self.report({'INFO'}, 'No objects have SHAPEKEYS')                                
                             
        return {'FINISHED'}

#--------------------- SK SYMMETRIZE ----------------------------------
def vgroupHalves(ob):
    #### select left half of verts and add to new vertex group ####
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action='DESELECT') # deselect all verts
        bpy.ops.object.mode_set(mode="OBJECT")
        
    for v in ob.data.vertices:
        if v.co[0] >= 0:
            v.select = True
    
    bpy.ops.object.vertex_group_add()
    ob.vertex_groups.active.name = "kt_temp_halfL"
    
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.object.vertex_group_assign()
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.object.mode_set(mode="OBJECT")
        
    bpy.ops.object.vertex_group_add()
    ob.vertex_groups.active.name = "kt_temp_halfR"
    
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.object.vertex_group_assign()
        bpy.ops.object.mode_set(mode="OBJECT")  

def skSymmetrize(ob):
    skName = ob.active_shape_key.name
    skVG = ob.active_shape_key.vertex_group
    shapeKeys = ob.data.shape_keys.key_blocks
    
    shapeKeys[skName].vertex_group = "kt_temp_halfL"
    bpy.ops.object.shape_key_add(from_mix=True)
    ob.active_shape_key.name = "kt_temp_mirror"
    bpy.ops.object.shape_key_mirror()
    shapeKeys["kt_temp_mirror"].vertex_group = "kt_temp_halfR"
    shapeKeys["kt_temp_mirror"].value = 1
    bpy.ops.object.shape_key_add(from_mix=True)
    ob.active_shape_key.name = "kt_temp_combo"
    ob.active_shape_key.value = 1    

    for i, sk in enumerate(shapeKeys): #first loop removes trash shapekeys
        if sk.name == "kt_temp_mirror":
            ob.active_shape_key_index = i
            bpy.ops.object.shape_key_remove()
    bpy.ops.object.shape_key_remove() #don't know why I can't do this in the loop!
    
    for i, sk in enumerate(shapeKeys): 
        if sk.name == "kt_temp_combo":
            sk.name = skName
            sk.vertex_group = skVG
            ob.active_shape_key_index = i
            
def vgroupHalvesRemove(ob):
    for vg in ob.vertex_groups:
        if vg.name == "kt_temp_halfR":
            bpy.ops.object.vertex_group_set_active(group=vg.name)
            bpy.ops.object.vertex_group_remove()
    bpy.ops.object.vertex_group_remove()             

class OBJECT_OT_skSymmetrize(bpy.types.Operator):
    bl_idname = "object.sk_symmetrize"
    bl_label = "Symmetrize"
    bl_description = "Mirror vert positions from +X to -X for active shapeKey"
    bl_options = {"UNDO"}
     
    def execute(self, context):
        actOb = bpy.context.active_object
        
        vgroupHalves(actOb)
        skSymmetrize(actOb)
        vgroupHalvesRemove(actOb)
        
        return {'FINISHED'}
    
    
#--------------------- RESET NORMALS ----------------------------------
    
class OBJECT_OT_resetMeshNormals(bpy.types.Operator):
    bl_idname = "object.reset_normals"
    bl_label = "Reset Mesh Normals"
    bl_description = "Reset face normals for all or selected objects"
    bl_options = {"UNDO"}
    
    def execute(self, context):
        scn = bpy.context.scene
        selOb = bpy.context.selected_objects
        
        skOb = []
        
        if selOb:
            targetOb = selOb
        else:
            targetOb = scn.objects
            
        for ob in targetOb:
            if ob.type == 'MESH':
                scn.objects.active = ob
                if bpy.ops.object.mode_set.poll():
                    bpy.ops.object.mode_set(mode="EDIT")
                    
                    #might want to store selected elements
                    
                    bpy.ops.mesh.select_all(action='SELECT') #select all
                    bpy.ops.mesh.normals_make_consistent(inside=False)
                    
                    bpy.ops.object.mode_set(mode="OBJECT")
                                         
        return {'FINISHED'}
        
    
#--------------------- SHAPEKEY SPLIT ----------------------------------

class OBJECT_OT_shapeKeySplit(bpy.types.Operator):
    bl_idname = "data.shapekey_split"
    bl_label = "Split Shapekeys"
    bl_description = "Splits shapekeys of active object into one object per shape"
    
    def execute(self, context):
        scn = bpy.context.scene
        kt = bpy.context.window_manager.katietools
        selOb = bpy.context.selected_objects
        actOb = bpy.context.active_object
        
        fixers = list(kt.cl_skFix.split(','))
        
        if kt.cl_absTrans == False:
            dimX = actOb.dimensions[0] * kt.cl_skTrans
        else:
            dimX = kt.cl_skTrans
           
        skNames = []
        dupCache = []
        trash = []   
        
        if selOb:
            if len(selOb) == 1:
                if actOb.data.shape_keys == None:
                    self.report({'INFO'}, "Active object has no shapekeys")
                else:        
                    shapeKeys = actOb.data.shape_keys.key_blocks
                    
                    for ob in scn.objects:
                        if ob.name in shapeKeys:
                            ob.name = ob.name + "_OLD"
                          
                    for sk in shapeKeys:        
                        skNames.append(sk.name)
                        bpy.ops.object.duplicate(linked=False) #TODO -- search and rename objects with same name as a shapekey
                        bpy.ops.transform.translate(value=(dimX, 0.0, 0.0))
                        dupCache.append(bpy.context.active_object)
                        
                    for ob in scn.objects:    
                        if ob in dupCache:
                            num = dupCache.index(ob)
                            ob.name = skNames[num] #rename duped objects with appropriate shapekey name
                            
                            for sk in ob.data.shape_keys.key_blocks:
                                if sk.name == ob.name or sk.name == "Basis" or sk.name in fixers: #needs the Basis shape to work
                                    sk.mute = False
                                else:
                                    sk.mute = True
                            
                            if ob.name == "Basis" or ob.name in fixers: #single out BASIS and FIX SHAPE objects
                                ob.select = True
                                trash.append(ob)
                                scn.objects.active = ob
                            else:
                                ob.select = False    
                                
                            bpy.ops.object.delete() #delete BASIS and FIX SHAPE objects
                        
                    for ob in scn.objects:        
                        if ob in dupCache:
                            ob.select = True
                            
                    scn.objects.active = bpy.context.selected_objects[0]
                    bpy.ops.data.shapekey_apply()

                    bpy.ops.transform.translate(value=((dimX * -(len(trash))), 0.0, 0.0)) #translate the left over shapes
                     
                    self.report({'INFO'}, "ShapeKeys propagated")
            else:
                self.report({'INFO'}, "One object at a time please!")
        else:
            self.report({'INFO'}, "Nothing selected")
        
        return {'FINISHED'}  
    
