import math

import bpy
import logging
import sys
import re

from .classes import (
    b_18,
    b_21
)
from ..common import (
    log
)
from .common import (
    getPolygonsBySelectedVertices,
    getSelectedVertices,
	isRootObj
)
from .classes import (
    fieldType, b_common
)

# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
# log = logging.getLogger("common")

reb3dSpace = re.compile(r'.*b3dSpaceCopy.*')
reb3dMesh = re.compile(r'.*b3dcopy.*')

class Graph:

    def __init__(self, graph):
        self.graph = graph

    def DFSUtil(self, val, visited):

        visited[val]["in"] += 1
        for v in self.graph[val]:
            print(v)
            if self.graph.get(v) is not None:
                visited[val]["out"] += 1
                self.DFSUtil(v, visited)

    def DFS(self, start=None):
        V = len(self.graph)  #total vertices

        visited = {}
        for val in self.graph.keys():
            visited[val] = {
                "in": 0,
                "out": 0
            }

        searchIn = []
        if start is not None:
            searchIn.append(start.name)
        else:
            searchIn = self.graph.keys()

        for val in searchIn:
            for v in self.graph[val]:
                print(v)
                if self.graph.get(v) is not None:
                    visited[val]["out"] += 1
                    self.DFSUtil(v, visited)

        return visited


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

def applyTransforms():
    roots = [cn for cn in bpy.data.objects if isRootObj(cn)]
    for root in roots:
        log.debug(root.name)
        hroots = getHierarchyRoots(root)
        for hroot in hroots:
            obj = bpy.data.objects.get(hroot)
            if obj is not None:
                applyTransform(obj)

def applyTransform(root):

    if bpy.data.objects.get('b3dCenterSpace') is None:
        b3dObj = bpy.data.objects.new('b3dCenterSpace', None)
        b3dObj['block_type'] = 24
        b3dObj.rotation_euler[0] = 0.0
        b3dObj.rotation_euler[1] = 0.0
        b3dObj.rotation_euler[2] = 0.0
        b3dObj.location = (0.0, 0.0, 0.0)
        bpy.context.collection.objects.link(b3dObj)

    if bpy.data.objects.get('b3dCenterSpace' + '_b3dSpaceCopy') is None:
        b3dObj = bpy.data.objects.new('b3dCenterSpace' + '_b3dSpaceCopy', None)
        b3dObj['block_type'] = 24
        b3dObj.rotation_euler[0] = 0.0
        b3dObj.rotation_euler[1] = 0.0
        b3dObj.rotation_euler[2] = 0.0
        b3dObj.location = (0.0, 0.0, 0.0)
        bpy.context.collection.objects.link(b3dObj)

    stack = [[root, 'b3dCenterSpace', 'b3dCenterSpace' + '_b3dSpaceCopy']]

    while stack:
        block, prevSpace, prevSpaceCopy = stack.pop()

        prevSpaceObj = bpy.data.objects.get(prevSpace)
        prevSpaceCopyObj = bpy.data.objects.get(prevSpaceCopy)

        log.debug("{} {}".format(block['block_type'], block.name))
        log.debug(prevSpace)
        log.debug(prevSpaceCopy)

        if block['block_type'] == 18:
            objName = block["add_name"]
            spaceName = block["space_name"]

            destObj = bpy.data.objects.get(objName)

            if not block.hide_get():

                if spaceName == 'empty name':
                    spaceName = prevSpace

                spaceObj = bpy.data.objects.get(spaceName)

                if(spaceObj == None):
                    log.warn("Transformation object not found in " + block.name)
                    return

                if(destObj == None):
                    log.warn("Destination object not found in " + block.name)
                    return

                spaceCopy = None
                if bpy.data.objects.get(spaceObj.name + "_b3dSpaceCopy"):
                    spaceCopy = bpy.data.objects[spaceObj.name + "_b3dSpaceCopy"]
                else:
                    spaceCopy = spaceObj.copy()
                    spaceCopy.parent = prevSpaceCopyObj
                    spaceCopy.rotation_euler[0] = spaceObj.rotation_euler[0]
                    spaceCopy.rotation_euler[1] = spaceObj.rotation_euler[1]
                    spaceCopy.rotation_euler[2] = spaceObj.rotation_euler[2]
                    spaceCopy.location = spaceObj.location
                    spaceCopy.name = spaceObj.name + "_b3dSpaceCopy"
                    bpy.context.collection.objects.link(spaceCopy)
                stack.append([destObj, spaceObj.name, spaceCopy.name])
            # else:
            #     stack.append([destObj, prevSpace, prevSpaceCopy])

            continue

        if isMeshBlock(block) and not block.hide_get():
            # block.hide_set(True)
            # log.debug(block.name)
            # log.debug(prevSpace)
            newmesh = block.copy()
            # newmesh.data = mesh.data.copy() # for NOT linked copy
            newmesh.parent = prevSpaceCopyObj
            newmesh.name = "{}_b3dcopy".format(block.name)
            # log.info("Linking {}".format(newmesh.name))
            bpy.context.collection.objects.link(newmesh)
            # newmesh.hide_set(False)

        for directChild in block.children:
            stack.append([directChild, prevSpace, prevSpaceCopy])


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

    reb3dPos = re.compile(r'b3dcopy')

    bpy.ops.object.select_all(action = 'DESELECT')

    for mesh in meshes:
        # res = reb3dPos.search(mesh.name)
        # postfixStart = res.start()
        # original = bpy.data.objects[mesh.name[:postfixStart-1]]
        # original.hide_set(False)
        mesh.select_set(True)
    bpy.ops.object.delete()

    for space in spaces:
        space.select_set(True)
    bpy.ops.object.delete()


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

