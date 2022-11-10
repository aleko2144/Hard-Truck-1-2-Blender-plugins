import math

import bpy
import logging
import sys
import re

from b3d_tools.common import log
from b3d_tools.b3d.classes import fieldType, b_common

# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
# log = logging.getLogger("common")

def prop(obj):
    return obj['prop']

def getAllChildren(obj):
    allChildren = []
    currentObjs = [obj]
    while(1):
        nextChildren = []
        if len(currentObjs) > 0:
            for obj in currentObjs:
                nextChildren.extend(obj.children)
            currentObjs = nextChildren
            allChildren.extend(currentObjs)
        else:
            break
    return allChildren

def getLODObjects(obj):
    vertObjs = None
    if obj["level_group"] == 0:
        vertObjs = [cn for cn in obj.children if ( \
            cn.get("block_type") is not None
            and (cn["block_type"]==6 or cn["block_type"]==7 \
            or cn["block_type"]==36 or cn["block_type"]==37 \
            or cn["block_type"]==8 or cn["block_type"]==35\
            or cn["block_type"]==28)) \
            and (cn.get("level_group") is not None and (cn["level_group"]==1))]
    else: # == 1
        vertObjs = [cn for cn in obj.children if ( \
            cn.get("block_type") is not None
            and (cn["block_type"]==6 or cn["block_type"]==7 \
            or cn["block_type"]==36 or cn["block_type"]==37 \
            or cn["block_type"]==8 or cn["block_type"]==35 \
            or cn["block_type"]==28))]
        # if len(vertObjs) == 0:
        #     vertObjs = [cn for cn in obj.children if (cn.get("block_type") is not None and (cn["block_type"]==8 or cn["block_type"]==35)) and (cn.get("level_group") is not None and (cn["level_group"]==1))]
    # vertObjs.sort(key=lambda x: x.name, reverse=True)
    # lodCnt = math.floor(len(vertObjs) / 2)
    # return vertObjs[0:lodCnt]
    return vertObjs

def getCondObjects(obj, group):
    vertObjs = None
    if group != -1:
        vertObjs = [cn for cn in obj.children if \
            (cn.get("level_group") is not None and (cn["level_group"]==group))]
    else:
        vertObjs = [cn for cn in obj.children]
    return vertObjs

def applyTransform(block_18):

    spaceName = block_18["space_name"]
    objName = block_18["add_name"]
    log.debug("Applying transform {} to object {}".format(spaceName, objName))

    spaceObj = bpy.data.objects.get(spaceName)
    destObj = bpy.data.objects.get(objName)

    if(spaceObj == None):
        log.warn("Transformation object not found in "+block_18.name)
        return

    if(destObj == None):
        log.warn("Destination object not found in "+block_18.name)
        return

    # if not destObj.hide_get(): #hidden objects not coopied

    linkObj = None
    if bpy.data.objects.get(spaceObj.name + "_b3dSpaceCopy"):
        linkObj = bpy.data.objects[spaceObj.name + "_b3dSpaceCopy"]
    else:
        linkObj = spaceObj.copy()
        linkObj.parent = spaceObj.parent
        linkObj.rotation_euler[0] = spaceObj.rotation_euler[0]
        linkObj.rotation_euler[1] = spaceObj.rotation_euler[1]
        linkObj.rotation_euler[2] = spaceObj.rotation_euler[2]
        linkObj.location = spaceObj.location
        linkObj.name = spaceObj.name + "_b3dSpaceCopy"
        bpy.context.collection.objects.link(linkObj)

    reIsCopy = re.compile(r'.*b3dcopy.*')

    allVisibleChildren = [obj for obj in getAllChildren(destObj) if not obj.hide_get()]

    subTransforms = [obj for obj in allVisibleChildren if obj.get("block_type") is not None and obj["block_type"] == 18]

    meshes = [obj for obj in allVisibleChildren if obj.type=="MESH" and not reIsCopy.search(obj.name)]

    newmeshes = []

    for trans in subTransforms:
        subSpaceObj = bpy.data.objects.get(trans["space_name"]+"_b3dSpaceCopy")
        if subSpaceObj:
            subSpaceObj.parent = linkObj

    log.info("Copying meshes")
    for mesh in meshes:
        newmesh = mesh.copy()
        # newmesh.data = mesh.data.copy() # for NOT linked copy
        newmesh.parent = linkObj
        newmesh.name = "{}_b3dcopy".format(mesh.name)
        newmeshes.append(newmesh)

    log.info("Linking meshes")
    for newmesh in newmeshes:
        log.info("Linking {}".format(newmesh.name))
        bpy.context.collection.objects.link(newmesh)


