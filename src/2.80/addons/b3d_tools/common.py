import bpy
import logging
import sys
import re

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger("common")

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

    allChildren = [obj for obj in getAllChildren(destObj)]

    subTransforms = [obj for obj in allChildren if obj.get("block_type") is not None and obj["block_type"] == 18]

    meshes = [obj for obj in allChildren if obj.type=="MESH" and not reIsCopy.search(obj.name)]

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
        # newmesh.rotation_euler[0] = spaceObj.rotation_euler[0]
        # newmesh.rotation_euler[1] = spaceObj.rotation_euler[1]
        # newmesh.rotation_euler[2] = spaceObj.rotation_euler[2]
        # newmesh.location = spaceObj.location
        newmeshes.append(newmesh)

    log.info("Linking meshes")
    for newmesh in newmeshes:
        bpy.context.collection.objects.link(newmesh)

    # destObj.rotation_euler[0] = spaceObj.rotation_euler[0]
    # destObj.rotation_euler[1] = spaceObj.rotation_euler[1]
    # destObj.rotation_euler[2] = spaceObj.rotation_euler[2]
    # destObj.location = spaceObj.location


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
    objs = [cn for cn in bpy.data.objects if cn.get("block_type") is not None and cn["block_type"]==18]
    for obj in objs:
        applyTransform(obj)

def showHideObjByType(type):
    objs = [cn for cn in bpy.data.objects if cn.get("block_type") is not None and cn["block_type"]==type]
    hiddenObj = [cn for cn in bpy.data.objects if cn.get("block_type") is not None and cn["block_type"]==type and cn.hide_get()]
    if objs == hiddenObj:
        for obj in objs:
            obj.hide_set(False)
    else:
        for obj in objs:
            obj.hide_set(True)

def showHideObjTreeByType(type):
    objs = [cn for cn in bpy.data.objects if cn.get("block_type") is not None and cn["block_type"]==type]
    hiddenObj = [cn for cn in bpy.data.objects if cn.get("block_type") is not None and cn["block_type"]==type and cn.hide_get()]
    if objs == hiddenObj:
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