def getHierarchyRoots(root):
    globalRoot = root
    while globalRoot.parent is not None:
        globalRoot = globalRoot.parent

    blocks18 = [cn for cn in bpy.data.objects if cn['block_type'] is not None and cn['block_type'] == 18]
    ref_set = set()
    for cn in blocks18:
        #out refs
        if bpy.data.objects.get(cn['add_name']) is not None:
            ref_set.add(cn['add_name'])

        #in refs
        temp = cn
        while temp.parent is not globalRoot:
            temp = temp.parent
        ref_set.add(temp.name)

    referenceables = list(ref_set)
    referenceables.sort()

    other = [cn.name for cn in globalRoot.children if cn['block_type'] is not None \
        and (cn['block_type'] == 4 or cn['block_type'] == 5 or cn['block_type'] == 19) \
        and cn.name not in referenceables ]

    noDubGraph = {}
    graph = {}
    for r in referenceables:
        noDubGraph[r] = set()

    for r in referenceables:
        references = [cn for cn in getAllChildren(bpy.data.objects[r]) if cn['block_type'] is not None and cn['block_type'] == 18]
        for refObj in references:
            noDubGraph[r].add(refObj['add_name'])

    for r in referenceables:
        graph[r] = list(noDubGraph[r])

    zgraph = Graph(graph)

    closestRoot = root
    if closestRoot != globalRoot:
        if closestRoot.name not in graph:
            while (closestRoot.parent['block_type'] is not None and closestRoot.parent['block_type'] != 5 \
            and closestRoot.parent.name not in graph) or closestRoot.parent is None: # closest or global
                closestRoot = closestRoot.parent
    else:
        closestRoot = None

    visited = zgraph.DFS(closestRoot)

    roots = [cn for cn in visited.keys() if (visited[cn]["in"] == 0) and (visited[cn]["out"] > 0)]

    res = other
    res.extend(roots)

    return res