reb3dSpace = re.compile(r'.*b3dSpaceCopy.*')
reb3dMesh = re.compile(r'.*b3dcopy.*')

def applyRemoveTransforms():
    toRemove = False
    for obj in (bpy.data.objects):
        if reb3dSpace.search(obj.name):
            toRemove = True
            break
    if toRemove:
        removeTransforms()
    else:
        applyTransforms()


def removeTransforms():
    spaces = [cn for cn in bpy.data.objects if reb3dSpace.search(cn.name)]
    meshes = [cn for cn in bpy.data.objects if reb3dMesh.search(cn.name)]

    for mesh in meshes:
        mesh.select_set(True)
    bpy.ops.object.delete()

    for space in spaces:
        space.select_set(True)
    bpy.ops.object.delete()

def applyTransforms():
    objs = [cn for cn in bpy.data.objects if cn.get("block_type") is not None and cn["block_type"]==18 and not cn.hide_get()]
    for obj in objs:
        applyTransform(obj)

def showHideObjByType(type):
    objs = [cn for cn in bpy.data.objects if cn.get("block_type") is not None and cn["block_type"]==type]
    hiddenObj = [cn for cn in bpy.data.objects if cn.get("block_type") is not None and cn["block_type"]==type and cn.hide_get()]
    if len(objs) == len(hiddenObj):
        for obj in objs:
            obj.hide_set(False)
    else:
        for obj in objs:
            obj.hide_set(True)

def showHideObjTreeByType(type):
    objs = [cn for cn in bpy.data.objects if cn.get("block_type") is not None and cn["block_type"]==type]
    hiddenObj = [cn for cn in bpy.data.objects if cn.get("block_type") is not None and cn["block_type"]==type and cn.hide_get()]
    if len(objs) == len(hiddenObj):
        for obj in objs:
            children = getAllChildren(obj)
            for child in children:
                child.hide_set(False)
            obj.hide_set(False)
    else:
        for obj in objs:
            children = getAllChildren(obj)
            for child in children:
                child.hide_set(True)
            obj.hide_set(True)

def getNBlockHierarchy(root, block_type, rootnum=0, curlevel=0, arr=[]):
    for obj in root.children:
        if obj['block_type'] == block_type:
            arr.append([rootnum, curlevel, obj])
            getNBlockHierarchy(obj, block_type, rootnum, curlevel+1, arr)
            rootnum+=1
        getNBlockHierarchy(obj, block_type, rootnum, curlevel, arr)

def processLOD(root, state):
    arr = []
    rootnum = 0
    curlevel = 0
    if root['block_type'] == 10:
        arr.append([rootnum, curlevel, root])
        curlevel +=1
    getNBlockHierarchy(root, 10, rootnum, curlevel, arr)
    LODRoots = [cn[2] for cn in arr if cn[1]==0]
    for LODRoot in LODRoots:
        print(LODRoot.name)
        lods = [cn for cn in LODRoot.children if (cn.get("level_group") is not None and (cn["level_group"]==1))]
        print(len(lods))
        for lod in lods:
            if isMeshBlock(lod):
                lod.hide_set(state)
            else:
                for obj in [cn for cn in getAllChildren(lod) if isMeshBlock(cn)]:
                    obj.hide_set(state)

def showLOD(root):
    processLOD(root, False)

def hideLOD(root):
    processLOD(root, True)

