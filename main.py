# This is a sample Python script.

# Press Ctrl+F5 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os

import prettytable as pt
from shapely.geometry import Point
from shapely.geometry import LineString

import Structure
import math

dataPath = "./scheme/枢纽网络构建/最小的实验网/data/"
connFile = dataPath + "Tconn.txt"  # [0 4 1 2 3 4]
contFile = dataPath + "Tcont.txt"  # [0 5}
coorFile = dataPath + "Tcoor.txt"  # [0 -45.454545454545503 107.438016528925601]
geomFile = dataPath + "Tgeom.txt"  # [0 1 2 21 159.38 0 2]

linkToLinkFile: str = dataPath + "Tlink-topodlink.txt"  # [0 1 1 1]
nodeTonodeFile = dataPath + "Tnode-toponode.txt"  # [0 0 0]
topodlinkFile = dataPath + "Ttopodlink.txt"  # [0 2 1 0]
toponodeFile = dataPath + "Ttoponode.txt"  # [0 -45.454545454545503 107.438016528925601]

radius = 0.001

MAXNODEID = 0
MAXTOPONODEID = 0
MAXSECTIONID = 0
MAXTOPODLINKID = 0


def readFromFile(fileName: str):
    content = []  # [[], [],]
    with open(fileName, 'r') as f:
        for line in f:
            lineList = line.split()
            if len(lineList) == 1:
                continue

            line = line.replace("\n", "")
            line = line.strip()
            lineList = line.split()
            content.append(lineList)
    return content


def buildData():
    connContent = readFromFile(connFile)
    contContent = readFromFile(contFile)
    coorContent = readFromFile(coorFile)
    geomContent = readFromFile(geomFile)

    linkToLinkContent = readFromFile(linkToLinkFile)
    nodeTonodeContent = readFromFile(nodeTonodeFile)
    topodlinkContent = readFromFile(topodlinkFile)
    toponodeContent = readFromFile(toponodeFile)

    topoMap = {}  # topoid  ---> TopoNode
    topoDLinkMap = {}  # topodlink.txt 文件信息 路段的拓扑点集合
    nodeMap = {}  # 节点id  ---> Node 对象
    sectionMap = {}  # 节点id  ---> Node 对象

    # 1. 读取 topoNode
    for element in toponodeContent:
        _id = int(element[0])
        xp = float(element[1])
        yp = float(element[2])
        topo = Structure.TopoNode(_id, xp, yp)
        topoMap[_id] = topo
        global MAXTOPONODEID
        MAXTOPONODEID = max(MAXTOPONODEID, _id)

    for i in range(len(connContent)):
        # conn
        _id = int(connContent[i][0])
        neighList = connContent[i][2:]

        global MAXNODEID
        MAXNODEID = max(MAXNODEID, _id)

        # 类型转换
        newneighList = []
        for ele in neighList:
            ele = int(ele)
            newneighList.append(ele)

        # cont
        _type = int(contContent[i][1])

        # node-toponode
        nodeID = int(nodeTonodeContent[i][0])
        topoID = int(nodeTonodeContent[i][2])

        # 节点坐标
        if _id == nodeID:  # 文件正常情况下，一定会相等
            topoNodeObj = topoMap.get(topoID)
            point = Structure.Node(_id, _type, topoNodeObj, newneighList)
            nodeMap[_id] = point

    for i in range(len(geomContent)):
        # geom
        origin = int(geomContent[i][0])
        dest = int(geomContent[i][1])
        _type = int(geomContent[i][2])
        grade = int(geomContent[i][3])
        length = float(geomContent[i][4])
        speed = int(geomContent[i][5])  # 速度 用不到此数据，生成新文件时还原该数据
        num = int(geomContent[i][6])  # 车道数 用不到此数据，生成新文件时还原该数据

        # topodlink
        for element in topodlinkContent:
            _topoLinkID = int(element[0])
            topoDLinkList = []
            for e in element[2:]:
                topoDLinkList.append(int(e))
            topoLink = Structure.TopoLink(_topoLinkID, topoDLinkList)
            topoDLinkMap[_topoLinkID] = topoLink

            global MAXTOPODLINKID
            MAXTOPODLINKID = max(MAXTOPODLINKID, _topoLinkID)

        # link-topodlink
        secID = int(linkToLinkContent[i][2])
        topoLinkID = int(linkToLinkContent[i][3])

        global MAXSECTIONID
        MAXSECTIONID = max(MAXSECTIONID, secID)

        # 转换成 Node 对象
        originPt = nodeMap[origin]
        destPt = nodeMap[dest]

        sec = Structure.Section(secID, _type, grade, originPt, destPt, length, speed, num, topoDLinkMap[topoLinkID])
        sectionMap[secID] = sec

    TB = pt.PrettyTable()
    TB.title = "TopoNode Info"
    TB.field_names = ["id", "xp", "yp"]
    for item in topoMap.items():
        key = item[0]
        value = item[1]
        TB.add_row([key, value.xp, value.yp])
    print(TB)

    TB = pt.PrettyTable()
    TB.title = "Node Info"
    TB.field_names = ["id", "type", "TopoNode ID", "neighIDList"]
    for item in nodeMap.items():
        key = item[0]
        value = item[1]
        TB.add_row([key, value.type, value.topo.id, value.neighIDList])
    print(TB)

    TB = pt.PrettyTable()
    TB.title = "Section Info"
    TB.field_names = ["id", "type", "grade", "origin", "destination", "length", "speed", "num", "topoDLink ID",
                      "topoDLink"]
    for item in sectionMap.items():
        key = item[0]
        value = item[1]
        TB.add_row([key, value.type, value.grade, value.origin.id, value.dest.id, value.length, value.speed, value.num,
                    value.topoDLink.id, value.topoDLink.topoLinkList])
    print(TB)

    # 输出最大ID值
    TB = pt.PrettyTable()
    TB.title = "MAX ID Info"
    TB.field_names = ["MAXNODEID", "MAXTOPONODEID", "MAXSECTIONID", "MAXTOPODLINKID"]
    TB.add_row([MAXNODEID, MAXTOPONODEID, MAXSECTIONID, MAXTOPODLINKID])
    print(TB)
    return topoMap, nodeMap, sectionMap