# def getNBlockHierarchy(root, block_type, rootnum=0, curlevel=0, arr=[]):
#     for obj in root.children:
#         if obj['block_type'] == block_type:
#             print("block_type block")
#             arr.append([rootnum, curlevel, obj])
#             getNBlockHierarchy(obj, block_type, rootnum, curlevel+1, arr)
#             rootnum+=1
#         elif obj['block_type'] == 18:
#             print("ref block")
#             refObj = bpy.data.objects[obj[prop(b_18.Add_Name)]]
#             arr.append([rootnum, curlevel, refObj])
#             getNBlockHierarchy(refObj, block_type, rootnum, curlevel+1, arr)
#             rootnum+=1
#         getNBlockHierarchy(obj, block_type, rootnum, curlevel, arr)

def isMeshBlock(obj):
    # 18 - for correct transform apply
    return obj.get("block_type") is not None \
        and (obj["block_type"]==8 or obj["block_type"]==35\
        or obj["block_type"]==28 \
        # or obj["block_type"]==18
        )

def isRefBlock(obj):
    return obj.get("block_type") is not None and obj["block_type"]==18


def processLOD(root, state, explevel = 0, curlevel = -1):

    stack = [[root, curlevel, False]]

    while stack:
        block, clevel, isActive = stack.pop()

        if block['block_type'] == 18:
            refObj = bpy.data.objects.get(block['add_name'])
            if refObj is not None:
                stack.append([refObj, clevel, isActive])
                if isActive:
                    block.hide_set(state)

        if block['block_type'] == 10:
            clevel += 1

        if isActive and isMeshBlock(block):
            block.hide_set(state)


        for directChild in block.children:
            log.debug("Processing {}".format(directChild.name))
            if clevel == explevel:
                if directChild['level_group'] == 1:
                    stack.append([directChild, clevel, True])
                else:
                    stack.append([directChild, -1, isActive])
            elif clevel > explevel:
                stack.append([directChild, clevel, True])
            else:
                stack.append([directChild, clevel, isActive])


def showLOD(root):
    if root.parent is None:
        hroots = getHierarchyRoots(root)
        for hroot in hroots:
            obj = bpy.data.objects.get(hroot)
            if obj is not None:
                processLOD(obj, False, 0, -1)
    else:
        processLOD(root, False, 0, -1)

def hideLOD(root):
    if root.parent is None:
        hroots = getHierarchyRoots(root)
        for hroot in hroots:
            obj = bpy.data.objects.get(hroot)
            if obj is not None:
                processLOD(obj, True, 0, -1)
    else:
        processLOD(root, True, 0, -1)


def processCond(root, group, state):

    curlevel = 0
    globlevel = 0

    stack = [[root, curlevel, globlevel, 0, False]]

    while stack:
        block, clevel, glevel, groupMax, isActive = stack.pop()

        l_group = group

        if block['block_type'] == 18:
            refObj = bpy.data.objects.get(block['add_name'])
            if refObj is not None:
                stack.append([refObj, clevel+1, glevel, groupMax, isActive])
                if isActive:
                    block.hide_set(state)

        if block['block_type'] == 21:
            glevel += 1
            clevel = 1
            groupMax = block[prop(b_21.GroupCnt)]
            if l_group > groupMax-1:
                l_group = groupMax-1

        if isActive and isMeshBlock(block):
            block.hide_set(state)

        for directChild in block.children:
            log.debug("Processing {}".format(directChild.name))
            nextState = False
            if glevel == 1:
                nextState = True
            elif glevel > 1:
                nextState = isActive and True
            if clevel == 1:
                if directChild['level_group'] == l_group or l_group == -1:
                    stack.append([directChild, clevel+1, glevel, groupMax, nextState])
                else:
                    stack.append([directChild, clevel+1, glevel, groupMax, False])
            elif clevel > 1:
                stack.append([directChild, clevel+1, glevel, groupMax, isActive])
            else:
                stack.append([directChild, clevel+1, glevel, groupMax, False])

def showConditionals(root, group):

    if root.parent is None:
        hroots = getHierarchyRoots(root)
        for hroot in hroots:
            obj = bpy.data.objects.get(hroot)
            if obj is not None:
                processCond(obj, group, False)
    else:
        processCond(root, group, False)