# def showHideLOD():
#     lodRoots = [cn for cn in bpy.data.objects if cn.get("block_type") is not None and cn["block_type"]==10]
#     hiddenLodRoots = [cn for cn in bpy.data.objects if cn.get("block_type") is not None and cn["block_type"]==10 and cn.hide_get()]
#     if len(hiddenLodRoots) > 0: #show
#         for lodRoot in lodRoots:
#             lods = getLODObjects(lodRoot)
#             if len(lods) > 0:
#                 lodRoot.hide_set(False)
#             for lod in lods:
#                 lod.hide_set(False)
#                 for obj in getAllChildren(lod):
#                     obj.hide_set(False)
#     else: #hide
#         for lodRoot in lodRoots:
#             lods = getLODObjects(lodRoot)
#             if len(lods) > 0:
#                 lodRoot.hide_set(True)
#             for lod in lods:
#                 lod.hide_set(True)
#                 for obj in getAllChildren(lod):
#                     obj.hide_set(True)

# def get21blocks(root, rootnum=0, curlevel=0, arr=[]):
#     for obj in root.children:
#         if obj['block_type'] == 21:
#             arr.append([rootnum, curlevel, obj])
#             get21blocks(obj, rootnum, curlevel+1, arr)
#             rootnum+=1
#         get21blocks(obj, rootnum, curlevel, arr)

def isMeshBlock(obj):
    # 18 - for correct transform apply
    return obj.get("block_type") is not None \
        and (obj["block_type"]==8 or obj["block_type"]==35\
        or obj["block_type"]==28 or obj["block_type"]==18)


def processCond(root, group, state):
    arr = []
    rootnum = 0
    curlevel = 0
    if root['block_type'] == 21:
        arr.append([rootnum, curlevel, root])
        curlevel +=1
    getNBlockHierarchy(root, 21, rootnum, curlevel, arr)
    condRoots = sorted(arr, key=lambda arr: arr[1], reverse=True)
    for condRootArr in condRoots:
        condRoot = condRootArr[2]
        groupMax = sorted([cn['level_group'] for cn in condRoot.children], reverse=True)[0]
        if group > groupMax:
            group = groupMax
        print(condRoot.name)
        conds = getCondObjects(condRoot, group)
        print(len(conds))
        for cond in conds:
            if isMeshBlock(cond):
                cond.hide_set(state)
            else:
                for obj in [cn for cn in getAllChildren(cond) if isMeshBlock(cn)]:
                    obj.hide_set(state)

def showConditionals(root, group):
    processCond(root, group, False)


def hideConditionals(root, group):
    processCond(root, group, True)



def drawCommon(l_self, obj):
	block_type = None
	level_group = None
	if 'block_type' in obj:
		block_type = obj['block_type']

	if 'level_group' in obj:
		level_group = obj['level_group']

	lenStr = str(len(obj.children))

	box = l_self.layout.box()
	box.label(text="Тип блока: " + str(block_type))
	box.label(text="Кол-во вложенных блоков: " + lenStr)
	box.label(text="Группа блока: " + str(level_group))

def drawAllFieldsByType(l_self, context, zclass):
    drawFieldsByType(l_self, context, b_common)
    drawFieldsByType(l_self, context, zclass)

def drawFieldsByType(l_self, context, zclass):
    btype = zclass.__name__.split('_')[1]
    bname = "block{}".format(btype)

    attrs = [obj for obj in zclass.__dict__.keys() if not obj.startswith('__')]
    for attr in attrs:
        obj = zclass.__dict__[attr]
        drawFieldByType(l_self, context, obj, bname)