def getSectionLen(originType, destType) -> float:
    if not (1 <= originType <= 4):
        return 0.0
    elif not (1 <= destType <= 4):
        return 0.0

    _len = ((originType - 1.0) * 4.0 + destType) * 0.001 + 0.900
    return _len


def queryOppoSec(originId, destId, sectionMap: dict) -> Structure.Section:
    for value in sectionMap.values():
        if value.origin.id == destId and value.dest.id == originId:
            # print("oppo sec: ({},{})--->{}".format(originId, destId, value.id))
            return value

    return None


def operateNode(node: Structure.Node, sec: Structure.Section) -> Structure.Node:
    # 2. 拆点
    # 2.1 计算拆分拓扑点坐标
    x1, y1 = sec.origin.topo.xp, sec.origin.topo.yp
    x2, y2 = sec.dest.topo.xp, sec.dest.topo.yp

    dd = pow(x1 - x2, 2) + pow(y1 - y2, 2)
    _len = math.sqrt(dd)
    # print("Length:", _len)
    global radius
    ratio = radius / _len

    # 2.2 判断起终点
    if node == sec.dest:
        # print("Dest", sec.id)
        ratio = 1.0 - ratio

    # 2.3 计算拆点坐标
    x = (x2 - x1) * ratio + x1
    y = (y2 - y1) * ratio + y1
    print("Coor:", x, y)

    """
    新增操作：
        1. 拓扑点:   id x, y
        2. 节点:    id type=8 topoNode neighIDList
        3. 路段:    id type=2 grade=21 origin dest len speed num topoLink
        4. topoLink 
    """
    # 3 新建节点信息
    # 3.1 新建拓扑点
    global MAXTOPONODEID
    MAXTOPONODEID += 1
    topo = Structure.TopoNode(MAXTOPONODEID, x, y)

    # 3.2 新建节点
    global MAXNODEID
    MAXNODEID += 1
    newNodeType = 8
    if node == sec.dest:
        neighIDList = [sec.origin.id]
    else:
        neighIDList = [sec.dest.id]

    newNode = Structure.Node(MAXNODEID, newNodeType, topo, neighIDList)
    # newNodeList.append(newNode)

    # 3.3 更新路段几何信息 (起终点、拓扑点集合)
    if node == sec.origin:
        sec.origin = newNode
        sec.topoDLink.topoLinkList[0] = MAXTOPONODEID
    elif node == sec.dest:
        sec.dest = newNode
        sec.topoDLink.topoLinkList[-1] = MAXTOPONODEID

    return newNode


def splitNode(node, sectionMap):
    # 1.找出连接的路段
    print("split node: ", node.id)
    newNodeList = []
    eliminateSecList = []
    for sec in sectionMap.values():
        if sec.id in eliminateSecList:
            continue

        preOriginId = sec.origin.id
        preDestId = sec.dest.id
        if node.id != sec.origin.id and node.id != sec.dest.id:
            continue

        newNode = operateNode(node, sec)
        newNodeList.append(newNode)

        # 查找对向路段
        oppoSec = queryOppoSec(preOriginId, preDestId, sectionMap)
        if oppoSec is None:
            continue

        # 更新对向路段几何信息 (起终点、拓扑点集合)
        if node.id == preOriginId:
            oppoSec.origin = newNode
            oppoSec.topoDLink.topoLinkList[0] = MAXTOPONODEID
        elif node.id == preDestId:
            oppoSec.dest = newNode
            oppoSec.topoDLink.topoLinkList[-1] = MAXTOPONODEID

        # 排除已处理路段
        eliminateSecList.append(sec.id)
        eliminateSecList.append(oppoSec.id)

    return newNodeList