def hideConditionals(root, group):

    if root.parent is None:
        hroots = getHierarchyRoots(root)
        for hroot in hroots:
            obj = bpy.data.objects.get(hroot)
            if obj is not None:
                processCond(obj, group, True)
    else:
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
    if zclass.__name__.split('_')[0] == 'b':
        drawFieldsByType(l_self, context, b_common)
        drawFieldsByType(l_self, context, zclass)
    else:
        drawFieldsByType(l_self, context, zclass)

def drawFieldsByType(l_self, context, zclass):
    # btype = zclass.__name__.split('_')[1]
    # bname = "block{}".format(btype)

    attrs = [obj for obj in zclass.__dict__.keys() if not obj.startswith('__')]
    for attr in attrs:
        obj = zclass.__dict__[attr]
        drawFieldByType(l_self, context, obj, zclass)

def drawFieldByType(l_self, context, obj, zclass):

    bname = ''
    btype, bnum = zclass.__name__.split('_')
    if btype == 'b':
        bname = 'block{}'.format(bnum)
    elif btype == 'pfb':
        bname = 'perFaceBlock{}'.format(bnum)
    elif btype == 'pvb':
        bname = 'perVertBlock{}'.format(bnum)

    ftype = obj['type']
    pname = obj['prop']
    mytool = context.scene.my_tool

    if ftype == fieldType.STRING \
    or ftype == fieldType.COORD \
    or ftype == fieldType.RAD \
    or ftype == fieldType.INT \
    or ftype == fieldType.FLOAT \
    or ftype == fieldType.ENUM \
    or ftype == fieldType.LIST:

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

            scn = bpy.context.scene

            rows = 2
            row = box.row()
            row.template_list("CUSTOM_UL_items", "", collect, pname, scn, "custom_index", rows=rows)

            col = row.column(align=True)
            props = col.operator("custom.list_action", icon='ADD', text="")
            props.action = 'ADD'
            props.bname = bname
            props.pname = pname
            props = col.operator("custom.list_action", icon='REMOVE', text="")
            props.action = 'REMOVE'
            props.bname = bname
            props.pname = pname
            col.separator()
            props = col.operator("custom.list_action", icon='TRIA_UP', text="")
            props.action = 'UP'
            props.bname = bname
            props.pname = pname
            props = col.operator("custom.list_action", icon='TRIA_DOWN', text="")
            props.action = 'DOWN'
            props.bname = bname
            props.pname = pname


            # row = box.row()
            # col = row.column(align=True)
            # row = col.row(align=True)
            # row.operator("custom.print_items", icon="LINENUMBERS_ON")
            # row = col.row(align=True)
            # row.operator("custom.clear_list", icon="X")
            # row.operator("custom.remove_duplicates", icon="GHOST_ENABLED")

            # row = box.row()
            # col = row.column(align=True)
            # row = col.row(align=True)
            # row.operator("custom.add_viewport_selection", icon="HAND") #LINENUMBERS_OFF, ANIM
            # row = col.row(align=True)
            # row.operator("custom.select_items", icon="VIEW3D", text="Select Item in 3D View")
            # row.operator("custom.select_items", icon="GROUP", text="Select All Items in 3D View").select_all = True
            # row = col.row(align=True)
            # row.operator("custom.delete_object", icon="X")

            # collect = getattr(getattr(mytool, bname), pname)
            # print(dir(collect))
            # for item in collect.items():
            #     print(item)
            #     col.prop(item, "value")

        if getattr(getattr(mytool, bname), "show_"+pname):
            col.enabled = True
        else:
            col.enabled = False
    elif ftype == fieldType.V_FORMAT:
        box = l_self.layout.box()
        box.prop(getattr(mytool, bname), "show_{}".format(pname))
        col1 = box.column()
        col1.prop(getattr(mytool, bname), "{}_{}".format(pname, 'triang_offset'))
        col1.prop(getattr(mytool, bname), "{}_{}".format(pname, 'use_uvs'))
        col1.prop(getattr(mytool, bname), "{}_{}".format(pname, 'use_normals'))
        col1.prop(getattr(mytool, bname), "{}_{}".format(pname, 'normal_flag'))

        if getattr(getattr(mytool, bname), "show_"+pname):
            col1.enabled = True
        else:
            col1.enabled = False

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