def drawFieldByType(l_self, context, obj, bname):
    ftype = obj['type']
    pname = obj['prop']
    mytool = context.scene.my_tool
    box = l_self.layout.box()
    box.prop(getattr(mytool, bname), "show_"+pname)

    col = box.column()
    if ftype == fieldType.STRING:
        col.prop(getattr(mytool, bname), pname)

    elif ftype == fieldType.COORD:
        col.prop(getattr(mytool, bname), pname)

    elif ftype == fieldType.RAD:
        col.prop(getattr(mytool, bname), pname)

    elif ftype == fieldType.INT:
        col.prop(getattr(mytool, bname), pname)

    elif ftype == fieldType.FLOAT:
        col.prop(getattr(mytool, bname), pname)

    elif ftype == fieldType.ENUM:
        col.prop(getattr(mytool, bname), pname)

    elif ftype == fieldType.LIST:
        collect = getattr(mytool, bname)
        # col.prop(getattr(mytool, bname), pname)
        col.template_list("SCENE_UL_list", "", collect, pname, mytool, "list_index")
        # collect = getattr(getattr(mytool, bname), pname)
        # print(dir(collect))
        # for item in collect.items():
        #     print(item)
        #     col.prop(item, "value")

    if getattr(getattr(mytool, bname), "show_"+pname):
        col.enabled = True
    else:
        col.enabled = False

def getAllObjsByType(context, object, zclass):
    getObjsByType(context, object, b_common)
    getObjsByType(context, object, zclass)

def getObjsByType(context, object, zclass):
    attrs = [obj for obj in zclass.__dict__.keys() if not obj.startswith('__')]
    btype = zclass.__name__.split('_')[1]
    bname = "block{}".format(btype)
    mytool = context.scene.my_tool
    for property in attrs:
        obj = zclass.__dict__[property]

        # print(dir(getattr(mytool, bname)))

        if getattr(getattr(mytool, bname), "show_"+obj['prop']) is not None \
            and getattr(getattr(mytool, bname), "show_"+obj['prop']):

            if obj['type'] == fieldType.FLOAT or obj['type'] == fieldType.RAD:
                getattr(mytool, bname)[obj['prop']] = float(object[obj['prop']])

            elif obj['type'] == fieldType.INT:
                getattr(mytool, bname)[obj['prop']] = int(object[obj['prop']])

            elif obj['type'] == fieldType.STRING:
                getattr(mytool, bname)[obj['prop']] = str(object[obj['prop']])

            elif obj['type'] == fieldType.LIST:

                col = getattr(getattr(mytool, bname), obj['prop'])

                col.clear()
                for i, obj in enumerate(object[obj['prop']]):
                    item = col.add()
                    item.index = i
                    item.value = obj
                # getattr(mytool, bname)[obj['prop']] = str(object[obj['prop']])

            else:
                getattr(mytool, bname)[obj['prop']] = object[obj['prop']]

def setAllObjsByType(context, object, zclass):
    setObjsByType(context, object, b_common)
    setObjsByType(context, object, zclass)


def setObjsByType(context, object, zclass):
    attrs = [obj for obj in zclass.__dict__.keys() if not obj.startswith('__')]
    btype = zclass.__name__.split('_')[1]
    bname = "block{}".format(btype)
    mytool = context.scene.my_tool
    for property in attrs:
        obj = zclass.__dict__[property]
        if getattr(getattr(mytool, bname), "show_"+obj['prop']) is not None \
            and getattr(getattr(mytool, bname), "show_"+obj['prop']):

            if obj['type'] == fieldType.FLOAT or obj['type'] == fieldType.RAD:
                object[obj['prop']] = float(getattr(mytool, bname)[obj['prop']])

            elif obj['type'] == fieldType.INT:
                object[obj['prop']] = int(getattr(mytool, bname)[obj['prop']])

            elif obj['type'] == fieldType.STRING:
                object[obj['prop']] = str(getattr(mytool, bname)[obj['prop']])

            elif obj['type'] == fieldType.COORD:
                xyz = getattr(mytool, bname)[obj['prop']]
                object[obj['prop']] = (xyz[0],xyz[1],xyz[2])

            elif obj['type'] == fieldType.LIST:
                collect = getattr(getattr(mytool, bname), obj['prop'])

                arr = []
                for item in list(collect):
                    arr.append(item.value)

                object[obj['prop']] = arr

            else:
                object[obj['prop']] = getattr(mytool, bname)[obj['prop']]