def splitNetwork(topoMap, nodeMap, sectionMap):
    # 1. 查找转换节点
    newAllNodeList = []
    for node in nodeMap.values():

        # 5 - 火车站 6 - 码头 7 - 机场 8 - 综合交通枢纽
        if not (5 <= node.type <= 8):  # 不满足条件进行下一次循环
            continue

        # 2.对筛选节点进行拆分
        newOnceNodeList = splitNode(node, sectionMap)
        newAllNodeList.append(newOnceNodeList)

        # 3. 新建路段
        print("********************")
        pList = [node.id for node in newOnceNodeList]
        print("new Node id: ", pList)

        for i in range(0, len(newOnceNodeList)):
            for j in range(0, len(newOnceNodeList)):
                if newOnceNodeList[i] is newOnceNodeList[j]:
                    continue

                # 更新新建节点邻接目录表
                newOnceNodeList[i].neighIDList.append(newOnceNodeList[j].id)

                # 新建路段信息
                global MAXSECTIONID
                MAXSECTIONID += 1
                newType = 2
                newGrade = 21
                _len = getSectionLen(newOnceNodeList[i].type, newOnceNodeList[j].type)

                global MAXTOPODLINKID
                MAXTOPODLINKID += 1
                topoLinkList = [newOnceNodeList[i].topo.id, newOnceNodeList[j].topo.id]
                topoLink = Structure.TopoLink(MAXTOPODLINKID, topoLinkList)
                newSec = Structure.Section(MAXSECTIONID, newType, newGrade, newOnceNodeList[i], newOnceNodeList[j],
                                           _len, 0, 2,
                                           topoLink)

                sectionMap[newSec.id] = newSec

    for onceList in newAllNodeList:
        for node in onceList:
            topoMap[node.topo.id] = node.topo
            nodeMap[node.id] = node


def writeToFile(fileName: str, content: list):
    with open(fileName, "a") as file:
        for line in content:
            file.writelines((line + "\n"))


def getFileContent(topoMap, nodeMap, sectionMap):
    count = len(nodeMap.keys())
    connWriteContent = [str(count)]
    contWriteContent = []
    nodeTonodeWriteContent = []
    for node in nodeMap.values():
        _id = str(node.id)
        _size = str(len(node.neighIDList))
        idList = [str(__id) for __id in node.neighIDList]
        neighIDStr = " ".join(idList)

        # 1. conn
        line = " ".join([_id, _size, neighIDStr])
        connWriteContent.append(line)

        # 2. cont
        _type = str(node.type)
        line = " ".join([_id, _type])
        contWriteContent.append(line)

        # 6. node-toponode
        topid = str(node.topo.id)
        line = f"{_id} {topid} {topid}"
        nodeTonodeWriteContent.append(line)

    print(connWriteContent)

    geomWriteContent = []
    topoDLinkWriteContent = []
    linkToLinkWriteContent = []
    for sec in sectionMap.values():
        _id = str(sec.id)
        _type = str(sec.type)
        grade = str(sec.grade)
        origin = str(sec.origin.id)
        dest = str(sec.dest.id)
        length = str(sec.length)
        speed = str(sec.speed)
        num = str(sec.num)

        # 3. geom
        line = f"{origin} {dest} {_type} {grade} {length} {speed} {num}"
        geomWriteContent.append(line)

        # 7. topodlink
        _topoLinkID = sec.topoDLink.id
        count = len(sec.topoDLink.topoLinkList)
        topoDLinkStr = " ".join(str(tid) for tid in sec.topoDLink.topoLinkList)
        line = f"{_topoLinkID} {count} {topoDLinkStr}"
        topoDLinkWriteContent.append(line)

        # 8. link-topodlink
        line = f"{origin} {dest} {_id} {_topoLinkID}"
        linkToLinkWriteContent.append(line)

    # 4. coor

    # 5. topoNode
    toponodeWriteContent = []
    for topoNode in topoMap.values():
        _id = str(topoNode.id)
        xp = str(topoNode.xp)
        yp = str(topoNode.yp)
        line = f"{_id} {xp} {yp}"
        toponodeWriteContent.append(line)

    return [connWriteContent, contWriteContent, nodeTonodeWriteContent, geomWriteContent, topoDLinkWriteContent,
            linkToLinkWriteContent, toponodeWriteContent]


def outPutResult(topoMap, nodeMap, sectionMap):
    allContentList = getFileContent(topoMap, nodeMap, sectionMap)
    # 写入文件 [connWriteContent, contWriteContent, nodeTonodeWriteContent, geomWriteContent, topoDLinkWriteContent,
    # linkToLinkWriteContent, toponodeWriteContent]

    _dir = "D:/Data/output/"
    fileName = ["Tconn.txt", "Tcont.txt", "Tnode-toponode.txt", "Tgeom.txt", "Ttopodlink.txt", "Tlink-topodlink.txt",
                "Ttoponode.txt"]
    i = 0
    for fileContent in allContentList:
        filePath = _dir + fileName[i]
        print("******************************")
        print(fileName[i])
        print(fileContent)
        writeToFile(filePath, fileContent)
        i += 1


def process():
    # 1.从文件构建结构体数据
    topoMap, nodeMap, sectionMap = buildData()

    # 2.拆网
    splitNetwork(topoMap, nodeMap, sectionMap)

    # 3.写入文件
    outPutResult(topoMap, nodeMap, sectionMap)


def main():
    process()


main()