def getFromAttributes(context, obj, attrs, bname, index):

    mytool = context.scene.my_tool


    if getattr(getattr(mytool, bname), "show_"+obj['prop']) is not None \
        and getattr(getattr(mytool, bname), "show_"+obj['prop']):

        if obj['type'] == fieldType.FLOAT:
            getattr(mytool, bname)[obj['prop']] = float(getattr(attrs[index], "value"))

        elif obj['type'] == fieldType.COORD:
            getattr(mytool, bname)[obj['prop']] = getattr(attrs[index], "vector")

        elif obj['type'] == fieldType.INT:
            getattr(mytool, bname)[obj['prop']] = int(getattr(attrs[index], "value"))

        elif obj['type'] == fieldType.V_FORMAT:
            format = getattr(attrs[index], "value") ^ 1
            triangOffset = format & 0b10000000
            useUV = format & 0b10
            useNormals = format & 0b10000 and format & 0b100000
            normalFlag = format & 1

            getattr(mytool, bname)["{}_{}".format(obj['prop'],'triang_offset')] = triangOffset
            getattr(mytool, bname)["{}_{}".format(obj['prop'],'use_uvs')] = useUV
            getattr(mytool, bname)["{}_{}".format(obj['prop'],'use_normals')] = useNormals
            getattr(mytool, bname)["{}_{}".format(obj['prop'],'normal_flag')] = normalFlag

def setFromAttributes(context, obj, attrs, bname, index):

    mytool = context.scene.my_tool

    if getattr(getattr(mytool, bname), "show_"+obj['prop']) is not None \
        and getattr(getattr(mytool, bname), "show_"+obj['prop']):

        if obj['type'] == fieldType.FLOAT:
            attrs[index].value = getattr(mytool, bname)[obj['prop']]

        elif obj['type'] == fieldType.INT:
            attrs[index].value = getattr(mytool, bname)[obj['prop']]

        elif obj['type'] == fieldType.COORD:
            attrs[index].vector = getattr(mytool, bname)[obj['prop']]

        elif obj['type'] == fieldType.V_FORMAT:
            value = 0
            triangOffset = getattr(mytool, bname)['{}_{}'.format(obj['prop'], 'triang_offset')]
            useUV = getattr(mytool, bname)['{}_{}'.format(obj['prop'], 'use_uvs')]
            useNormals = getattr(mytool, bname)['{}_{}'.format(obj['prop'], 'use_normals')]
            normalFlag = getattr(mytool, bname)['{}_{}'.format(obj['prop'], 'normal_flag')]

            if triangOffset:
                value = value ^ 0b10000000
            if useUV:
                value = value ^ 0b10
            if useNormals:
                value = value ^ 0b110000
            if normalFlag:
                value = value ^ 0b1

            value = value ^ 1

            attrs[index].value = value

def getPerFaceByType(context, object, zclass):
    zattrs = [obj for obj in zclass.__dict__.keys() if not obj.startswith('__')]
    btype = zclass.__name__.split('_')[1]
    bname = "perFaceBlock{}".format(btype)
    mesh = object.data
    bpy.ops.object.mode_set(mode = 'OBJECT')
    polygons = getPolygonsBySelectedVertices(object)
    indexes = [cn.index for cn in polygons]

    if len(indexes) > 0:
        index = indexes[0]
        for property in zattrs:
            obj = zclass.__dict__[property]
            attrs = mesh.attributes[obj['prop']].data
            getFromAttributes(context, obj, attrs, bname, index)

    bpy.ops.object.mode_set(mode = 'EDIT')

def getPerVertexByType(context, object, zclass):
    zattrs = [obj for obj in zclass.__dict__.keys() if not obj.startswith('__')]
    btype = zclass.__name__.split('_')[1]
    bname = "perVertBlock{}".format(btype)
    mesh = object.data
    bpy.ops.object.mode_set(mode = 'OBJECT')
    vertices = getSelectedVertices(object)
    # log.debug(vertices)
    indexes = [cn.index for cn in vertices]

    if len(indexes) > 0:
        index = indexes[0]
        for property in zattrs:
            obj = zclass.__dict__[property]
            attrs = mesh.attributes[obj['prop']].data
            getFromAttributes(context, obj, attrs, bname, index)

    bpy.ops.object.mode_set(mode = 'EDIT')

def setPerVertexByType(context, object, zclass):
    zattrs = [obj for obj in zclass.__dict__.keys() if not obj.startswith('__')]
    btype = zclass.__name__.split('_')[1]
    bname = "perVertBlock{}".format(btype)
    mesh = object.data

    bpy.ops.object.mode_set(mode = 'OBJECT')
    vertices = getSelectedVertices(object)
    indexes = [cn.index for cn in vertices]

    for index in indexes:
        for property in zattrs:
            obj = zclass.__dict__[property]
            attrs = mesh.attributes[obj['prop']].data
            setFromAttributes(context, obj, attrs, bname, index)

    bpy.ops.object.mode_set(mode = 'EDIT')

def setPerFaceByType(context, object, zclass):
    zattrs = [obj for obj in zclass.__dict__.keys() if not obj.startswith('__')]
    btype = zclass.__name__.split('_')[1]
    bname = "perFaceBlock{}".format(btype)
    mesh = object.data

    bpy.ops.object.mode_set(mode = 'OBJECT')
    polygons = getPolygonsBySelectedVertices(object)
    indexes = [cn.index for cn in polygons]

    for index in indexes:
        for property in zattrs:
            obj = zclass.__dict__[property]
            attrs = mesh.attributes[obj['prop']].data
            setFromAttributes(context, obj, attrs, bname, index)

    bpy.ops.object.mode_set(mode = 'EDIT')

def createCustomAttribute(mesh, values, zclass, zobj):
    # attrs = [obj for obj in zclass.__dict__.keys() if not obj.startswith('__')]
    ctype, btype = zclass.__name__.split('_')
    domain = ''
    if ctype == 'pvb':
        domain = 'POINT'
    elif ctype == 'pfb':
        domain = 'FACE'

    # log.debug(domain)
    # log.debug(zobj['type'])
    if zobj['type'] == fieldType.FLOAT:
        ztype = 'FLOAT'
        mesh.attributes.new(name=zobj['prop'], type=ztype, domain=domain)
        attr = mesh.attributes[zobj['prop']].data
        # log.debug(len(attr))
        # log.debug(len(values))
        for i in range(len(attr)):
            setattr(attr[i], "value", values[i])

    elif zobj['type'] == fieldType.COORD:
        ztype = 'FLOAT_VECTOR'
        mesh.attributes.new(name=zobj['prop'], type=ztype, domain=domain)
        attr = mesh.attributes[zobj['prop']].data
        # log.debug(len(attr))
        # log.debug(len(values))
        for i in range(len(attr)):
            setattr(attr[i], "vector", values[i])

    elif zobj['type'] == fieldType.INT:
        ztype = 'INT'
        mesh.attributes.new(name=zobj['prop'], type=ztype, domain=domain)
        attr = mesh.attributes[zobj['prop']].data
        # log.debug(len(attr))
        # log.debug(len(values))
        for i in range(len(attr)):
            setattr(attr[i], "value", values[i])

    elif zobj['type'] == fieldType.V_FORMAT:
        ztype = 'INT'
        mesh.attributes.new(name=zobj['prop'], type=ztype, domain=domain)
        attr = mesh.attributes[zobj['prop']].data
        # log.debug(len(attr))
        # log.debug(len(values))
        for i in range(len(attr)):
            setattr(attr[i], "value", values[i])